# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
##cython: profile=True

from cython_gsl cimport *
from libc.stdlib cimport malloc, free
import cython
from libc.stdio cimport printf
import collections
from cython cimport parallel
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
cimport numpy as np
import numpy as np


'''
Logical structure of ode creation:

1) parsing starts at the highest level construct that is passed from the Python
main loop: an EvoSystem instance. This will be passed to the constructor of the
SYSTEM extension type.

2) every substructure has (in principle) its own matching cython extension type,
that will be used to further construct the ode system, by deconstructing the
substructure instance (eg Population) into its sub-components, via matching
cython extenion types.

3) A caveat of this approach is that the cython extension types cannot have
containers holding extension types as attributes: because extension types are in
essence c-structs, whose size must be known at compile time, variable length
arrays of unknown size are not allowed.

4) To circumvent the caveat, the extension types will be used to allocate memory
for and instantiate accompanying c-structs that will hold the actual data needed
for the ode integration.

5) A master equation will eventually be passed to the integrator and loop over
all the data in structs, updating variables of the system.
'''

cdef void convert(double vars[], double derivs[], enzyme_str * enzyme,
                  double cell_volume, double volume_limitation) nogil:
    '''
    Calculate change of reactants and products as a function of an enzymatic reaction.

    For the enzyme, calculates the reaction rates of all sub-reactions
    catalysed by the enzyme and updates reactant and product concentrations. A
    constraint on the enzyme efficiency is taken into account that depends on
    the total concentration of enzymes within the cell volume (effect of
    crowding).

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    enzyme : enzyme structure
    cell_volume : double
        internal cell volume
    volume_limitation : double
        scaling factor of the reaction rate
    '''
    cdef int i, j
    cdef double rate, nume, denom
    cdef enzyme_params_str * eparams
    cdef double enzyme_conc = vars[enzyme.variable]
    cdef reactant_str * reac
    cdef product_str * prod
    cdef double total_rate = 0.
    cdef double V_max = enzyme.v_max * enzyme_conc

    # Calculate the rates of all sub-reactions of the enzyme
    for i in range(enzyme.nr_equations):
        eparams = &enzyme.params[i]
        nume = enzyme.v_max * enzyme_conc
        denom = 1.
        for j in range(eparams.nr_reactants):
            reac = &eparams.reactants[j]
            nume *=  pow(vars[reac.var], reac.stoi)
            denom *= pow((vars[reac.var] + reac.k_bind), reac.stoi)

        rate = (nume / denom )
        if volume_limitation > 0.0:
            rate *= volume_limitation

        total_rate += rate
        enzyme.params[i].sub_reac_rate = rate

    cdef double rate_scaling = 1.
    # Calculate rate scaling parameter if the total reaction rate exceeds
    # the maximum reaction rate for the enzyme.
    if total_rate > V_max:
        rate_scaling =   V_max / total_rate

    # Update all reactant and product derivatives involved in the reaction.
    for i in range(enzyme.nr_equations):
        eparams = &enzyme.params[i]
        for j in range(eparams.nr_reactants):
            reac = &eparams.reactants[j]
            derivs[reac.var] -= reac.stoi * (eparams.sub_reac_rate * rate_scaling)
        for j in range(eparams.nr_products):
            prod = &eparams.products[j]
            derivs[prod.var] += prod.stoi * (eparams.sub_reac_rate * rate_scaling)

cdef void converting(double vars[],  double derivs[], cell_str * cell, double volume_occupancy_constant  = 0.0) nogil:
    '''
    Calculate change of reactants and products as a function of all enzymatic reactions.

    Calculates the reaction rates and updates reactant and product
    concentrations. A constraint on the enzyme efficiency is taken into account
    that depends on the total concentration of enzymes within the cell volume
    (effect of crowding).

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    volume_occupancy_constant : double
        parameter determining cell crowding
    '''
    cdef int i
    cdef double total_enzyme_concentration = 0.0

    for i in range(cell.genome.nr_enzymes):
        total_enzyme_concentration += vars[cell.genome.enzymes[i].variable]

    cdef double volume_limitation = 0.0
    if volume_occupancy_constant > 0.0:
        volume_limitation = pow(volume_occupancy_constant,2)/(pow(total_enzyme_concentration,2)+pow(volume_occupancy_constant,2))

    for i in range(cell.genome.nr_enzymes):
        convert(vars, derivs, cell.genome.enzymes[i] , vars[cell.cell_size_s.var], volume_limitation)

cdef double membrane_area(double volume, double N=0.7) nogil:
    '''
    Calculates a membrane area, based on the cell volume

    Parameters
    ----------
    volume : double
        cell volume
    N : double
        scaling constant to approximate surface area

    Returns
    -------
    membrane area : double
    '''
    return pow(volume, N)

cdef void transport(double vars[], double derivs[], pump_str * pump,
                  double volume_out, double cell_volume,
                  double membrane_limitation) nogil:
    '''
    Calculate change of internal and external substrate as a function of an
    transport reaction.

    For the pump, calculates the reaction rates of all sub-reactions catalysed
    by the pump and updates internal and external substrate concentrations. A
    constraint on the pump efficiency is taken into account that depends on the
    total concentration of enzymes on the cell surface (effect of crowding).

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    pump : pump_str
        pump structure
    volume_out : double
        external volume
    cell_volume : double
        internal cell volume
    membrane_limitation : double
        scaling factor of the reaction rate
    '''
    cdef double rate, rate_scaling
    cdef int sub_in, sub_out, en
    cdef double pump_conc = vars[pump.variable]
    cdef double direction = pump.direction
    cdef pump_params_str * pparams
    cdef double total_rate = 0.
    cdef double V_max = pump.v_max * pump_conc
    for i in range(pump.nr_equations):
        pparams = &pump.params[i]
        sub_in = pparams.substrate_in
        sub_out = pparams.substrate_out
        en = pparams.energy_mol
        if direction > 0.:
            rate = (vars[sub_out] * vars[en] * pump.v_max * pump_conc
                    / ((vars[sub_out] + pparams.k_sub) * (vars[en] + pparams.k_ene)))
        else:
            rate = (vars[sub_in] * vars[en] * pump.v_max * pump_conc
                    / ((vars[sub_in] + pparams.k_sub) * (vars[en] + pparams.k_ene)))
        pump.params[i].sub_reac_rate = rate
        total_rate+=rate

    cdef double sub_reaction_rate_scaling = 1.
    if total_rate > V_max:
        sub_reaction_rate_scaling =  V_max / total_rate
    rate_scaling = sub_reaction_rate_scaling * membrane_limitation
    for i in range(pump.nr_equations):
        pparams = &pump.params[i]
        sub_in = pparams.substrate_in
        sub_out = pparams.substrate_out
        en = pparams.energy_mol
        derivs[sub_out] -= pparams.sub_stoi * direction * (pparams.sub_reac_rate * rate_scaling) / volume_out
        derivs[sub_in] += pparams.sub_stoi * direction * (pparams.sub_reac_rate * rate_scaling)
        derivs[en] -= pparams.ene_cost * (pparams.sub_reac_rate * rate_scaling)

cdef void transporting(double vars[],  double derivs[], cell_str * cell, double env_volume,
                       double membrane_occupancy_constant = .1) nogil:
    '''
    Calculate change of internal and external substrates as a function of all
    transport reactions.

    Calculates the reaction rates and updates internal and external substrate
    concentrations. A constraint on the pump efficiency is taken into account
    that depends on the total concentration of pumps on the cell surface
    (effect of crowding).

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    env_volume : double
        exteral volume
    membrane_occupancy_constant : double
        parameter determining membrane crowding
    '''
    cdef int i
    cdef double area, volume, av_ratio
    cdef double membrane_limitation = 1.
    cdef double total_pump_concentration = 0.

    if membrane_occupancy_constant > 0.:
        volume = vars[cell.cell_size_s.var]
        area = membrane_area(volume)
        av_ratio = area / volume
        for i in range(cell.genome.nr_pumps):
            total_pump_concentration += vars[cell.genome.pumps[i].variable]
        membrane_limitation = av_ratio / ( membrane_occupancy_constant * total_pump_concentration + av_ratio )
    for i in range(cell.genome.nr_pumps):
        transport(vars, derivs, cell.genome.pumps[i] , env_volume, vars[cell.cell_size_s.var], membrane_limitation)

