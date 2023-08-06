#@PydevCodeAnalysisIgnore

## THIS pxd file is a header to odes.pyx . Writing headers for pyx (cython)
#files, ensures that when importing the pyx into another cython source file, the
#type declaration are known at compile time just like with normal c-headers.

ctypedef int (*Func)(double, double[], double[], void *) nogil #@IgnoreException
cdef void store_state_nogil(system_str *, double) nogil
#-------------------- **GROWTH FUNCTION** --------------------#

cdef struct building_block_str:
    int var
    int stoi

cdef struct production_str:
    int variable
    bint energy
    double v_max
    double degr_const
    int nr_building_blocks
    building_block_str ** building_blocks
    double [:] time_production_vector
    double [:] time_prod_change_rate_vector
    double pos_production
    double [:] time_pos_prod_vector

cdef struct toxicity_str:
    int variable
    double [:] time_toxicity_vector
    double [:] time_tox_change_rate_vector
    int nr_internal_mols
    mol_str ** internal_mols

cdef struct cell_size_str:
    int var
    double growth_rate
    double shrink_rate
    double growth_const
    double shrink_const
    double growth_cost
    double max_size
    double [:] time_cell_size_vector
    double [:] time_csize_change_rate_vector

#------------------------ **ENZYME** -------------------------#

cdef struct reactant_str:
    int var
    int stoi
    double k_bind

cdef struct product_str:
    int var
    int stoi

cdef struct enzyme_params_str:
    int nr_reactants
    int nr_products
    reactant_str * reactants
    product_str * products
    double sub_reac_rate

cdef struct enzyme_str:
    double v_max
    double gene_multiplicity
    double degr_const
    int nr_equations
    enzyme_params_str * params
    int variable
    reg_seq_str * reg_seq
    double [:] time_concentration_vector
    double [:] time_change_rate_vector

cdef class ENZYME:
    cdef public object py_enzyme
    cdef enzyme_str enzyme_s
    cdef int get_var(self)
    cdef REG_SEQ reg_seq_c
    cdef set_reg_seq(self, object, object, object, object)
    cdef set_degradation(self, object)
    cdef add_params(self, object, object, int, object, object)
    cdef set_time_course_view(self, object)

#------------------------ **PUMP** -------------------------#

cdef struct pump_params_str:
    double k_sub
    double k_ene
    double ene_cost
    double sub_stoi
    int substrate_out
    int substrate_in
    int energy_mol
    double sub_reac_rate

cdef struct pump_str:
    double v_max
    double gene_multiplicity
    double degr_const
    double direction
    int nr_equations
    pump_params_str * params
    int variable
    reg_seq_str * reg_seq
    double [:] time_concentration_vector
    double [:] time_change_rate_vector


cdef class PUMP:
    cdef public object py_pump
    cdef pump_str pump_s
    cdef int get_var(self)
    cdef REG_SEQ reg_seq_c
    cdef set_reg_seq(self, object, object, object, object)
    cdef set_degradation(self, object)
    cdef add_params(self, object, object, object, int, object, object, object)
    cdef set_time_course_view(self, object)

#------------------------ **TF** -------------------------#

cdef struct tf_str:
    double gene_multiplicity
    double degr_const
    double coop
    int nr_equations
    int variable
    double eff_apo
    double eff_bound
    double k_bind_op
    int nr_ligands
    ligand_str * ligands
    reg_seq_str * reg_seq
    double w_tf_apo
    double [:] time_concentration_vector
    double [:] time_change_rate_vector

cdef struct binding_tf_str:
    double score
    tf_str * tf

cdef struct ligand_str:
    int variable
    double k_bind
    double coop

cdef class TF:
    cdef public object py_tf
    cdef tf_str tf_s
    cdef int get_var(self)
    cdef REG_SEQ reg_seq_c
    cdef set_reg_seq(self, object, object, object, object)
    cdef set_degradation(self, object)
    cdef set_ligands(self, object, object, object)
    cdef set_time_course_view(self, object)

#------------------------ **REGULATION** -------------------------#