cdef void diffusing(double vars[], double derivs[], cell_str * cell, double env_volume) nogil:
    '''
    Diffusion of small molecules over the cell membrane.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    env_volume : double
        exteral volume
    '''

    cdef int i
    cdef int mol_int_var, mol_ext_var
    cdef double rate, cell_volume, cell_area
    cdef mol_str * mol_s
    cell_volume = vars[cell.cell_size_s.var]
    cell_area = membrane_area(cell_volume)
    for i in range(cell.nr_small_mols):
        mol_s = cell.small_mols[i]
        mol_int_var = mol_s.variable
        mol_ext_var = mol_s.diff_external_var
        rate = (vars[mol_int_var] - vars[mol_ext_var]) *  mol_s.diff_const * cell_area
        derivs[mol_int_var] -= rate / cell_volume
        derivs[mol_ext_var] += rate / env_volume

cdef void degradation_and_dilution(double vars[], double derivs[], cell_str * cell) nogil:
    '''
    Concentration change due to degradation and cell volume change.

    Molecules degrade with a fixed rate per molecule. In addition, molecule
    concentrations dilute due to cell volume increase (and shrinking) as
    determined by the cell growth_rate.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    '''
    cdef int i
    cdef double rate
    cdef mol_str * mol_s
    cdef pump_str * pump_s
    cdef enzyme_str * enzyme_s
    cdef tf_str * tf_s
    cdef double mu = cell.cell_size_s.growth_rate - cell.cell_size_s.shrink_rate
    for i in range(cell.nr_small_mols):
        mol_s = cell.small_mols[i]
        rate = vars[mol_s.variable] * ( mol_s.degr_const + mu)
        derivs[mol_s.variable] -= rate
    for i in range(cell.genome.nr_pumps):
        pump_s = cell.genome.pumps[i]
        rate = vars[pump_s.variable] * ( pump_s.degr_const + mu )
        derivs[pump_s.variable] -= rate
    for i in range(cell.genome.nr_enzymes):
        enzyme_s = cell.genome.enzymes[i]
        rate = vars[enzyme_s.variable] * ( enzyme_s.degr_const + mu )
        derivs[enzyme_s.variable] -= rate
    for i in range(cell.genome.nr_tfs):
        tf_s = cell.genome.tfs[i]
        rate = vars[tf_s.variable] * ( tf_s.degr_const + mu )
        derivs[tf_s.variable] -= rate
    derivs[cell.production_s.variable] -= vars[cell.production_s.variable] * (cell.production_s.degr_const + mu)

cdef double tf_states(double vars[], tf_str * tf) nogil:
    '''
    Calculate the fraction of the TF that remains unbound by any of its ligands.

    Calculate as:
    p_unbound = Product<1,i>( (1 - p_bound_ligand_i) ) for i in {binding ligands}

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    tf : tf_str
        the TF structure

    Returns
    -------
    fraction of TF in ligand-free state.
    '''
    cdef double p_unbound = 1.
    cdef double p_bound, ligand_conc, ligand_coop, k_bind
    cdef int i
    for i in range(tf.nr_ligands):
        ligand_conc = vars[tf.ligands[i].variable]
        ligand_coop = tf.ligands[i].coop
        ligand_k = tf.ligands[i].k_bind
        p_bound = ( pow(ligand_conc, ligand_coop) /
                    (pow(ligand_k, ligand_coop) + pow(ligand_conc, ligand_coop) ))
        p_unbound *= (1 - p_bound)
    return p_unbound

cdef void tfs_states(double vars[], tf_str ** tfs, int nr_tfs) nogil:
    '''
    Calculate the fractions of TFs that remain unbound by any of their ligands.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    tfs : array of tf_str
        the list of TF structures
    nr_tfs : int
        number of TFs

    Returns
    -------
    fraction of TF in ligand-free state.
    '''
    cdef int i
    cdef double eff_apo
    for i in range(nr_tfs):
        tfs[i].w_tf_apo = tf_states(vars, tfs[i])

cdef double transcription_rate(double vars[], reg_seq_str * reg_seq) nogil:
    '''
    Calculate the rate of transcription for a gene.

    The function sums the regulatory effects of tfs bound to the gene's operator
    by multiplying the occupancy rate of the tf in its ligand bound and ligand
    free state with the binding_score and intrinsic binding affinity of the tf
    for its recognized operator and the respective regulatory effects: eff_bound
    and eff_apo. The fractions of the tf that are in apo and bound state have
    been determined by the tfs_states function. Binding of the tfs is a function
    of their concentration and the binding_score and affinity for the operator.

    from Neyfakh et al. (2006)

    V = [TF in a particular form] × K_b /binding polynomial

    where binding polynomial is 1 plus the sum of [TF in a particular form] ×
    K_b terms for all TFs which can bind the operator

    Reg = Σ V_i × E_i

    where V i is the fraction of time the operator is in a particular state (i.
    e., unbound or bound by a particular TF, in either apo or ligand-bound form;
    Σ V_i = 1), and E_i is the effect of the corresponding state on the rate of
    transcrip- tion (i. e., 1 or either EffApo or EffBound, for the
    corresponding TFs).

    N.B. we use k_bind_op = 1/ K_b to mirror semantics of K terms in enzymatic
    rate reactions, i.e. lower K terms mean saturation at lower TF
    concentrations

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    reg_seq : reg_seq_str
        regulatory region structure
    '''

    cdef int i
    cdef double tf_conc, fract_apo, binding_rate
    cdef double total_frac_bound_nume = 0.
    cdef double reg = 0.
    cdef binding_tf_str * binding_tf
    # Sum all binding factors (building up numerator)
    for i in range(reg_seq.nr_binding_tfs):
        binding_tf = &reg_seq.binding_tfs[i]
        tf_conc = vars[binding_tf.tf.variable]
        binding_rate = pow((tf_conc * binding_tf.score) / binding_tf.tf.k_bind_op, binding_tf.tf.coop)
        total_frac_bound_nume += binding_rate
    cdef double total_frac_bound_denom = 1 + total_frac_bound_nume
    # Calculate the regulatory effects (building up denominator)
    for i in range(reg_seq.nr_binding_tfs):
        binding_tf = &reg_seq.binding_tfs[i]
        tf_conc = vars[binding_tf.tf.variable]
        fract_apo = binding_tf.tf.w_tf_apo
        # Rate of binding of tf to operator:
        binding_rate = pow((tf_conc * binding_tf.score) / binding_tf.tf.k_bind_op, binding_tf.tf.coop)
        # Regulation effect of ligand_free tf-form:
        reg += fract_apo * binding_tf.tf.eff_apo *  binding_rate / total_frac_bound_denom
        # Regulation effect of ligand bound tf-form:
        reg += (1 - fract_apo) * binding_tf.tf.eff_bound * binding_rate / total_frac_bound_denom
    # Expression effect of unbound operator ( is scaled to 1):
    reg += 1 - (total_frac_bound_nume/ total_frac_bound_denom)

    # ---uncomment to print regulatory effects---
    # frac_reg = (total_frac_bound_nume/ total_frac_bound_denom)
    # if reg_seq.nr_binding_tfs > 0 and frac_reg > 0.5:
    #     frac_bound = bound_tot/ reg_seq.nr_binding_tfs
    #     if frac_bound > 0.1:
    #         printf('fract_tf_reg: %f , fract_bound: %f reg: %f\n', frac_reg, frac_bound, reg)
    return reg * reg_seq.pr_str

cdef void transcription(double vars[], double derivs[], cell_str * cell,
                        double product_scaling, double scaling_power) nogil:
    '''
    Transcription of genes.

    Transcription (+translation) of genes is a function of the regulatory
    effects, the gene multiplicity and, depending on parameters, the available
    product and/or energy concentration in the cell. Regulatory effects are the
    sum of binding activities of all binding TFs in either ligand bound or
    ligand free states and the remaining basal transcription rate (fraction of
    time that the regulatory region is not bound by TF).

    If the production cost > 0 then the production constraint function is a
    saturating function of product concentration in the cell, limiting the rate
    of transcription. Transcription rate decreases when product concentration is
    low. There is a (small) product cost to transcription.

    If the energy cost > 0 then the energy constraint function is a saturation
    function of energy concentration inside the cell, limiting the rate of
    transcription. Transcription rate decreases  when energy concentration is
    low. There is a (small) energy cost to transcription.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    product_scaling : double
        scaling constant for effective product
    scaling_power : double
        product scaling power constant
    '''
    cdef int i,j, ene_var
    cdef double rate, ene_fract
    cdef double ene_conc_tot = 0.
    cdef pump_str * pump_s
    cdef enzyme_str * enzyme_s
    cdef tf_str * tf_s
    cdef double product = vars[cell.production_s.variable]
    cdef double scaled_product = 0.
    cdef double base_rate = 1.
    cdef bint prod_cost = False
    cdef bint energy_cost = False
    if cell.trans_cost > 0:
        prod_cost = True
    if cell.ene_trans_cost > 0:
        energy_cost = True
    if prod_cost:
        if product_scaling == 0:
            product_scaling = product
        if product > 0:
            scaled_product = pow(product, scaling_power) / ( pow(product, scaling_power) +
                                                                   pow(product_scaling, scaling_power))
        base_rate *= scaled_product
    if energy_cost:
        for j in range(cell.nr_energy_mols):
            ene_var = cell.energy_mols[j]
            ene_conc_tot += vars[ene_var]
        energy_constraint = ene_conc_tot / (ene_conc_tot + cell.k_ene_trans)
        base_rate *= energy_constraint
    for i in range(cell.genome.nr_pumps):
        pump_s = cell.genome.pumps[i]
        if pump_s.gene_multiplicity == 0:
            continue
        rate = base_rate * pump_s.gene_multiplicity * transcription_rate(vars, pump_s.reg_seq)
        if rate <= 0.:
            continue
        derivs[pump_s.variable] += rate
        if prod_cost:
            derivs[cell.production_s.variable] -= cell.trans_cost * rate * vars[cell.production_s.variable]
        if energy_cost:
            for j in range(cell.nr_energy_mols):
                ene_var = cell.energy_mols[j]
                ene_conc = vars[ene_var]
                derivs[ene_var] -= cell.ene_trans_cost * rate * ene_conc / ene_conc_tot

    for i in range(cell.genome.nr_enzymes):
        enzyme_s = cell.genome.enzymes[i]
        if enzyme_s.gene_multiplicity == 0:
            continue
        rate = base_rate * enzyme_s.gene_multiplicity * transcription_rate(vars, enzyme_s.reg_seq)
        if rate <= 0.:
            continue
        derivs[enzyme_s.variable] += rate
        if prod_cost:
            derivs[cell.production_s.variable] -= cell.trans_cost * rate * vars[cell.production_s.variable]
        if energy_cost:
            for j in range(cell.nr_energy_mols):
                ene_var = cell.energy_mols[j]
                ene_conc = vars[ene_var]
                derivs[ene_var] -= cell.ene_trans_cost * rate * ene_conc / ene_conc_tot

    for i in range(cell.genome.nr_tfs):
        tf_s = cell.genome.tfs[i]
        if tf_s.gene_multiplicity == 0:
            continue
        rate = base_rate * tf_s.gene_multiplicity * transcription_rate(vars, tf_s.reg_seq)
        if rate <= 0.:
            continue
        derivs[tf_s.variable] += rate
        if prod_cost:
            derivs[cell.production_s.variable] -= cell.trans_cost * rate * vars[cell.production_s.variable]
        if energy_cost:
            for j in range(cell.nr_energy_mols):
                ene_var = cell.energy_mols[j]
                ene_conc = vars[ene_var]
                derivs[ene_var] -= cell.ene_trans_cost * rate * ene_conc / ene_conc_tot

cdef void production(double vars[], double derivs[], cell_str * cell) nogil:
    '''
    Calculate product generation from building blocks.

    Building blocks are consumed to generate product. If a positive energy
    parameter value is chosen, energy is consumed in addition.

    If 'homeostatic building block' parameter > 0, the rate of production will
    be scaled with the absolute distances of building block concentrations to
    the total average building block concentration, such that larger deviations
    from the average result in a lower net production rate.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    '''

    cdef int i, ene_var
    cdef production_str * production_s = &cell.production_s
    cdef building_block_str * block_s
    cdef double ene_conc = 0.
    cdef double rate = production_s.v_max
    cdef double bb_conc, bb_avrg
    cdef double abs_conc_diff = 0
    cdef double tot_conc = 0

    if production_s.energy:
        for i in range(cell.nr_energy_mols):
            ene_var = cell.energy_mols[i]
            ene_conc += vars[ene_var]
        rate *= ene_conc

    for i in range(production_s.nr_building_blocks):
        block_s = production_s.building_blocks[i]
        tot_conc += vars[block_s.var]
        rate *= pow(vars[block_s.var], block_s.stoi)

    bb_avrg = tot_conc / <double>production_s.nr_building_blocks
    for i in range(production_s.nr_building_blocks):
        block_s = production_s.building_blocks[i]
        abs_conc_diff += fabs(bb_avrg - vars[block_s.var])
    if bb_avrg > 1e-30:
        rate = rate / (1 + abs_conc_diff * cell.h_homeostatic_bb/ bb_avrg)
    for i in range(production_s.nr_building_blocks):
        block_s = production_s.building_blocks[i]
        derivs[block_s.var] -= (rate * block_s.stoi)

    if production_s.energy:
        for i in range(cell.nr_energy_mols):
            ene_var = cell.energy_mols[i]
            derivs[ene_var] -= rate * vars[ene_var]

    cell.production_s.pos_production = rate
    derivs[production_s.variable] += rate

cdef void calc_growth_rate(double vars[], cell_str * cell,
                           double product_scaling, double scaling_power) nogil:
    '''
    Calculate the growth (and shrink) rate of a cell.

    Growth depends on available product and the cell volume, whereas shrinking
    is an intrinsic process that is only proportional to cell volume. The
    production rate is scaled by a saturating function of the product
    concentration, and the cell volume, such that maximum growth rate 'v_max'
    will only be achieved in the limit of saturating product concentration and a
    very small cell volume relative to the cell's 'max_size'. Rates are stored
    in the cell_str struct for subsequent use in the 'cell_growth' function.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    product_scaling : double
        measure of relative production in the population to scale this cells
        growth rate
    scaling_power : double
        scaling constant for production scaling
    '''
    cdef double production = vars[cell.production_s.variable]
    cdef double V = vars[cell.cell_size_s.var]
    cdef double scaled_production = 0.
    if product_scaling == 0:
        product_scaling = production
    if production > 0:
        scaled_production = pow(production, scaling_power) / ( pow(production, scaling_power) +
                                                               pow(product_scaling, scaling_power))
    cdef double v_max =  cell.cell_size_s.growth_const * scaled_production
    cell.cell_size_s.growth_rate = v_max * V * ( 1. - V / cell.cell_size_s.max_size )
    cell.cell_size_s.shrink_rate = V * cell.cell_size_s.shrink_const

cdef void cell_growth(double vars[], double derivs[], cell_str * cell) nogil:
    '''
    Calculate cell volume change by growth and shrinking.

    Growth is proportional to the Production (Prod), the cell Volume and the
    distance of Volume to max-cell-Volume:

    growth_rate = growth_const * ( Prod / ( Prod + prod_scaling) ) * V * ( 1 - V/ max_V)

    dV/dt = growth_rate - shrink_rate
    dProd/dt = - cost * growth_rate * Prod

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    '''
    cdef cell_size_str * cell_size_s = &cell.cell_size_s
    derivs[cell_size_s.var] += cell_size_s.growth_rate - cell_size_s.shrink_rate
    derivs[cell.production_s.variable] -= ( cell_size_s.growth_cost *
                                            cell_size_s.growth_rate *
                                            vars[cell.production_s.variable] )

cdef void toxicity(double vars[], double derivs[], cell_str * cell) nogil:
    '''
    Calculate change in toxic effect on cell due to toxic molecule concentrations.

    The toxic effect of a small molecule concentration is calculated from the
    positive difference of the internal concentration and its 'toxic_level'
    concentration as : max(0, ([mol_i] - toxic_level_i) / toxic_level_i ).

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    '''

    cdef int i
    cdef toxicity_str toxicity_s = cell.toxicity_s
    cdef mol_str * small_mol
    cdef double toxic_effect, toxic_level
    for i in range(toxicity_s.nr_internal_mols):
        small_mol = toxicity_s.internal_mols[i]
        toxic_level = small_mol.toxic_level
        toxic_effect = 0.
        if toxic_level > 0.:
            toxic_effect = max(0, (vars[small_mol.variable] - toxic_level)/ toxic_level)
        derivs[toxicity_s.variable] += toxic_effect