cdef struct reg_seq_str:
    double pr_str
    int nr_binding_tfs
    binding_tf_str * binding_tfs

cdef class REG_SEQ:
    cdef reg_seq_str reg_seq_s
    cdef add_binding_tfs(self, object, object, object)

#------------------------ **SMALL MOLECULES** -------------------------#

cdef public struct mol_str:
    int variable
    double degr_const
    double diff_const
    double influx_const
    double toxic_level
    int diff_external_var
    double grid_diffusion_force
    double [:] time_concentration_vector
    double [:] time_change_rate_vector

cdef class SMALL_MOL:
    cdef public object py_mol
    cdef mol_str mol_s
    cdef int get_var(self)
    cdef set_degradation(self, object)
    cdef set_influx(self, object)
    cdef set_diffusion(self, object, object, object)
    cdef set_time_course_view(self, object)

#------------------------ **CELL** -------------------------#

cdef struct genome_str:
    pump_str ** pumps
    tf_str ** tfs
    enzyme_str ** enzymes
    int nr_pumps
    int nr_enzymes
    int nr_tfs

cdef struct cell_str:
    double volume
    double trans_cost
    double k_ene_trans
    double ene_trans_cost
    double h_homeostatic_bb
    int nr_small_mols
    mol_str ** small_mols
    int nr_energy_mols
    int * energy_mols
    genome_str genome
    double [:] time_points
    int nr_time_points_stored
    production_str production_s
    toxicity_str toxicity_s
    cell_size_str cell_size_s

cdef class CELL:
    cdef public object py_cell
    cdef public pumps_c #dictionary
    cdef public enzymes_c #dictionary
    cdef public tfs_c #dictionary
    cdef public small_mols_c #dictionary
    cdef int dummy
    cdef cell_str cell_s
    cdef add_pumps(self, object, object)
    cdef add_enzymes(self, object)
    cdef add_tfs(self, object, object)
    cdef add_small_mols(self, object, object)
    cdef add_regulation(self)
    cdef add_energy(self, object)
    cdef double get_py_mol_conc(self, object)
    cdef double get_py_prot_conc(self, object)

    cdef add_production(self, object)
    cdef double get_py_production(self)
    cdef int get_production_var(self)

    cdef add_toxicity(self, object)
    cdef double get_py_toxicity(self)
    cdef int get_toxicity_var(self)

    cdef add_cell_size(self, object)
    cdef double get_py_cell_size(self)
    cdef int get_cell_size_var(self)
    cdef set_time_course_views(self)

#------------------------ **ENVIRONMENT** -------------------------#

cdef struct env_str:
    double volume
    int nr_small_mols
    int nr_time_points_stored
    double [:] time_points
    mol_str ** small_mols

cdef class ENVIRONMENT:
    cdef public object py_env
    cdef env_str env_s
    cdef public small_mols_c
    cdef add_small_mols(self, object, object)
    cdef double get_py_mol_conc(self, object)
    cdef set_time_course_views(self)

#------------------------ **POPULATION** -------------------------#

cdef struct population_str:
    int nr_cells
    double product_scaling
    double product_scaling_power
    cell_str ** cells

cdef class POPULATION:
    cdef public cells_c
    cdef population_str pop_s
    cdef set_time_course_views(self)
    cdef update_time_course_views(self)

#------------------------ **SYSTEM** -------------------------#

cdef struct system_str:
    Func master_eq
    int dimension
    population_str * population
    env_str * environment
    double * vars
    double * derivs
    int num_threads
    double * time
    double membrane_occupancy_constant
    double volume_occupancy_constant

cdef class SYSTEM:
    cdef public object py_loc
    cdef public pop_c
    cdef system_str sys_s
    cdef public env_c
    cdef void init_internal_vars(self)
    cdef void init_external_vars(self)
    cdef void update_external_vars(self)
    cdef void update_internal_vars(self)
    cdef void update_influxes(self)
    cdef void update_sys(self, double, bint)
    cdef void store_nr_time_points_py(self)
    cdef bint check_sane_vals(self)