cdef void cell_odes(double vars[], double derivs[], cell_str * cell,
                    double env_volume, double membrane_occupancy_constant,
                    double volume_occupancy_constant,
                    double product_scaling, double scaling_power) nogil:
    '''
    Calculate rate of change of the cell's system of state variables.

    Processes included in the calculation are
    * cell volume change
    * ligand binding states of TFs
    * TF mediated gene transcription/translation
    * transport reactions
    * enzymatic conversion reactions
    * molecule degradation and cell volume mediated dilution
    * passive membrane diffusion
    * biomass production from building blocks
    * cell growth from biomass
    * buildup of toxic effects

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    cell : cell_str
        the cell structure
    env_volume : double
        volume of external environment
    membrane_occupancy_constant : double
        scaling parameter for transport rates
    volume_occupancy_constant : double
        scaling parameter for conversion rates
    product_scaling : double
        scaling parameter for biomass production rate
    scaling_power : double
        scaling paramter for production function
    '''

    calc_growth_rate(vars, cell, product_scaling, scaling_power)
    tfs_states(vars, cell.genome.tfs, cell.genome.nr_tfs)
    transcription(vars, derivs, cell, product_scaling, scaling_power)
    transporting(vars, derivs, cell, env_volume, membrane_occupancy_constant)
    converting(vars, derivs, cell, volume_occupancy_constant)
    degradation_and_dilution(vars, derivs, cell)
    diffusing(vars, derivs, cell, env_volume)
    production(vars, derivs, cell)
    cell_growth(vars, derivs, cell)
    toxicity(vars, derivs, cell)

cdef void pop_odes(double vars[], double derivs[], population_str * pop,
                   double env_volume, double membrane_occupancy_constant,
                   double volume_occupancy_constant) nogil:
    '''
    Calculate rate of change of the local population's system of state variables.

    Iterate through cells in the local population to update their state.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    pop : population_str
        the local population structure
    env_volume : double
        volume of external environment
    membrane_occupancy_constant : double
        scaling parameter for transport rates
    volume_occupancy_constant : double
        scaling parameter for conversion rates
    '''
    cdef int i
    for i in range(pop.nr_cells):
        cell_odes(vars, derivs, pop.cells[i], env_volume, membrane_occupancy_constant,
                  volume_occupancy_constant, pop.product_scaling, pop.product_scaling_power)

cdef void influx(double vars[], double derivs[], env_str * env) nogil:
    '''
    Calculate influx rates into the external environment.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    env : env_str
        external environment structure
    '''
    cdef int i
    cdef double rate
    cdef mol_str * mol_s
    for i in range(env.nr_small_mols):
        mol_s = env.small_mols[i]
        rate = mol_s.influx_const
        derivs[mol_s.variable] += rate

cdef void env_degrading(double vars[], double derivs[], env_str * env) nogil:
    '''
    External molecule degradation.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    env : env_str
        the external environment structure
    '''
    cdef int i
    cdef double rate
    cdef mol_str * mol_s
    for i in range(env.nr_small_mols):
        mol_s = env.small_mols[i]
        rate = vars[mol_s.variable] * mol_s.degr_const
        derivs[mol_s.variable] -= rate

cdef void derivs_zero(double derivs[], int dim) nogil:
    '''
    Set all derivatives to zero.

    Parameters
    ----------
    derivs : array
        array of rate values of the ode system
    '''
    cdef int i
    for i in range(dim):
        derivs[i] = 0.

cdef int master_eq_function(double time, double vars[], double derivs[], void *params) nogil:
    '''
    Calculate the update function of the full system of equations.

    Sub-routines are invoked to calculate:
    * influx of metabolites into the external environment
    * degradation of molecules in the external environment
    * updated state variables of the local population

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    derivs : array
        array of rate values of the ode system
    params : pointer to struct
        pointer to the system structure

    Returns
    -------
    success state
    '''
    cdef system_str * system = (<system_str *>params)
    derivs_zero(derivs, system.dimension)
    influx(vars, derivs, system.environment)
    env_degrading(vars, derivs, system.environment)
    pop_odes(vars, derivs, system.population, system.environment.volume,
             system.membrane_occupancy_constant, system.volume_occupancy_constant)
    return GSL_SUCCESS

cdef void store_cell_state(double vars[], cell_str * cell, double time) nogil:
    '''
    Store the cell's state variables at given time point to a time course vector.

    The cell has  time course vectors to store its state variable over time. The
    time point is stored in a separate time vector. The index of the last point
    stored is updated.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    cell : cell_str
        cell structure
    time : double
        time point
    '''
    cdef int index = cell.nr_time_points_stored
    cdef int i
    cell.time_points[index] = time
    for i in range(cell.nr_small_mols):
        cell.small_mols[i].time_concentration_vector[index] = vars[cell.small_mols[i].variable]
    for i in range(cell.genome.nr_pumps):
        cell.genome.pumps[i].time_concentration_vector[index] = vars[cell.genome.pumps[i].variable]
    for i in range(cell.genome.nr_enzymes):
        cell.genome.enzymes[i].time_concentration_vector[index] = vars[cell.genome.enzymes[i].variable]
    for i in range(cell.genome.nr_tfs):
        cell.genome.tfs[i].time_concentration_vector[index] = vars[cell.genome.tfs[i].variable]
    cell.production_s.time_production_vector[index] = vars[cell.production_s.variable]
    cell.toxicity_s.time_toxicity_vector[index] = vars[cell.toxicity_s.variable]
    cell.cell_size_s.time_cell_size_vector[index] = vars[cell.cell_size_s.var]
    cell.production_s.time_pos_prod_vector[index] = cell.production_s.pos_production
    cell.nr_time_points_stored += 1

cdef void store_pop_state(double vars[], population_str * pop, double time) nogil:
    '''
    Store the computed values of all variables of the local population of cells.

    Stores the values in the corresponding cell c_structs, so that they become
    known to the C-extension classes.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    pop : population_str
        local population structure
    time : double
        time point
    '''
    cdef int i
    for i in range(pop.nr_cells):
        store_cell_state(vars, pop.cells[i], time)

cdef void store_env_state(double vars[], env_str * env, double time) nogil:
    '''
    Store the computed values of all variables of the external environment.

    Parameters
    ----------
    vars : array
        array of variable values of the ode system
    env : env_str
        external environment structure
    time : double
        time point
    '''
    cdef int index = env.nr_time_points_stored
    cdef int i
    env.time_points[index] = time
    for i in range(env.nr_small_mols):
        env.small_mols[i].time_concentration_vector[index] = vars[env.small_mols[i].variable]
    env.nr_time_points_stored += 1

cdef void store_state_nogil(system_str * sys_s, double time) nogil:
    '''
    Store the computed values of system variables in the corresponding c_structs.

    Parameters
    ----------
    sys_s : system_str
        system structure
    time : double
        time point
    '''
    store_pop_state(sys_s.vars, sys_s.population, time)
    store_env_state(sys_s.vars, sys_s.environment, time)

cdef void print_vars(system_str * sys_s) nogil:
    cdef int i
    printf('vars: ')
    for i in range(sys_s.dimension):
        printf("var %d: %f ",i, sys_s.vars[i])
    printf('\n')

cdef class ENZYME:
    '''
    A C-extension representation of the python
    class:`VirtualMicrobes.virtual_cell.Gene.MetabolicGene` class.

    The class constructs a C representation of the python object. It instantiates
    * reactant and product structures
    * enzyme kinetic parameters
    * a time course vector for storing variable state

    After initialisation of all TFs in the CELL, set_reg_seq is called to
    instantiate:
    * regulatory sequence structure

    The construction of the c_struct members of the C-extension class is
    necessary and sufficient to calculate the state change associated with this
    enzyme as an part of the system of ODEs of the local ENVIRONMENT and
    POPULATION objects.

    Parameters
    ----------
    enzyme : class:`VirtualMicrobes.virtual_cell.Gene.MetabolicGene`
        python enzyme object
    cell : class:`VirtualMicrobes.virtual_cell.Cell.Cell`
        python cell object
    var_map : dict
        mapping from python objects to ODE system variable indices
    '''

    def __cinit__(self, enzyme, cell, var_map):
        cdef object params_list, subskss, params
        params_list, subs_kss = enzyme.ode_params()
        self.py_enzyme = enzyme
        self.enzyme_s.v_max = enzyme['v_max']
        self.enzyme_s.gene_multiplicity = cell.molecules["gene_products"][enzyme].multiplicity
        self.set_degradation(cell)
        self.enzyme_s.nr_equations = len(params_list)
        self.enzyme_s.variable = var_map["gene_products"][cell][enzyme]
        self.enzyme_s.params = <enzyme_params_str *>PyMem_Malloc(self.enzyme_s.nr_equations
                                                           * sizeof(enzyme_params_str))
        cdef int i
        for i, params in enumerate(params_list):
            self.add_params(params,subs_kss, i, cell, var_map)

    cdef set_time_course_view(self, py_cell):
        self.enzyme_s.time_concentration_vector = py_cell.molecules["gene_products"][self.py_enzyme].time_course

    cdef set_reg_seq(self, prom, op, genome, tfs_c_dict):
        cdef object binding_tfs_scores
        binding_tfs_scores = genome.binding_tfs_scores(op)
        self.reg_seq_c = REG_SEQ.__new__(REG_SEQ, prom, op, binding_tfs_scores, tfs_c_dict)
        self.enzyme_s.reg_seq = &(self.reg_seq_c.reg_seq_s)

    cdef set_degradation(self, cell):
        cdef double constant
        cdef object reaction
        reaction, constant = cell.molecules["gene_products"][self.py_enzyme].degradation
        self.enzyme_s.degr_const = constant

    cdef add_params(self, params, subs_kss, int eq_nr, cell, var_map):
        cdef int nr_reactants = len(params["reactants"])
        cdef int nr_products = len(params["products"])
        cdef enzyme_params_str enz_pars
        cdef object mol, re, p
        enz_pars.reactants = <reactant_str *> PyMem_Malloc(nr_reactants
                                                     * sizeof(reactant_str))
        enz_pars.products = <product_str *> PyMem_Malloc(nr_products
                                                   * sizeof(product_str))
        enz_pars.nr_reactants = len(params["reactants"])
        enz_pars.nr_products = len(params["products"])
        cdef int i
        for i, re in enumerate(params["reactants"]):
            mol = re["mol"]
            enz_pars.reactants[i].var = var_map["small_molecules"][cell][mol]
            if re["stoi"] < 1:
                raise Exception("stoi should be > 1", cell, params, re)
            enz_pars.reactants[i].stoi = re["stoi"]
            enz_pars.reactants[i].k_bind = subs_kss[mol]
        for i, p in enumerate(params["products"]):
            mol = p["mol"]
            if p["stoi"] < 1:
                raise Exception("stoi should be > 1", cell, params, p)
            enz_pars.products[i].var = var_map["small_molecules"][cell][mol]
            enz_pars.products[i].stoi = p["stoi"]
        self.enzyme_s.params[eq_nr] = enz_pars

    cdef int get_var(self):
        return self.enzyme_s.variable


    def __dealloc__(self):
        for i in range(self.enzyme_s.nr_equations):
            PyMem_Free(self.enzyme_s.params[i].reactants)
            PyMem_Free(self.enzyme_s.params[i].products)
        PyMem_Free(self.enzyme_s.params)
        self.enzyme_s.time_concentration_vector = None
        self.enzyme_s.time_change_rate_vector = None

cdef class PUMP:
    '''
    A C-extension representation of the python
    class:`VirtualMicrobes.virtual_cell.Gene.Transporter` class.

    The class constructs a C representation of the python object. It instantiates
    * reactant and product structures
    * enzyme kinetic parameters
    * a time course vector for storing variable state

    After initialisation of all TFs in the CELL, set_reg_seq is called to
    instantiate:
    * regulatory sequence structure

    The construction of the c_struct members of the C-extension class is
    necessary and sufficient to calculate the state change associated with this
    enzyme as an part of the system of ODEs of the local ENVIRONMENT and
    POPULATION objects.

    Parameters
    ----------
    pump : class:`VirtualMicrobes.virtual_cell.Gene.Transporter`
        python enzyme object
    cell : class:`VirtualMicrobes.virtual_cell.Cell.Cell`
        python cell object
    env : class:`VirtualMicrobes.environment.Environment.Locality`
        python environment object
    var_map : dict
        mapping from python objects to ODE system variable indices
    '''

    def __cinit__(self, pump, cell, env, var_map):
        cdef object params_list, subs_kss, ene_kss, params
        params_list, subs_kss, ene_kss = pump.ode_params()
        self.py_pump = pump
        self.pump_s.v_max = pump['v_max']
        self.pump_s.gene_multiplicity = cell.molecules["gene_products"][pump].multiplicity
        self.pump_s.direction = -1 if pump.params['exporting'] else 1.
        self.set_degradation(cell)
        self.pump_s.nr_equations = len(params_list)
        self.pump_s.variable = var_map["gene_products"][cell][pump]
        self.pump_s.params = <pump_params_str *>PyMem_Malloc(self.pump_s.nr_equations
                                                       * sizeof(pump_params_str))
        cdef int i
        for i, params in enumerate(params_list):
            self.add_params(params, subs_kss, ene_kss, i,  cell, env,var_map)

    cdef set_time_course_view(self, py_cell):
        self.pump_s.time_concentration_vector = py_cell.molecules["gene_products"][self.py_pump].time_course

    cdef set_reg_seq(self, prom, op, genome, tfs_c_dict):
        cdef object binding_tfs_scores = genome.binding_tfs_scores(op)
        self.reg_seq_c = REG_SEQ.__new__(REG_SEQ, prom, op, binding_tfs_scores, tfs_c_dict)
        self.pump_s.reg_seq = &(self.reg_seq_c.reg_seq_s)

    cdef set_degradation(self,  cell):
        cdef double constant
        cdef object reaction
        reaction, constant = cell.molecules["gene_products"][self.py_pump].degradation
        self.pump_s.degr_const = constant

    cdef add_params(self, params, subs_kss, ene_kss, int eq_nr, cell, env, var_map ):
        cdef pump_params_str pparams
        cdef object substrate, substrate_internal, energy_molecule
        substrate = params["reactants"]["substrate"]["mol"]
        substrate_internal = params["products"]["substrate"]["mol"]
        energy_molecule = params["reactants"]["energy"]["mol"]
        pparams.k_sub = subs_kss[substrate] #params["reactants"]["substrate"]["k_bind"]
        pparams.k_ene = ene_kss[energy_molecule] #params["reactants"]["energy"]["k_bind"]
        pparams.ene_cost = params["reactants"]["energy"]["stoi"]
        pparams.sub_stoi = params["reactants"]["substrate"]["stoi"]
        if pparams.ene_cost < 1 :
            raise Exception("stoi should be 1 or higher", params, cell)
        pparams.substrate_out = var_map["small_molecules"][env][substrate]
        pparams.energy_mol = var_map["small_molecules"][cell][energy_molecule]
        pparams.substrate_in = var_map["small_molecules"][cell][substrate_internal]
        self.pump_s.params[eq_nr] = pparams

    cdef int get_var(self):
        return self.pump_s.variable

    def __dealloc__(self):
        PyMem_Free(self.pump_s.params)
        self.pump_s.time_concentration_vector = None
        self.pump_s.time_change_rate_vector = None

cdef class TF:
    '''
    A C-extension representation of the python
    class:`VirtualMicrobes.virtual_cell.Gene.TranscriptionFactor` class.

    The class constructs a C representation of the python object. It instantiates
    * reactant and product structures
    * TF ligand structures
    * a time course vector for storing variable state

    After initialisation of all TFs in the cell, set_reg_seq is called to
    instantiate:
    * regulatory sequence structure

    The construction of the c_struct members of the C-extension class is
    necessary and sufficient to calculate the state change associated with this
    enzyme as an part of the system of ODEs of the local ENVIRONMENT and
    POPULATION objects.

    Parameters
    ----------
    enzyme : class:`VirtualMicrobes.virtual_cell.Gene.MetabolicGene`
        python enzyme object
    cell : class:`VirtualMicrobes.virtual_cell.Cell.Cell`
        python cell object
    env : class:`VirtualMicrobes.environment.Environment.Locality`
        python environment object
    var_map : dict
        mapping from python objects to ODE system variable indices
    '''

    def __cinit__(self,tf, cell, env, var_map):
        self.py_tf = tf
        self.tf_s.gene_multiplicity = cell.molecules["gene_products"][tf].multiplicity
        self.tf_s.eff_apo = self.py_tf["eff_apo"]
        self.tf_s.eff_bound = self.py_tf["eff_bound"]
        self.tf_s.k_bind_op = self.py_tf['k_bind_op']
        self.tf_s.coop = self.py_tf['binding_coop']
        self.set_degradation(cell)
        self.tf_s.variable = var_map["gene_products"][cell][self.py_tf]
        self.set_ligands(cell, env, var_map)

    cdef set_time_course_view(self, py_cell):
        self.tf_s.time_concentration_vector = py_cell.molecules["gene_products"][self.py_tf].time_course

    cdef set_reg_seq(self, prom, op, genome, tfs_c_dict):
        binding_tfs_scores = genome.binding_tfs_scores(op)
        self.reg_seq_c = REG_SEQ.__new__(REG_SEQ, prom, op, binding_tfs_scores, tfs_c_dict)
        self.tf_s.reg_seq = &(self.reg_seq_c.reg_seq_s)

    cdef set_degradation(self, cell):
        cdef double constant
        cdef object reaction
        reaction, constant = cell.molecules["gene_products"][self.py_tf].degradation
        self.tf_s.degr_const = constant

    cdef set_ligands(self, cell, env, var_map):
        cdef object ligand_kss, l
        ligand_kss = self.py_tf['ligand_ks']
        cdef double ligand_coop = self.py_tf['ligand_coop']
        self.tf_s.nr_ligands = len(ligand_kss)
        self.tf_s.ligands = <ligand_str *> PyMem_Malloc(self.tf_s.nr_ligands
                                                  * sizeof(ligand_str))
        cdef double k
        cdef int i
        for i,(l,k) in enumerate(ligand_kss.items()):
            if self.py_tf['sense_external']:
                self.tf_s.ligands[i].variable = var_map["small_molecules"][env][l.paired]
            else:
                self.tf_s.ligands[i].variable = var_map["small_molecules"][cell][l]
            self.tf_s.ligands[i].k_bind = k
            self.tf_s.ligands[i].coop = ligand_coop

    cdef int get_var(self):
        return self.tf_s.variable

    def __dealloc__(self):
        PyMem_Free(self.tf_s.ligands)
        self.tf_s.time_concentration_vector = None
        self.tf_s.time_change_rate_vector = None

cdef class REG_SEQ:
    '''
    A C-extension representation of the python
    class:`VirtualMicrobes.virtual_cell.Sequence.Operator` class.

    The class constructs a C representation of the python object. It instantiates
    * a regulatory sequence structure

    Parameters
    ----------
    promoter : class:`VirtualMicrobes.virtual_cell.Gene.Promoter`
        python promoter object
    operator : class:`VirtualMicrobes.virtual_cell.Sequence.Operator`
        python operator object
    binding_tfs_scores : dict
        mapping from python TF objects to binding scores
    tfs_c_dict : dict
        mapping from python tf to TF extension class objects
    '''
    def __cinit__(self, promoter, operator, binding_tfs_scores, tfs_c_dict):
        self.reg_seq_s.pr_str = promoter.strength
        self.add_binding_tfs(operator, binding_tfs_scores, tfs_c_dict)

    cdef add_binding_tfs(self, op, binding_tfs_scores, tfs_c_dict):
        self.reg_seq_s.nr_binding_tfs = len(binding_tfs_scores)
        self.reg_seq_s.binding_tfs = <binding_tf_str *> PyMem_Malloc(self.reg_seq_s.nr_binding_tfs
                                                               * sizeof(binding_tf_str))
        cdef object tf
        cdef int i
        cdef TF tf_c
        for i, (tf,s) in enumerate(binding_tfs_scores):
            tf_c = tfs_c_dict[tf]
            self.reg_seq_s.binding_tfs[i].score = s
            self.reg_seq_s.binding_tfs[i].tf = &(tf_c.tf_s)

    def __dealloc__(self):
        PyMem_Free(self.reg_seq_s.binding_tfs)

cdef class SMALL_MOL:
    '''
    A C-extension representation of the python
    class:`VirtualMicrobes.virtual_cell.Event.Molecule` class.

    The class constructs a C representation of the python object. It instantiates
    * small molecule structures
    * a time course vector for storing variable state

    Parameters
    ----------
    mol : class:`VirtualMicrobes.virtual_cell.Event.Molecule`
        python molecule object
    container : class:`VirtualMicrobes.virtual_cell.Cell.Cell`
                or class:`VirtualMicrobes.environment.Environment.Locality`
        python cell or environment object
    var_map : dict
        mapping from python objects to ODE system variable indices
    influx : bool
        flag to set influx of molecule
    diffusion_external_env : class:`VirtualMicrobes.environment.Environment` or None
        if set, the external environment for passive diffusion
    '''
    def __cinit__(self, mol, container, var_map,
                  influx=True, diffusion_external_env=None):
        self.py_mol = mol
        self.mol_s.toxic_level = mol.toxic_level
        self.mol_s.variable = var_map["small_molecules"][container][mol]

        self.set_degradation(container)
        if influx:
            self.set_influx(container)
        if diffusion_external_env is not None:
            self.set_diffusion(container, diffusion_external_env, var_map)

    cdef set_time_course_view(self, py_container):
        self.mol_s.time_concentration_vector = py_container.molecules["small_molecules"][self.py_mol].time_course

    cdef set_degradation(self, container):
        cdef double constant
        cdef object reaction
        reaction, constant = container.molecules["small_molecules"][self.py_mol].degradation
        self.mol_s.degr_const = constant

    cdef set_influx(self, container):
        cdef double constant
        cdef object reaction
        reaction, constant = container.molecules["small_molecules"][self.py_mol].influx
        self.mol_s.influx_const = constant

    cdef set_diffusion(self, cell, env, var_map):
        cdef double constant
        cdef object reaction
        reaction, constant = cell.molecules["small_molecules"][self.py_mol].diffusion
        reaction_dict = reaction.reaction_scheme()
        self.mol_s.diff_external_var = var_map["small_molecules"][env][reaction_dict["external"]]
        self.mol_s.diff_const = constant

    cdef int get_var(self):
        return self.mol_s.variable

    def __dealloc__(self):
        self.mol_s.time_concentration_vector = None
        self.mol_s.time_change_rate_vector = None

cdef class CELL:
    '''
    A C-extension representation of the python
    class:`VirtualMicrobes.virtual_cell.Cell.Cell` class.

    The class constructs a C representation of the python object. It instantiates
    * all gene product structures
    * all internal molecule structures
    * energy molecule structures
    * building block molecule structures
    * cell level parameters and variables
    * regulatory sequence structures
    * a time course vector for storing variable state

    The construction of the c_struct members of the C-extension class is
    necessary and sufficient to calculate the state change associated with this
    cell as a part of the system of ODEs of the local ENVIRONMENT and
    POPULATION objects.

    Parameters
    ----------
    cell : class:`VirtualMicrobes.virtual_cell.Cell.Cell`
        python cell object
    env : class:`VirtualMicrobes.environment.Environment.Locality`
        python environment object
    var_map : dict
        mapping from python objects to ODE system variable indices
    '''

    def __cinit__(self, cell,env, var_map):
        self.py_cell = cell
        self.pumps_c = []
        self.enzymes_c = []
        self.tfs_c = collections.OrderedDict()
        self.small_mols_c = []
        self.cell_s.volume = self.py_cell.volume
        self.cell_s.trans_cost = self.py_cell.transcription_cost
        self.cell_s.ene_trans_cost = self.py_cell.energy_transcription_cost
        self.cell_s.k_ene_trans = self.py_cell.energy_transcription_scaling
        self.cell_s.h_homeostatic_bb = self.py_cell.homeostatic_bb_scaling
        self.cell_s.nr_small_mols = len(self.py_cell.molecules["small_molecules"])
        self.cell_s.nr_energy_mols = len(self.py_cell.energy_mols)
        self.add_small_mols(env, var_map)
        self.add_pumps(env, var_map)
        self.add_enzymes(var_map)
        self.add_tfs(env, var_map)
        self.add_regulation()
        self.add_production(var_map)
        self.add_energy(var_map)
        self.add_toxicity(var_map)
        self.add_cell_size(var_map)

    cdef add_pumps(self, env, var_map):
        cdef object pumps, p
        pumps = list(self.py_cell.pumps)
        self.cell_s.genome.nr_pumps = len(pumps)
        self.cell_s.genome.pumps = <pump_str **> PyMem_Malloc(self.cell_s.genome.nr_pumps
                                                        * sizeof(pump_str*))
        cdef PUMP pump_c
        cdef int i
        for i, p in enumerate(pumps):
            pump_c = PUMP.__new__(PUMP, p, self.py_cell, env, var_map)
            self.cell_s.genome.pumps[i] = (&pump_c.pump_s)
            self.pumps_c.append(pump_c)

    cdef add_enzymes(self, var_map):
        cdef object enzymes, e
        enzymes = list(self.py_cell.enzymes)
        self.cell_s.genome.nr_enzymes = len(enzymes)
        self.cell_s.genome.enzymes = <enzyme_str **> PyMem_Malloc(self.cell_s.genome.nr_enzymes
                                                            * sizeof(enzyme_str*))
        cdef ENZYME enzyme_c
        cdef int i
        for i, e in enumerate(enzymes):
            enzyme_c = ENZYME.__new__(ENZYME, e, self.py_cell, var_map)
            self.cell_s.genome.enzymes[i] = (&enzyme_c.enzyme_s)
            self.enzymes_c.append(enzyme_c)

    cdef add_tfs(self, env, var_map):
        cdef object tfs, t
        tfs = list(self.py_cell.tfs)
        self.cell_s.genome.nr_tfs = len(tfs)
        self.cell_s.genome.tfs = <tf_str **> PyMem_Malloc(self.cell_s.genome.nr_tfs
                                                    * sizeof(tf_str*))
        cdef TF tf_c
        cdef int i
        for i, t in enumerate(tfs):
            tf_c = TF.__new__(TF, t, self.py_cell, env, var_map)
            self.cell_s.genome.tfs[i] = (&tf_c.tf_s)
            self.tfs_c[t] = tf_c

    cdef add_small_mols(self, env, var_map):
        cdef SMALL_MOL small_mol_c
        cdef double init_conc
        self.cell_s.small_mols = <mol_str **> PyMem_Malloc(self.cell_s.nr_small_mols * sizeof(mol_str*))
        cdef object mol
        cdef int i
        for i, mol in enumerate(self.py_cell.molecules["small_molecules"]):
            small_mol_c = SMALL_MOL.__new__(SMALL_MOL, mol, self.py_cell, var_map,
                                            False, env)
            self.cell_s.small_mols[i] = (&small_mol_c.mol_s)
            self.small_mols_c.append(small_mol_c)

    cdef add_regulation(self):
        cdef object pump, enzyme, tf
        cdef PUMP pump_c
        cdef ENZYME enzyme_c
        cdef TF tf_c
        for pump_c in self.pumps_c:
            if pump_c.pump_s.gene_multiplicity > 0: # else, no longer has gene in the genome
                pump_c.set_reg_seq(pump_c.py_pump.promoter,
                                   pump_c.py_pump.operator,
                                   self.py_cell.genome,
                                   self.tfs_c)
        for enzyme_c in self.enzymes_c:
            if enzyme_c.enzyme_s.gene_multiplicity > 0:
                enzyme_c.set_reg_seq(enzyme_c.py_enzyme.promoter,
                                     enzyme_c.py_enzyme.operator,
                                     self.py_cell.genome,
                                     self.tfs_c)
        for tf_c in self.tfs_c.values():
            if tf_c.tf_s.gene_multiplicity > 0:
                tf_c.set_reg_seq(tf_c.py_tf.promoter,
                                 tf_c.py_tf.operator,
                                 self.py_cell.genome,
                                 self.tfs_c)

    cdef add_production(self, var_map):
        self.cell_s.production_s.nr_building_blocks = len(self.py_cell.building_blocks_dict)
        self.cell_s.production_s.variable = var_map['cell_growth'][self.py_cell]
        self.cell_s.production_s.v_max = self.py_cell.v_max_growth
        self.cell_s.production_s.energy = self.py_cell.energy_for_growth
        self.cell_s.production_s.degr_const = self.py_cell.params.product_degradation_rate
        self.cell_s.production_s.building_blocks = <building_block_str**>PyMem_Malloc(self.cell_s.production_s.nr_building_blocks
                                                                            * sizeof(building_block_str*))
        cdef building_block_str * block_s
        cdef object bl
        cdef int stoi
        for i, (bl, stoi) in enumerate(self.py_cell.building_blocks_dict.items()):
            block_s = <building_block_str *>PyMem_Malloc(sizeof(building_block_str))
            block_s.var = var_map["small_molecules"][self.py_cell][bl]
            block_s.stoi = stoi
            self.cell_s.production_s.building_blocks[i] = block_s

    cdef add_energy(self, var_map):
        self.cell_s.energy_mols = <int*>PyMem_Malloc(self.cell_s.nr_energy_mols * sizeof(int))
        cdef object ene_mol
        cdef int i
        for i, ene_mol in enumerate(self.py_cell.energy_mols):
            self.cell_s.energy_mols[i] = var_map['small_molecules'][self.py_cell][ene_mol]

    cdef add_toxicity(self, var_map):
        self.cell_s.toxicity_s.nr_internal_mols = self.cell_s.nr_small_mols
        self.cell_s.toxicity_s.variable = var_map['cell_toxicity'][self.py_cell]
        self.cell_s.toxicity_s.internal_mols = <mol_str **> PyMem_Malloc(self.cell_s.toxicity_s.nr_internal_mols
                                                                    * sizeof(mol_str*))
        cdef int i
        for i in range(self.cell_s.nr_small_mols):
            self.cell_s.toxicity_s.internal_mols[i] = self.cell_s.small_mols[i]

    cdef int get_toxicity_var(self):
        return self.cell_s.toxicity_s.variable

    cdef add_cell_size(self, var_map):
        self.cell_s.cell_size_s.var = var_map['cell_volume'][self.py_cell]
        self.cell_s.cell_size_s.max_size = self.py_cell.max_volume
        self.cell_s.cell_size_s.growth_const = self.py_cell.growth_rate
        self.cell_s.cell_size_s.shrink_const = self.py_cell.shrink_rate
        self.cell_s.cell_size_s.growth_cost = self.py_cell.growth_cost

        self.cell_s.cell_size_s.growth_rate = 0.
        self.cell_s.cell_size_s.shrink_rate = 0.

    cdef int get_production_var(self):
        return self.cell_s.production_s.variable

    cdef double get_py_mol_conc(self, mol):
        return self.py_cell.get_small_mol_conc(mol)

    cdef double get_py_prot_conc(self, prot):
        return self.py_cell.get_gene_prod_conc(prot)

    cdef double get_py_production(self):
        return self.py_cell.raw_production

    cdef double get_py_toxicity(self):
        return self.py_cell.toxicity

    cdef double get_py_cell_size(self):
        return self.py_cell.volume

    cdef int get_cell_size_var(self):
        return self.cell_s.cell_size_s.var

    cdef set_time_course_views(self):
        self.cell_s.time_points = self.py_cell.time_points
        self.cell_s.toxicity_s.time_toxicity_vector = self.py_cell.toxicity_time_course
        self.cell_s.cell_size_s.time_cell_size_vector = self.py_cell.cell_size_time_course
        self.cell_s.production_s.time_production_vector = self.py_cell.raw_production_time_course
        self.cell_s.production_s.time_pos_prod_vector = self.py_cell.pos_prod_time_course
        cdef int i
        cdef PUMP p
        cdef ENZYME e
        cdef TF t
        cdef SMALL_MOL m
        for p in self.pumps_c:
            p.set_time_course_view(self.py_cell)
        for e in self.enzymes_c:
            e.set_time_course_view(self.py_cell)
        for t in self.tfs_c.values():
            t.set_time_course_view(self.py_cell)
        for m in self.small_mols_c:
            m.set_time_course_view(self.py_cell)

    def __dealloc__(self):
        PyMem_Free(self.cell_s.genome.pumps)
        PyMem_Free(self.cell_s.genome.enzymes)
        PyMem_Free(self.cell_s.genome.tfs)
        PyMem_Free(self.cell_s.small_mols)
        PyMem_Free(self.cell_s.energy_mols)
        cdef int i
        for i in range(self.cell_s.production_s.nr_building_blocks):
            PyMem_Free(self.cell_s.production_s.building_blocks[i])
        PyMem_Free(self.cell_s.production_s.building_blocks)
        PyMem_Free(self.cell_s.toxicity_s.internal_mols)
        self.cell_s.time_points = None
        self.cell_s.production_s.time_production_vector = None
        self.cell_s.production_s.time_pos_prod_vector = None
        self.cell_s.production_s.time_prod_change_rate_vector = None
        self.cell_s.toxicity_s.time_toxicity_vector = None
        self.cell_s.toxicity_s.time_tox_change_rate_vector = None
        self.cell_s.cell_size_s.time_cell_size_vector = None
        self.cell_s.cell_size_s.time_csize_change_rate_vector = None


cdef class ENVIRONMENT:
    '''
    A C-extension representation of the python
    class:`VirtualMicrobes.virtual_cell.environment.Environment` class.

    The class constructs a C representation of the python object. It instantiates
    * all external molecule structures
    * regulatory sequence structures
    * a time course vector for storing variable state

    The construction of the c_struct members of the C-extension class is
    necessary and sufficient to calculate the state change associated with this
    cell as a part of the system of ODEs of the local ENVIRONMENT and
    POPULATION objects.

    Parameters
    ----------
    locality : class:`VirtualMicrobes.environment.Environment.Locality`
        python environment object
    '''
    def __cinit__(self, locality):
        self.py_env = locality
        self.small_mols_c = collections.OrderedDict()
        self.env_s.volume = locality.volume
        self.env_s.nr_small_mols = len(self.py_env.molecules["small_molecules"])
        self.add_small_mols(locality, locality.variables_map)
        self.set_time_course_views()

    cdef add_small_mols(self, env, var_map):
        cdef SMALL_MOL small_mol_c
        self.env_s.small_mols = <mol_str **> PyMem_Malloc(self.env_s.nr_small_mols * sizeof(mol_str*))
        cdef object mol
        cdef int i
        for i, mol in enumerate(self.py_env.molecules["small_molecules"]):
            small_mol_c = SMALL_MOL.__new__(SMALL_MOL, mol, env, var_map)
            self.env_s.small_mols[i] = (&small_mol_c.mol_s)
            self.small_mols_c[mol] = small_mol_c

    cdef double get_py_mol_conc(self, mol):
        return self.py_env.get_small_mol_conc(mol)

    cdef set_time_course_views(self):
        self.env_s.nr_time_points_stored = 0
        self.env_s.time_points = self.py_env.time_points
        cdef SMALL_MOL m
        for m in self.small_mols_c.values():
            m.set_time_course_view(self.py_env)

    def __dealloc__(self):
        PyMem_Free(self.env_s.small_mols)
        self.env_s.time_points = None

cdef class POPULATION:
    '''
    A C-extension representation of the list of python
    class:`VirtualMicrobes.virtual_cell.Cell.Cell` objects in the local environment.

    The class constructs a C representation of the python object. It instantiates
    * all cell structures of the local population

    The construction of the c_struct members of the C-extension class is
    necessary and sufficient to calculate the state change associated with the
    list of cells in the local population as a part of the system of ODEs of the
    local ENVIRONMENT and POPULATION objects.

    Parameters
    ----------
    locality : class:`VirtualMicrobes.environment.Environment.Locality`
        python environment object
    product_scaling : double
        scaling parameter for production rate of cells
    product_scaling_power : double
        scaling parameter for production function
    '''
    def __cinit__(self, locality, double product_scaling, double product_scaling_power):
        self.pop_s.nr_cells = len(locality.cells)
        self.pop_s.product_scaling = product_scaling
        self.pop_s.product_scaling_power = product_scaling_power
        self.pop_s.cells = <cell_str **>PyMem_Malloc(self.pop_s.nr_cells * sizeof(cell_str*))
        cdef int i
        cdef CELL cell_c
        self.cells_c = [] #unordered OK (?)
        for i, cell in enumerate(locality.cells):
            cell_c = CELL.__new__(CELL, cell, locality, locality.variables_map)
            self.cells_c.append(cell_c)
            self.pop_s.cells[i] = (&cell_c.cell_s)
        self.set_time_course_views()

    cdef set_time_course_views(self):
        cdef CELL cell_c
        for cell_c in self.cells_c:
            cell_c.set_time_course_views()

    cdef update_time_course_views(self):
        cdef CELL cell_c
        for cell_c in self.cells_c:
            if cell_c.py_cell.arrays_changed:
                cell_c.set_time_course_views()
                cell_c.py_cell.arrays_changed = False

    def __dealloc__(self):
        PyMem_Free(self.pop_s.cells)

cdef class SYSTEM:
    '''
    A C-extension class representing the system of variables that define the
    local population at a single grid point.

    The class constructs a C representation of the python object. It instantiates
    * all gene product structures
    * all internal molecule structures
    * energy molecule structures
    * building block molecule structures
    * cell level parameters and variables
    * regulatory sequence structures
    * a time course vector for storing variable state

    The construction of the c_struct members of the C-extension class is
    necessary and sufficient to calculate the state change associated with this
    cell as a part of the system of ODEs of the local ENVIRONMENT and
    POPULATION objects.

    Parameters
    ----------
    cell : class:`VirtualMicrobes.virtual_cell.Cell.Cell`
        python cell object
    env : class:`VirtualMicrobes.environment.Environment.Locality`
        python environment object
    var_map : dict
        mapping from python objects to ODE system variable indices
    '''
    def __cinit__(self, locality, product_scaling, int num_threads=8):
        self.py_loc = locality
        self.sys_s.dimension = locality.dimension
        self.sys_s.vars = <double *> PyMem_Malloc(self.sys_s.dimension * sizeof(double))
        self.sys_s.derivs = <double *> PyMem_Malloc(self.sys_s.dimension * sizeof(double))
        self.sys_s.master_eq = master_eq_function
        self.sys_s.num_threads = num_threads
        self.sys_s.membrane_occupancy_constant = locality.params.transporter_membrane_occupancy
        self.sys_s.volume_occupancy_constant = locality.params.enzyme_volume_occupancy
        cdef POPULATION pop_c = POPULATION.__new__(POPULATION, locality, product_scaling,
                                                   locality.params.growth_rate_scaling)
        self.pop_c = pop_c
        self.sys_s.population = (&pop_c.pop_s)
        cdef ENVIRONMENT env_c = ENVIRONMENT.__new__(ENVIRONMENT, locality)
        self.env_c = env_c
        self.sys_s.environment = (&env_c.env_s)
        self.init_internal_vars()
        self.init_external_vars()

    cdef bint check_sane_vals(self):
        cdef bint sane = True
        cdef int i
        for i in range(self.sys_s.dimension):
            if self.sys_s.vars[i] < 0. or self.sys_s.vars[i] > 1e6:
                printf("var %d is not sane at %f \n", i, self.sys_s.vars[i])
                sane = False
        return sane

    cdef void init_external_vars(self):
        cdef int nr_vars = self.sys_s.dimension
        cdef SMALL_MOL small_mol
        cdef ENVIRONMENT env_c
        env_c = self.env_c
        for small_mol in env_c.small_mols_c.values():
            self.sys_s.vars[small_mol.get_var()] = env_c.get_py_mol_conc(small_mol.py_mol)

    cdef void update_external_vars(self):
        cdef ENVIRONMENT env_c = self.env_c
        if env_c.py_env.new_concentrations:
            self.init_external_vars()

    cdef void init_internal_vars(self):
        cdef int var
        cdef CELL cell_c
        cdef PUMP pump
        cdef ENZYME enzyme
        cdef TF tf_c
        cdef SMALL_MOL small_mol
        for cell_c in self.pop_c.cells_c:
            cell_c.cell_s.nr_time_points_stored = cell_c.py_cell.nr_time_points_stored
            for pump in cell_c.pumps_c:
                self.sys_s.vars[pump.get_var()] = cell_c.get_py_prot_conc(pump.py_pump)
            for enzyme in cell_c.enzymes_c:
                self.sys_s.vars[enzyme.get_var()] = cell_c.get_py_prot_conc(enzyme.py_enzyme)
            for py_tf, tf_c in cell_c.tfs_c.items():
                self.sys_s.vars[tf_c.get_var()] = cell_c.get_py_prot_conc(py_tf)
            for small_mol in cell_c.small_mols_c:
                self.sys_s.vars[small_mol.get_var()] = cell_c.get_py_mol_conc(small_mol.py_mol)
            self.sys_s.vars[cell_c.get_production_var()] = cell_c.get_py_production()
            self.sys_s.vars[cell_c.get_toxicity_var()] = cell_c.get_py_toxicity()
            self.sys_s.vars[cell_c.get_cell_size_var()] = cell_c.get_py_cell_size()

    cdef void update_internal_vars(self):
        cdef CELL cell_c
        for cell_c in self.pop_c.cells_c:
            if cell_c.py_cell.divided:
                self.sys_s.vars[cell_c.get_cell_size_var()] = cell_c.get_py_cell_size()
                self.sys_s.vars[cell_c.get_production_var()] = cell_c.get_py_production()

    cdef void update_influxes(self):
        cdef SMALL_MOL small_mol_c
        cdef object mol_py
        for mol_py, small_mol_c in self.env_c.small_mols_c.items():
            small_mol_c.set_influx(self.env_c.py_env)

    cdef void update_sys(self, double product_scaling, bint reset):
        if reset:
            self.init_external_vars()
            self.init_internal_vars()
        else:
            self.update_internal_vars()
            self.update_external_vars()
            self.update_influxes()
        self.sys_s.population.product_scaling = product_scaling
        self.sys_s.environment.nr_time_points_stored = 0
        cdef POPULATION pop_c = self.pop_c
        pop_c.update_time_course_views()

    cdef void store_nr_time_points_py(self):
        cdef CELL cell_c
        self.py_loc.nr_time_points_stored = self.sys_s.environment.nr_time_points_stored
        for cell_c in self.pop_c.cells_c:
            cell_c.py_cell.nr_time_points_stored = cell_c.cell_s.nr_time_points_stored

    def __dealloc__(self):
        PyMem_Free(self.sys_s.vars)
        PyMem_Free(self.sys_s.derivs)
