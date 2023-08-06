import collections
from copy import copy, deepcopy
import itertools
import math
import orderedset
import warnings

from VirtualMicrobes.event import Reaction
from VirtualMicrobes.event.Reaction import Degradation, Diffusion, ClassConvert
from VirtualMicrobes.mutate.Mutation import ChromosomeDuplication, ChromosomeDeletion, \
    Fusion, Fission, PointMutation, TandemDuplication, StretchDeletion, \
    Inversion, Translocation, Insertion, OperatorInsertion
from VirtualMicrobes.my_tools.utility import OrderedDefaultdict, GeneProduct, SmallMol, \
    OrderedSet
import VirtualMicrobes.my_tools.utility as util
from VirtualMicrobes.readwrite import read_obj
import VirtualMicrobes.simulation.class_settings as cs
from VirtualMicrobes.virtual_cell.Chromosome import Chromosome
from VirtualMicrobes.virtual_cell.Gene import MetabolicGene, Transporter, TranscriptionFactor
import VirtualMicrobes.virtual_cell.Gene as Gene
from VirtualMicrobes.virtual_cell.Genome import Genome
from VirtualMicrobes.virtual_cell.PhyloUnit import AddInheritanceType
from VirtualMicrobes.virtual_cell.Sequence import Sequence
import networkx as nx
import numpy as np


try:
    import bottleneck as bt
    np.nanmean = bt.nanmean
except ImportError:
    pass

def _production_func():
    pass

def _toxicity_func(l, t):
    toxicity = 0.
    if t:
        toxicity = max(0, (l - t) / t)
    return toxicity

def _toxicity_effect_func(r, e, s):
    '''
    calculate a (raw) death rate from the toxic effects accumulated in the cell.
    Currently it uses a Hill like function for death rate calculation.
    :param r: base rate
    :param e: accumulated toxic effects
    :param s: scaling of toxic effects
    '''
    #return r ** (1. / (1. + s * e))
    return e/(s+e) * (1 - r) + r

def _gen_id_func(i):
    return int(i) + 1

def make_mutations_dict():
    return {'chromosomal': list(), 'sg': list(), 'stretch':list()}

def make_inherited_hgt_dict():
    return {'internal': list(), 'external': list()}

class Cell:
    class_version = '2.6'
    __metaclass__ = AddInheritanceType
    __phylo_type = cs.phylo_types['Cell']
    uid = 0
    '''
    An Cell in the Simulation.

    Initializes the state of the cell (without genome); notably:
        * internal molecule dictionaries
        * arrays to hold time course data of internal molecule concentrations
        * mutation dictionary, a record of mutations that occured during reproduction
        * internal state variables for volume, toxicity etc

    Parameters
    ----------
    params : :class:`attrdict.AttrDict`
        mapping object that holds global simulation parameters
    environment : :class:`VirtualMicrobes.environment.Environment`
        environment that cell lives in; determines molecular and reaction universe
    rand_gen : RNG
    fromfile: path to .cell-file to reproduce cell from
    toxicity_function : func
        calculates toxicity based on actual and threshold level of a concentration
    toxicity_effect_function : func
        calculates added death rate from toxicity
    '''
    def __init__(self, params, environment, rand_gen=None,
                 toxicity_function=None,toxicity_effect_function=None,
                 time_birth=-1, **kwargs):
        self.version = self.__class__.class_version

        super(Cell, self).__init__(time_birth=time_birth, **kwargs)
        if toxicity_function is None:
            toxicity_function = _toxicity_func
        if toxicity_effect_function is None:
            toxicity_effect_function = _toxicity_effect_func

        ### set a reference to the global paramaters ###
        self.params = params
        self.max_time_course_length = 0
        self.arrays_changed = False
        self.init_cell_time_courses()
        ### initialize variables of the cell by extracting from init params ###
        self.init_cell_params()
        self.init_rand_gen = rand_gen
        self.molecules = dict()  # NOTE: unordered ok ; mapping to store info about molecules present in the cell
        self.molecules["gene_products"] = OrderedDefaultdict(GeneProduct)
        self.molecules["small_molecules"] = OrderedDefaultdict(SmallMol)
        self.init_mol_views()
        self.toxicity_func = toxicity_function
        self.toxic_effect_func = toxicity_effect_function
        self.add_small_molecules(environment,
                                 conc=self.params.init_small_mol_conc,
                                 degr_const=self.params.small_mol_degr_const,
                                 ene_degr_const=self.params.ene_degr_const,
                                 bb_degr_const=self.params.bb_degr_const)
        self.init_building_blocks_dict(nr_blocks=self.params.nr_cell_building_blocks,
                                       rand_gen=self.init_rand_gen,
                                       stois=self.params.building_block_stois)
        self.init_energy_mols(environment)
        self.init_mutations_dict()
        #self.init_genome(environment, ... ) moved by brem
        self.volume = self.params.cell_init_volume
        self.raw_production = 0.
        self.pos_production = 0.
        self.raw_production_change_rate = 0.
        self.toxicity = 0.
        self.toxicity_change_rate = 0.
        self.raw_death_rate = 0.
        self.production_toxic_effect = 0.
        self.alive = True
        self.divided = False
        self.wiped = False
        self.iterage = 0

    def init_cell_params(self):
        '''
        Set cell parameters based on simulation parameter settings.
        '''
        self.max_volume = self.params.max_cell_volume
        self.growth_rate = self.params.cell_growth_rate # volume increase rate
        self.shrink_rate = self.params.cell_shrink_rate
        self.growth_cost = self.params.cell_growth_cost
        self.v_max_growth = self.params.v_max_growth # rate at which building blocks are converted into production potential
        self.energy_for_growth = self.params.energy_for_growth # consume energy when making production potential
        self.transcription_cost = self.params.transcription_cost
        self.energy_transcription_cost = self.params.energy_transcription_cost
        self.energy_transcription_scaling = self.params.energy_transcription_scaling
        self.homeostatic_bb_scaling = self.params.homeostatic_bb_scaling

    def set_properties(self, celldict):
        '''
        Set cell properties based on dict.

        Parameters
        ----------
        celldict : dict
            dict with values for cell properties
        '''
        self.volume = celldict['volume']
        self.raw_death_rate = celldict['raw_death_rate']
        self.raw_production = celldict['raw_production']
        self.raw_production_change_rate = celldict['raw_production_change_rate']
        self.pos_production = celldict['pos_production']
        self.iterage = celldict['iterage']
        self.alive = celldict['alive']
        self.version = self.__class__.class_version
        self.divided = celldict['divided']
        self.toxicity = celldict['toxicity']
        self.toxicity_change_rate = celldict['toxicity_change_rate']
        self.marker_dict['lineage'] = celldict['lineage']
        #self.marker_dict['lineage'] = celldict['iterage']%1000
        self.wiped = celldict['wiped']

    def set_molconcs(self, concdict):
        '''
        Set molecule concentrations based on dict.

        Parameters
        ----------
        concdict : dict
            dict with values for mol concentrations
        '''
        for mol in self.molecules["small_molecules"]:
            #print 'setting conc of molecule ' + str(mol.name) + ' to ' + str(concdict[mol.name])
            self.set_small_mol_conc(mol,concdict[mol.name])

    def init_building_blocks_dict(self, nr_blocks, rand_gen, stois):
        '''
        Initialize the dictionary of cellular building blocks and their
        stoichiometry.

        Parameters
        ----------
        nr_blocks : int
            number of different metabolic building blocks of the cell.
        rand_gen : RNG
        stois : tuple of int
            (lower, higher) range of stoichiometric constants from which to
            randomly draw stoichiometries.
        '''
        if nr_blocks is None:
            cell_blocks = self._get_building_blocks()
        else:
            cell_blocks = rand_gen.sample(self._get_building_blocks(), nr_blocks)
        self.building_blocks_dict = collections.OrderedDict([(block, rand_gen.randint(*stois) )
                                                             for block in cell_blocks  ])

    def init_energy_mols(self, environment):
        '''
        Store the energy molecules of the cell.

        Parameters
        ----------
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            simulation environment that contains metabolic universe

        Notes
        -----
        energy_mols are used in odes.pyx
        '''
        self.energy_mols = [ mol for mol in environment.internal_molecules if mol.is_energy ]

    def init_genome(self, environment,
                    chrom_compositions=None, min_bind_score=None,
                    prioritize_influxed=None,
                    rand_gene_params=None, circular_chromosomes=None,
                    rand_gen=None, randomize=True):
        '''
        Iniitialize the genome of the cell.

        The genome is constructed according to a list of chromosome composition
        descriptions. These descriptions specify the number of each gene type a
        set of chromosomes. Sets of metabolic , transport and transcription
        factor genes are initialized using heuristic functions that guarantee
        basic viability of the cell and a basic logic in transported and sensed
        metabolites, by taking into account the set of indispensible metabolites
        (building blocks and energy carriers). Finally, kinetic and other parameters of
        all genes are randomized and the genes distributed over the chromosomes.

        Parameters
        ----------
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            simulation environment that determines metabolic universe
        chrom_compositions : list of :class:`VirtualMicrobes.my_tools.utility.GeneTypeNumbers`
            per chromosome composition of different gene types
        min_bind_score : float
            parameter for minimal binding score for transcription regulation
        prioritize_influxed : bool
            first choose enzymatic reactions that use substrates that are influxed in `environment`
        rand_gene_params : :class:`VirtualMicrobes.my_tools.utility.ParamSpace`
            range from which to draw randomized gene parameters
        circular_chromosomes : bool
            make the chromosomes circular
        rand_gen : RNG
        randomize : bool
            whether gene parameters should be randomized after creation

        Returns
        -------
        :class:`VirtualMicrobes.virtual_cell.Genome.Genome`
        '''

        if chrom_compositions is None:
            chrom_compositions = self.params.chromosome_compositions
        if min_bind_score is None:
            min_bind_score = self.params.min_bind_score
        if prioritize_influxed is None:
            prioritize_influxed = self.params.prioritize_influxed_metabolism
        if rand_gene_params is None:
            rand_gene_params = self.params.rand_gene_params
        if circular_chromosomes is None:
            circular_chromosomes = self.params.circular_chromosomes
        if rand_gen is None:
            rand_gen = self.init_rand_gen

        metabolic_pathway_dict = {'consumed':OrderedSet(),
                                  'produced':OrderedSet(),
                                  'converted':OrderedSet(),
                                  'imported':OrderedSet(),
                                  'exported':OrderedSet(),
                                  'sensed':OrderedSet()}
        for bb in self.building_blocks_dict:
            metabolic_pathway_dict['consumed'].add(bb.mol_class)
        nr_tfs, nr_pumps, nr_enzymes = map(sum, zip(*[ (cp.tf, cp.pump, cp.enz)
                                                      for cp in chrom_compositions ]))
        enzymes = self.generate_enzymes(nr_enzymes, environment, rand_gen,
                                        metabolic_pathway_dict, prioritize_influxed=prioritize_influxed)
        if len(enzymes) < nr_enzymes:
            warnings.warn('Only {} out of {} enzymes could be generated'
                          ' for this individual.'.format(len(enzymes), nr_enzymes))
        pumps = self.generate_pumps(nr_pumps, environment, rand_gen,
                                    metabolic_pathway_dict, prioritize_influxed=prioritize_influxed)
        if len(pumps) < nr_pumps:
            warnings.warn('Only {} out of {} enzymes could be generated'
                          ' for this individual.'.format(len(pumps), nr_pumps))
        tfs = self.generate_tfs(nr_tfs, environment, rand_gen, metabolic_pathway_dict)

        if randomize:
            map(lambda g: g.randomize(rand_gene_params, rand_gen), enzymes+pumps+tfs)
        chromosomes = []
        for chrom_comp in chrom_compositions:
            c_enz, c_pumps, c_tfs = (rand_gen.sample(enzymes, chrom_comp.enz),
                                     rand_gen.sample(pumps, chrom_comp.pump),
                                     rand_gen.sample(tfs, chrom_comp.tf) )
            genes = c_enz + c_pumps + c_tfs
            enzymes = list(OrderedSet(enzymes) -  OrderedSet(c_enz))
            pumps = list(OrderedSet(pumps) - OrderedSet(c_pumps))
            tfs = list(OrderedSet(tfs) - OrderedSet(c_tfs))
            rand_gen.shuffle(genes)
            chromosomes.append(Chromosome(gene_list=genes, circular=circular_chromosomes))

        self.genome = Genome(chromosomes, min_bind_score)

        self.init_gene_products()           # Moved by brem. Used to be in Cell.__init__ but we moved init_genome..

        return self.genome

    def set_state_from_file(self, environment, filename, max_lin_marker):
        '''
        Set the state of the cell based on a configuration file.

        Parameters
        ----------
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment defines metabolic universe for the cell
        filename : string
            name of cell state file
        lineagemarker : marker to distinguish lineage
        '''
        celldict = read_obj.parse_cell_stringrepr(filename)                                               # Generates cell with help from file
        self.read_genome(environment, celldict['genes'], celldict['genome'])
        self.set_properties(celldict['cell_properties'])
        self.set_molconcs(celldict['molecule_concs'])
        if celldict['cell_properties']['lineage'] is not None:
            if int(celldict['cell_properties']['lineage']) > max_lin_marker:
                celldict['cell_properties']['lineage'] = str((int)(celldict['cell_properties']['lineage'])%max_lin_marker+1)
                print 'Note to user: lineage marker for cell too big, setting to ' + celldict['cell_properties']['lineage'] + " instead."
            self.mark('lineage', int(celldict['cell_properties']['lineage']))
            print 'setting lineage marker to ' + str(int(celldict['cell_properties']['lineage']))

    def read_genome(self, environment, gene_dict, genome_order, verbose=False):
        '''
        Reads and sets genome based on genes dictionary and a list of gene indexes representing the genome order.

        Parameters
        ----------
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment provides the reactions to match to the genes
        gene_dict : dict
            dictionary that contains all properties of the gene
            most are just values such as v_max, prom_str, type etc.
            ene_ks and subs_ks are themselves dicts for each mol
        genome_order : list
            a list of indexes that represent in what order the genes should be put into the genome

        Returns
        -------
        :class:`VirtualMicrobes.virtual_cell.Genome
        '''

        genes = {}
        genes_concs = {}
        self.genome = Genome([],min_bind_score = self.params.min_bind_score)  # Empty genome because of []

        for gene, gene_props in gene_dict.items():
            if verbose:
                print 'Reading gene of type ' + gene_props['type']
            newgene = Gene.read_gene(environment, gene_props, gene)
            genes[gene] = newgene
            genes_concs[newgene] = gene_props['concentration']
        for chrom in genome_order:
            gene_list = []
            for index in genome_order[chrom]:
                gene_list.append(genes[index])
                if verbose:
                    print 'adding ' + genes[index].params["type"] + ' to chromosome ' + str(chrom)

            self.genome.add_chromosome(Chromosome(gene_list=gene_list, circular=self.params.circular_chromosomes))

        for gene in genes.values():
            if gene not in list(self.genome):
                self.add_gene_product(gene,concentration=genes_concs)

        self.init_gene_products(concentration=genes_concs)     # With this, only genes in genome are added

        self.genome.init_regulatory_network(self.params["min_bind_score"])
        return self.genome


    def generate_enzymes(self, nr_enzymes, env, rand_gen,
                         metabolic_pathway_dict,
                         prioritize_influxed=True):
        '''
        Generate the set of enzymes of the cell.

        Uses heuristics for constructing 'viable' initial metabolic pathways for
        the production of building blocks and energy metabolites.

        Parameters
        ----------
        nr_enzymes : int
            number of enzymes to generate
        env :  :class:`VirtualMicrobes.environment.Environment.Environment`
            environment provides the set of metabolites and possible metabolic
            reactions
        rand_gen : RNG
        metabolic_pathway_dict : dict
            dictionary to keep track of metabolites consumed and produced by the
            cell.
        prioritize_influxed : bool
            first create enzymes that can utilize metabolites that are present
            (influxed) in environment

        Returns
        -------
        list of :class:`VirtualMicrobes.virtual_cell.Gene.MetabolicGene`s
        '''
        tries=10
        def influxed_species_in_mol_class(mol_class, env):
            return (len(set(mol_class.molecules.values()) &
                        set(map(lambda m: m.paired,env.influxed_mols))) > 0)

        enzymes = []
        class_conversions = [ c for c in env.conversions if isinstance(c, ClassConvert) ]
        for _ in range(nr_enzymes):
            conversion = None
            bb_classes = OrderedSet([ bb.mol_class for bb in self.building_blocks_dict] )
            bb_lacking = bb_classes - metabolic_pathway_dict['produced']
            produceable_lacking_bb = [ bb for bb in bb_lacking
                                     if len(env.mols_to_reactions_dict['conversion']['produced'][bb]) > 0]
            # if not all building blocks are produced yet, create enzyme that produces bb
            if len(produceable_lacking_bb) > 0:
                for _ in range(tries):
                    produce_bb = rand_gen.choice(produceable_lacking_bb)
                    potential_conversions = env.mols_to_reactions_dict['conversion']['produced'][produce_bb]

                    if prioritize_influxed:
                        #prioritize reactions with reactants that are influxed in the environment
                        prioritized = filter(lambda c: all([ influxed_species_in_mol_class(r, env)
                                                            or r.is_energy for r in c.reactants  ]),
                                             potential_conversions)
                        if len(prioritized):
                            potential_conversions = prioritized
                    try:
                        conversion = rand_gen.choice(potential_conversions)
                        break # succeeded
                    except IndexError:
                        warnings.warn('No available reactions to produce building block {}'.format(produce_bb))
            # else, if no energy is produced, create enzyme to produce energy carrier
            if conversion is None and not sum([ p.is_energy for p in metabolic_pathway_dict['produced'] ]):
                for _ in range(tries):
                    produce_ene = rand_gen.choice(env.energy_classes.values())
                    try:
                        conversion = rand_gen.choice(env.mols_to_reactions_dict['conversion']['produced'][produce_ene])
                        break # succeeded
                    except IndexError:
                        warnings.warn('No available reactions to produce energy class {}'.format(produce_ene))
            if conversion is None:
                consumed_not_produced = metabolic_pathway_dict['consumed'] - metabolic_pathway_dict['produced']
                consumed_not_produced_producable = [ mc for mc in consumed_not_produced
                                                    if len(env.mols_to_reactions_dict['conversion']['produced'][mc]) > 0]
                choose_class_conversion = rand_gen.choice([True,False]) if len(class_conversions) else False
                if len(consumed_not_produced_producable) > 0 and not choose_class_conversion:
                    for _ in range(tries):
                        produce_consumed = rand_gen.choice(consumed_not_produced_producable)
                        try:
                            conversion = rand_gen.choice(env.mols_to_reactions_dict['conversion']['produced'][produce_consumed])
                            break # succeeded
                        except IndexError:
                            warnings.warn('No available reactions to produce intermediate {}'.format(produce_consumed))
                elif not choose_class_conversion:
                    conversion = rand_gen.choice(env.conversions)
                else:
                    not_converted = ((metabolic_pathway_dict['produced'] &
                                      OrderedSet(env.mols_to_reactions_dict['class_convert'].keys()) ) -
                                      metabolic_pathway_dict['converted'])

                    if len(not_converted) > 0:
                        convert_produced = rand_gen.choice(list(not_converted))
                        try:
                            conversion = rand_gen.choice(env.mols_to_reactions_dict['class_convert'][convert_produced])
                        except IndexError:
                            warnings.warn('No available class conversion for {}'.format(convert_produced))
                    else:
                        conversion = rand_gen.choice([ c for c in env.conversions if isinstance(c, ClassConvert) ])

            if conversion is None: # No conversion reaction could be chosen
                continue

            # update dict to with produced and consumed metabolites
            if not isinstance(conversion, ClassConvert):
                for reac_class in conversion.reactants:
                    metabolic_pathway_dict['consumed'].add(reac_class)
                for prod_class in conversion.products:
                    metabolic_pathway_dict['produced'].add(prod_class)
            else:
                metabolic_pathway_dict['converted'].add(conversion.substrate.mol_class)
            enzymes.append(MetabolicGene(reaction=conversion, operator_seq_len=self.params.operator_seq_len))
        return enzymes

    def generate_pumps(self, nr_pumps, env, rand_gen,
                       metabolic_pathway_dict,
                       import_first=True, prioritize_influxed=True):
        '''
        Generate set of transporters of the cell.

        Use heuristics for connecting to the metabolic pathways formed so far by
        the enzymes present in the cell.

        Parameters
        ----------
        nr_pumps: int
            number of transporters to generate
        env :  :class:`VirtualMicrobes.environment.Environment.Environment`
            environment provides the set of metabolites and possible metabolic
            reactions
        rand_gen : RNG
        metabolic_pathway_dict : dict
            dictionary to keep track of metabolites consumed and produced by the
            cell.
        import_first : bool
            first create import enzymes for all metabolites that can be consumed
            in metabolism
        prioritize_influxed : bool
            first create transporters that can import metabolites that are
            present (influxed) in environment

        Returns
        -------
        list of :class:`VirtualMicrobes.virtual_cell.Gene.Transporter`s

        See Also
        --------
        `generate_enzymes`

        '''
        def influxed_species_in_mol_class(mol_class, env):
            return len(set(mol_class.molecules.values()) &
                       set(map(lambda m: m.paired,env.influxed_mols))) > 0

        pumps = []
        building_block_classes = OrderedSet([ b.mol_class
                                             for b in self.building_blocks_dict] )
        for _ in range(nr_pumps):
            transport = None
            not_imported = (metabolic_pathway_dict['consumed'] -
                            metabolic_pathway_dict['imported'])
            importable = OrderedSet([ mc for mc in not_imported
                            if len(env.mols_to_reactions_dict['transport'][mc]) > 0 ])
            importable_priority = (importable -
                                   (metabolic_pathway_dict['produced'] -
                                    building_block_classes))
            not_exported = ((metabolic_pathway_dict['produced'] -
                             metabolic_pathway_dict['exported']) -
                            building_block_classes )
            exportable = OrderedSet([ mc for mc in not_exported
                            if len(env.mols_to_reactions_dict['transport'][mc]) > 0 ])
            exportable_priority = exportable -  metabolic_pathway_dict['consumed']

            importer = True if import_first else rand_gen.choice([True,False])
            if importer and len(importable) > 0:
                if len(importable_priority) > 0:
                    if prioritize_influxed:
                        #prioritize transport with substrates that are influxed in the environment

                        prioritized = filter(lambda c: influxed_species_in_mol_class(c, env) , importable)
                        if len(prioritized):
                            importable_priority = prioritized
                    to_import = rand_gen.choice(list(importable_priority))
                else:
                    to_import = rand_gen.choice(list(importable))
                try:
                    transport = rand_gen.choice(env.mols_to_reactions_dict['transport'][to_import])
                except IndexError:
                    warnings.warn('No available transport for {}'.format(to_import))
            if transport is None and len(exportable) > 0:
                importer = False
                if len(exportable_priority) > 0:
                    to_export = rand_gen.choice(list(exportable_priority))
                else:
                    to_export = rand_gen.choice(list(exportable))
                try:
                    transport = rand_gen.choice(env.mols_to_reactions_dict['transport'][to_export])
                except IndexError:
                    warnings.warn('No available transport for {}'.format(to_export))
            if transport is None:
                transport = rand_gen.choice(env.transports)

            if transport is None: # No transport reaction could be chosen
                continue

            transport_type = 'imported' if importer else 'exported'
            metabolic_pathway_dict[transport_type].add(transport.substrate_class)
            pumps.append(Transporter(reaction=transport,
                                     exporting=not importer,
                                     operator_seq_len=self.params.operator_seq_len))
        return pumps


    def generate_tfs(self, nr_tfs, env, rand_gen,  metabolic_pathway_dict, bb_ene_only=False):
        '''
        Create TFs of the cell.

        Prioritizes TFs that sense metabolites that are relevant for the cell,
        i.e. metabolites that are actively consumed or produced by the cell's
        enzymes (or production function).

        Parameters
        ----------
        nr_tfs : int
            number of tfs to generate
        env :  :class:`VirtualMicrobes.environment.Environment.Environment`
            environment provides the set of metabolites and possible metabolic reactions
        rand_gen : RNG
        metabolic_pathway_dict : dict
            dictionary to keep track of metabolites consumed and produced by the cell.
        bb_ene_only : bool
            create TFs with either a building block or an energy carrier as ligand exclusively

        Returns
        -------
        list of :class:`VirtualMicrobes.virtual_cell.Gene.TranscriptionFactor`s

        See Also
        --------
        :func:`generate_enzymes`
        '''
        tfs = []
        for _ in range(nr_tfs):
            if bb_ene_only:
                ligand_class = rand_gen.choice([m for m in env.molecule_classes if m.has_building_block or m.is_energy])
            else:
                not_sensed = (metabolic_pathway_dict['consumed'] |
                              metabolic_pathway_dict['produced']) - metabolic_pathway_dict['sensed']
                if len(not_sensed) > 0:
                    ligand_class = rand_gen.choice(list(not_sensed))
                else:
                    ligand_class = rand_gen.choice(env.molecule_classes)
            sense_external = rand_gen.choice([False,True])
            metabolic_pathway_dict['sensed'].add(ligand_class)
            tfs.append(TranscriptionFactor(ligand_mol_class=ligand_class,
                                           ligand_cooperativity=self.params.ligand_binding_cooperativity,
                                           operator_seq_len=self.params.operator_seq_len,
                                           binding_seq_len=self.params.binding_seq_len,
                                           binding_cooperativity=self.params.tf_binding_cooperativity,
                                           sense_external=sense_external))
        return tfs

    def reset_grn(self, min_bind_score=None):
        '''
        Recalculate and reset all binding interactions in the genome.

        Parameters
        ----------
        min_bind_score : float
            minimum identity score to set a regulatory interaction.
        '''
        if min_bind_score is None:
            min_bind_score = self.params.min_bind_score
        self.genome.reset_regulatory_network(min_bind_score)

    def update_grn(self, min_bind_score=None):
        '''
        Update the regulatory network, by finding (new) matches between TF binding sites
        and gene operators.

        min_bind_score : float
            minimum identity score to set a regulatory interaction.
        '''
        if min_bind_score is None:
            min_bind_score = self.params.min_bind_score
        self.genome.update_regulatory_network(min_bind_score)

    ########################## Mutation ##########################
    @property
    def point_mut(self):
        '''List of point mutations of this individual.'''
        return self.mutations["sg"]
    @property
    def sequence_mut(self):
        '''List of sequence mutations of this individual.'''
        return [ p for p in self.mutations['sg'] if isinstance(p.new_val, Sequence)]
    @property
    def chromosomal_mut(self):
        '''List of chromosomal mutations of this individual.'''
        return self.mutations["chromosomal"]
    @property
    def chromosome_dup(self):
        '''List of chromosome duplications of this individual.'''
        return [ c for c in self.mutations['chromosomal'] if isinstance(c, ChromosomeDuplication)]
    @property
    def chromosome_del(self):
        '''List of chromosome deletions of this individual.'''
        return [ c for c in self.mutations['chromosomal'] if isinstance(c, ChromosomeDeletion)]
    @property
    def chromosome_fusion(self):
        '''List of chromosome fusions of this individual.'''
        return [ c for c in self.mutations['chromosomal'] if isinstance(c, Fusion)]
    @property
    def chromosome_fission(self):
        '''List of chromosome fissions of this individual.'''
        return [ c for c in self.mutations['chromosomal'] if isinstance(c, Fission)]
    @property
    def stretch_mut(self):
        '''List of stretch mutations of this individual.'''
        return [s for s in self.mutations['stretch'] if not isinstance(s, Insertion)]
    @property
    def tandem_dup(self):
        '''List of stretch duplications of this individual.'''
        return [ s for s in self.mutations['stretch'] if isinstance(s, TandemDuplication)]
    @property
    def stretch_del(self):
        '''List of stretch deletions of this individual.'''
        return [ s for s in self.mutations['stretch'] if isinstance(s, StretchDeletion) ]
    @property
    def translocate(self):
        '''List of stretch translocations of this individual.'''
        return [ s for s in self.mutations['stretch'] if isinstance(s, Translocation)]
    @property
    def stretch_invert(self):
        '''List of stretch inversions of this individual.'''
        return [ s for s in self.mutations['stretch'] if isinstance(s, Inversion) ]
    @property
    def internal_hgt(self):
        '''List of internal Horizontal Gene Transfers of this individual.'''
        return self.inherited_hgt['internal']
    @property
    def external_hgt(self):
        '''List of external Horizontal Gene Transfers of this individual.'''
        return self.inherited_hgt['external']

    ########################## Mutation Counts ##########################
    @property
    def point_mut_count(self):
        '''Number of point mutations of this individual.'''
        return len(self.point_mut)
    @property
    def chromosomal_mut_count(self):
        '''Number of chromosomal mutations of this individual.'''
        return len(self.chromosomal_mut)
    @property
    def chromosome_dup_count(self):
        '''Number of chromosomal duplications of this individual.'''
        return len(self.chromosome_dup)
    @property
    def chromosome_del_count(self):
        '''Number of chromosomal deletions of this individual.'''
        return len(self.chromosome_del)
    @property
    def chromosome_fuse_count(self):
        '''Number of chromosomal fusions of this individual.'''
        return len(self.chromosome_fusion)
    @property
    def chromosome_fiss_count(self):
        '''Number of chromosomal fissions of this individual.'''
        return len(self.chromosome_fission)
    @property
    def sequence_mut_count(self):
        '''Number of sequence mutations of this individual.'''
        return len(self.sequence_mut)
    @property
    def stretch_mut_count(self):
        '''Number of stretch mutations of this individual.'''
        return len(self.stretch_mut)
    @property
    def tandem_dup_count(self):
        '''Number of stretch duplications of this individual.'''
        return len(self.tandem_dup)
    @property
    def stretch_del_count(self):
        '''Number of stretch deletions of this individual.'''
        return len(self.stretch_del)
    @property
    def translocate_count(self):
        '''Number of stretch translocations of this individual.'''
        return len(self.translocate)
    @property
    def stretch_invert_count(self):
        '''Number of stretch inversions of this individual.'''
        return len(self.stretch_invert)
    @property
    def internal_hgt_count(self):
        '''Number of internal Horizontal Gene Transfers of this individual.'''
        return len( self.internal_hgt )
    @property
    def external_hgt_count(self):
        '''Number of external Horizontal Gene Transfers of this individual.'''
        return len(self.external_hgt )
    @property
    def ancestral_mutations(self):
        '''
        Cumulative mutations in the line(s) of descent.

        For each LOD of this individual concatenate all mutations in each
        mutation category that happened in the ancestors of this individual.
        Because multiple LODs might exist, return a list of dictionaries that
        hold all mutations that this lineage acumulated, per mutation category.

        Returns
        -------
        list of mutation dictionaries of LODs
        '''
        mutations_dicts = []
        for lod in self.lods_up():
            mutations_dict = make_mutations_dict()
            for a in lod:
                for k in mutations_dict:
                    mutations_dict[k] += a.mutations[k]
            mutations_dicts.append(mutations_dict)
        return mutations_dicts

    @property
    def tf_sensed(self):
        '''
        The set of molecule classes that are sensed by TFs.
        '''
        return set( [tf.ligand_class for tf in self.genome.tfs ])
    @property
    def conversions_type(self):
        '''
        The set of conversion reactions in the genome.
        '''
        return set( [ enz.reaction for enz in self.genome.enzymes ] )
    @property
    def importer_type(self):
        '''
        The set of import reactions in the genome.
        '''
        return set([ p.reaction for p in self.genome.inf_pumps] )
    @property
    def exporter_type(self):
        '''
        The set of export reactions in the genome.
        '''
        return set([ p.reaction for p in self.genome.eff_pumps])

    def genes_get_prop_vals(self, genes, get_prop):
        '''
        Construct array of values of a gene property for all duplicates of a
        list of genes.

        Parameters
        ----------
        genes : list of :class:`VirtualMicrobes.virtual_cell:Gene:Gene` objects
            The genes for which to list the proprty
        get_prop : func [:class:`VirtualMicrobes.virtual_cell:Gene:Gene`] -> value
            A function that takes a gene as argument and returns a value

        Returns
        -------
        numpy array
        '''
        return np.array([get_prop(g) for g in genes])

    ########################## Genome Stats ##########################

    @property
    def genome_size(self):
        return self.genome.size
    @property
    def chromosome_count(self):
        return len(self.genome.chromosomes)
    @property
    def tf_count(self):
        return len(list(self.genome.tfs))
    @property
    def enzyme_count(self):
        return len(list(self.genome.enzymes))
    @property
    def pump_count(self):
        return len(list(self.genome.pumps))
    @property
    def eff_pump_count(self):
        return len(list(self.genome.eff_pumps))
    @property
    def inf_pump_count(self):
        return len(list(self.genome.inf_pumps))
    @property
    def promoter_strengths(self):
        return self.genes_get_prop_vals(self.genome, lambda x: x.promoter.strength )
    @property
    def tf_promoter_strengths(self):
        return self.genes_get_prop_vals(self.genome.tfs, lambda x: x.promoter.strength)

    def gene_substrate_ks(self, ks_param, genes):
        return np.array([ ks for gene in genes for ks in gene[ks_param].values()])
    @property
    def tf_ligand_ks(self):
        return self.gene_substrate_ks('ligand_ks', self.genome.tfs)
    @property
    def enz_subs_ks(self):
        return self.gene_substrate_ks('subs_ks', self.genome.enzymes)
    @property
    def pump_ene_ks(self):
        return self.gene_substrate_ks('ene_ks', self.genome.pumps)
    @property
    def pump_subs_ks(self):
        return self.gene_substrate_ks('subs_ks', self.genome.pumps)

    def qual_expr_diff(self, ref_cell):
        '''
        Calculate a qualitative expression difference with a reference cell.

        Parameters
        ----------
        ref_cell : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            reference cell to compare gene expression.

        Returns
        -------
        mean positive (relative) difference of all gene expression values.
        '''
        concs_self = [self.molecules['gene_products'][gene].concentration for gene in list(self.genome)]
        concsum_self = sum(concs_self)

        concs_ref = [ref_cell.molecules['gene_products'][gene].concentration for gene in list(ref_cell.genome)]
        concsum_ref = sum(concs_ref)

        if concsum_self > 0.0 and concsum_ref > 0.0:
            concs_self = [x / concsum_self for x in concs_self]
            concs_ref = [x / concsum_ref for x in concs_ref]
            absdiff = [abs(x - y) for x, y in zip(concs_self, concs_ref)]
            return np.mean(absdiff)*concsum_self
        else:
            return 0.0

    def gene_substrate_differential_ks(self, ks_param, genes):
        '''
        Calculate differences between K parameters per substrate for a list of genes.

        Parameters
        ----------
        ks_param : str
            type of parameter
        genes : list
            list of genes for which to calculate the diffs

        Returns
        -------
        array of diffs per gene
        '''

        per_gene_diffs = []
        for gene in genes:
            abs_diffs = []
            for one,two in itertools.combinations(gene[ks_param].values(),2):
                abs_diffs.append( abs(one - two ))
            per_gene_diffs.append(np.average(abs_diffs))
        return np.array(per_gene_diffs)
    @property
    def tf_ligand_differential_ks(self):
        return self.gene_substrate_differential_ks('ligand_ks', self.genome.tfs)
    @property
    def enz_subs_differential_ks(self):
        return self.gene_substrate_differential_ks('subs_ks', self.genome.enzymes)
    @property
    def pump_ene_differential_ks(self):
        return self.gene_substrate_differential_ks('ene_ks', self.genome.pumps)
    @property
    def pump_subs_differential_ks(self):
        return self.gene_substrate_differential_ks('subs_ks', self.genome.pumps)
    @property
    def tf_differential_reg(self):
        return np.array([ abs(tf['eff_apo'] - tf['eff_bound']) for tf in self.genome.tfs ])
    @property
    def tf_k_bind_ops(self):
        return self.genes_get_prop_vals(self.genome.tfs, lambda x: x['k_bind_op'])
    @property
    def enz_vmaxs(self):
        return self.genes_get_prop_vals(self.genome.enzymes, lambda x: x['v_max'])
    @property
    def pump_vmaxs(self):
        return self.genes_get_prop_vals(self.genome.pumps, lambda x: x['v_max'])
    @property
    def enz_promoter_strengths(self):
        return self.genes_get_prop_vals(self.genome.enzymes, lambda x: x.promoter.strength)
    @property
    def pump_promoter_strengths(self):
        return self.genes_get_prop_vals(self.genome.pumps, lambda x: x.promoter.strength)
    @property
    def avrg_promoter_strengths(self):
        return np.nanmean(self.promoter_strengths)
    @property
    def tf_avrg_promoter_strengths(self):
        return np.nanmean(self.tf_promoter_strengths)
    @property
    def enz_avrg_promoter_strengths(self):
        return np.nanmean(self.enz_promoter_strengths)
    @property
    def pump_avrg_promoter_strengths(self):
        return np.nanmean(self.pump_promoter_strengths)
    @property
    def sum_promoter_strengths(self):
        return np.sum(self.promoter_strengths)
    @property
    def tf_sum_promoter_strengths(self):
        return np.sum(self.tf_promoter_strengths)
    @property
    def enz_sum_promoter_strengths(self):
        return np.sum(self.enz_promoter_strengths)
    @property
    def pump_sum_promoter_strengths(self):
        return np.sum(self.pump_promoter_strengths)

    @property
    def gene_type_counts(self):
        return {'tfs':  self.tf_count,
                'eff-pumps': self.eff_pump_count,
                'inf-pumps':self.inf_pump_count,
                'enzymes': self.enzyme_count}

    @property
    def copy_numbers(self):
        return np.array(self.genome.copy_numbers.values())
    @property
    def copy_numbers_tfs(self):
        return np.array(self.genome.copy_numbers_tfs.values())
    @property
    def copy_numbers_enzymes(self):
        return np.array(self.genome.copy_numbers_enzymes.values())
    @property
    def copy_numbers_inf_pumps(self):
        return np.array(self.genome.copy_numbers_inf_pumps.values())
    @property
    def copy_numbers_eff_pumps(self):
        return np.array(self.genome.copy_numbers_eff_pumps.values())

    ########################## Metabolic Stats ##########################
    @property
    def enzymes(self):
        '''
        Enzyme products in the Cell.

        Notes
        -----
        Can include gene products of genes that are no longer in the genome.
        '''
        return ( prod for prod in self.gene_products if prod['type'] == 'enz')

    @property
    def pumps(self):
        '''
        Transporter products in the Cell.

        Notes
        -----
        Can include gene products of genes that are no longer in the genome.
        '''
        return ( prod for prod in self.gene_products if prod['type'] == 'pump')

    @property
    def tfs(self):
        '''
        TF products in the Cell.

        Notes
        -----
        Can include gene products of genes that are no longer in the genome.
        '''
        return ( prod for prod in self.gene_products if prod['type'] == 'tf')

    @property
    def reaction_set_dict(self):
        '''
        Dictionary of enzymatic reaction types to reactions.

        Reactions of genes are mapped to their reaction types (Conversion, Transport).
        '''
        d = OrderedDefaultdict(set)
        for g in self.gene_products:
            if g.is_enzyme:
                exporting = g['exporting'] if g['type'] == 'pump' else False
                d[g.reaction.type_].add((g.reaction, exporting))
        return d

    @property
    def reaction_set_dict2(self):
        '''
        Dictionary of enzymatic reaction types to reactions.

        Reactions of genes are mapped to their reaction types (Conversion, Transport).

        Notes
        -----
        Different formatting from `reaction_set_dict`.
        '''
        d = {'conversion':set(), 'exporter':set(), 'importer':set()}
        for g in self.gene_products:
            if g.is_enzyme:
                if g['type'] == 'pump':
                    if g['exporting']:
                        d['exporter'].add(g.reaction)
                    else:
                        d['importer'].add(g.reaction)
                else:
                    d[g.reaction.type_].add(g.reaction)
        return d

    @property
    def providing(self):
        '''
        Return the set of metabolic classes that are produced AND exported.

        See Also
        --------
        :func:`producer_type`
        :func:`export_type`
        '''
        return self.producer_type & self.export_type #intersection

    @property
    def strict_providing(self):
        '''
        Return provided resources classes that are not imported by self.

        See Also
        --------
        :func:`providing`
        '''
        return self.providing - self.import_type

    @property
    def exploiting(self):
        '''
        Return the set of metabolic classes that are imported and consumed.
        '''
        return self.import_type & self.consumer_type

    @property
    def strict_exploiting(self):
        '''
        Return exploited resources classes that are not produced by self.

        See Also
        --------
        :func:`exploiting`
        '''
        return self.exploiting - self.producer_type

    @property
    def producer_type(self):
        '''
        Return the set of all metabolic classes produced in enzymatic reactions by this cell.
        '''
        products = set()
        for r in self.conversions_type:
            if isinstance(r, ClassConvert):
                continue
            products |= set(r.products)
        return products

    @property
    def consumer_type(self):
        '''
        Return the set of all metabolic classes consumed in enzymatic reactions by this cell.
        '''
        substrates = set()
        for r in self.conversions_type:
            if isinstance(r, ClassConvert):
                continue
            substrates |= set(r.reactants)
        return substrates

    @property
    def import_type(self):
        '''
        Return the set of all metabolic classes imported by this cell.
        '''
        imported = set()
        for p in set(self.genome.inf_pumps):
            imported |= set(p.reaction.products)
        return imported

    @property
    def export_type(self):
        '''
        Return the set of all metabolic classes exported by this cell.
        '''
        exported = set()
        for p in set(self.genome.eff_pumps):
            exported |= set(p.reaction.products)
        return exported

    @property
    def metabolic_type(self):
        '''
        Return a set of sets that uniquely defines the metabolic functions of this cell.
        '''
        return frozenset([('producer', frozenset(self.producer_type )),
                          ('consumer',frozenset(self.consumer_type )),
                          ('import', frozenset(self.import_type )),
                          ('export', frozenset(self.export_type ))
                          ])

    @property
    def produces(self):
        '''
        Set of produced metabolic species.
        '''
        return Reaction.produces(self.conversions_type)
    @property
    def consumes(self):
        '''
        Set of consumed metabolic species.
        '''
        return Reaction.consumes(self.conversions_type)

    def is_autotroph(self, env):
        '''
        Determine if cell is autotrophic within an environment.

        Autotrophy is defined as the ability to produce building blocks from
        precursors that are present 'natively' in the environment. This may be
        done in a multistep pathway in which the cell produces intermediates
        with its own metabolic enzymes.

        Parameters
        ----------
        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            the environment relative to which autotrophy is tested

        See Also
        --------
        :func:`is_heterotroph`
        '''
        bb = set(self.building_blocks)
        conversions = [ e.reaction for e in set(self.genome.enzymes)]
        mol_set = Reaction.find_product_set([ m.paired for m in env.influxed_mols ], conversions)
        if not bb - mol_set:
            return True
        return False

    def is_heterotroph(self, env):
        '''
        Determine if cell is heterotrophic within an environment.

        Heterotrophy is defined as the ability to produce the building blocks from
        precursors that could only be present as (by)products from metabolism of
        other individuals in the environment, but not natively present (through influx).

        Parameters
        ----------
        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            the environment relative to which autotrophy is tested

        See Also
        --------
        :func:`is_autotroph`
        '''
        bb = set(self.building_blocks)
        ene = set(self.energy_mols)
        conversions = [ e.reaction for e in set(self.genome.enzymes)]
        not_influxed = set(env.internal_molecules) - set([ m.paired for m in env.influxed_mols ]) - bb - ene
        mol_set = Reaction.find_product_set(not_influxed, conversions)
        if not bb - mol_set:
            return True
        return False

    def trophic_type(self, env):
        '''
        Trophic type classification of individual's metabolic capacities.

        Based on the metabolic reactions present in the individual's genome
        an individual can be classified as being 'autotrophic' and/or
        'heterotrophic'. Facultative mixotrophs are defined as having both
        autotrophic and heterotrophic metabolic capacities, while obligate
        mixotroph are neither self-sufficient autotrophs, nor heterotrophs.

        Parameters
        ----------
        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            the environment trophic type is determined in

        See Also
        --------
        :func:`is_autotroph`
        :func:`is_heterotroph`
        '''
        auto = self.is_autotroph(env)
        hete = self.is_heterotroph(env)
        if auto and hete:
            # can use either trophic modes to sustain itself
            return 'fac-mixotroph'
        elif auto:
            # can be fully autotrophic
            return 'autotroph'
        elif hete:
            # can be fully heterotrophic
            return 'heterotroph'
        else:
            # has to use a mix of autotrophic and heterotrophic means to sustain itself
            return 'obl-mixotroph'

    @property
    def providing_count(self):
        '''Number of metabolic classes produced and exported by this individual.'''
        return len(self.providing)
    @property
    def strict_providing_count(self):
        '''Number of metabolic classes produced, exported  but not
        consumed by this individual.'''
        return len(self.strict_providing)
    @property
    def exploiting_count(self):
        '''Number of metabolic classes imported and consumed by this individual.'''
        return len(self.exploiting)
    @property
    def strict_exploiting_count(self):
        '''Number of metabolic classes imported and consumed, but not produced
         by this individual.'''
        return len(self.strict_exploiting)
    @property
    def producing_count(self):
        '''Number of metabolic classes produced by this individual.'''
        return len(self.producer_type)
    @property
    def consuming_count(self):
        '''Number of metabolic classes consumed by this individual.'''
        return len(self.consumer_type)
    @property
    def importing_count(self):
        '''Number of metabolic classes imported by this individual.'''
        return len(self.import_type)
    @property
    def exporting_count(self):
        '''Number of metabolic classes exported by this individual.'''
        return len(self.export_type)
    @property
    def building_blocks(self):
        '''Building Blocks in metabolism of this individual.'''
        return self.building_blocks_dict.keys()

    ########################## Ecotype Stats ##########################
    def metabolic_type_vector(self, env):
        '''
        Construct boolean vector of metabolic capacity of the cell.

        Based on the complete set of environmental molecule classes, write out
        a cells metabolism in terms of produced, consumed, imported and exported
        molecule classes by the cells metabolism.

        Parameters
        ----------
        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment relative to which the metabolic capacity is determined

        Returns
        -------
        mapping of metabolic-function to
        :class:`VirtualMicrobes.event.Molecule.MoleculeClass`s presence/absence.
        '''
        env_met_classes = env.molecule_classes
        vect_dict = {'produced':dict(), 'consumed':dict(), 'imported':dict(), 'exported':dict()} # NOTE: unordered ok
        produced = self.producer_type
        consumed = self.consumer_type
        imported = self.import_type
        exported = self.export_type
        for met in env_met_classes:
            vect_dict['produced'][met] = True if met in produced else False
            vect_dict['consumed'][met] = True if met in consumed else False
            vect_dict['imported'][met] = True if met in imported else False
            vect_dict['exported'][met] = True if met in exported else False
        return vect_dict

    def genotype_vector(self, env ):
        '''
        Construct boolean vector of gene-type presence-absence.

        Parameters
        ----------
        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment relative to which the gene type presence absence is determined

        Returns
        -------
        mapping of gene-function to
        :class:`VirtualMicrobes.event.Reaction.Reaction` |
        :class:`VirtualMicrobes.event.Molecule.MoleculeClass`s presence/absence.
        '''

        env_conversions, env_transports, env_met_classes = ( env.conversions,
                                                             env.transports,
                                                             env.molecule_classes )
        vect_dict = {'sensed':dict(), 'conversions':dict(), 'transports':dict()} # NOTE: unordered ok
        tf_sensed = self.tf_sensed
        conversions = self.conversions_type
        imports = self.importer_type
        exports = self.exporter_type
        for met in env_met_classes:
            vect_dict['sensed'][met] = True if met in tf_sensed else False
        for conv in env_conversions:
            vect_dict['conversions'][conv] = True if conv in conversions else False
        for transport in env_transports:
            vect_dict['transports'][(transport, 'i')] = True if transport in imports else False
        for transport in env_transports:
            vect_dict['transports'][(transport, 'e')] = True if transport in exports else False
        return vect_dict

    @property
    def genotype(self):
        '''
        Construct frozen set of the genotype classification of this cell.

        The genotype represents the gene functionality that the cell is capable
        of. It is expressed as the total set of transport, enzymatic and
        transcription sensing capabilities of the cell.

        Returns
        -------
        frozenset
        '''

        return frozenset( self.tf_sensed | self.conversions_type
                          | self.importer_type | self.exporter_type )

    @property
    def reaction_genotype(self):
        '''
        Construct frozen set of the reaction genotype classification of this cell.

        The genotype represents the enzyme functionality that the cell is
        capable of. It is expressed as the total set of transport, enzymatic
        capabilities of the cell, but excluding the tf sensing capabilities.

        Returns
        -------
        frozenset

        See Also
        --------
        func:`genotype`
        '''

        return frozenset( self.conversions_type | self.importer_type | self.exporter_type )

    ########################## \end stats ##########################

    @property
    def mean_life_time_toxicity(self):
        '''
        Average toxicity value over the life time of the individual.
        '''
        max_tp = self.nr_time_points_stored
        return np.mean(self.toxicity_time_course[:max_tp]) if max_tp else self.toxicity

    def get_toxicity_time_course(self):
        '''
        Time course of cell toxicity.
        '''
        max_tp = self.nr_time_points_stored
        return np.vstack((self.time_points[:max_tp],
                          self.toxicity_time_course[:max_tp]))

    @property
    def mean_life_time_production(self):
        '''
        Average production value over the life time of the individual.
        '''
        max_tp = self.nr_time_points_stored
        return np.mean(self.raw_production_time_course[:max_tp]) if max_tp else self.raw_production

    def get_raw_production_time_course(self):
        '''
        Time course of raw production value.
        '''
        max_tp = self.nr_time_points_stored
        return np.vstack((self.time_points[:max_tp],
                          self.raw_production_time_course[:max_tp]))

    @property
    def mean_life_time_pos_production(self):
        '''
        Average positive production value over the life time of the individual.
        '''
        max_tp = self.nr_time_points_stored
        return np.mean(self.pos_prod_time_course[:max_tp]) if max_tp else self.pos_production

    def get_pos_prod_time_course(self):
        '''
        Time course of positive component of production rate.
        '''
        max_tp = self.nr_time_points_stored
        return np.vstack((self.time_points[:max_tp],
                          self.pos_prod_time_course[:max_tp]))

    def get_time_points(self):
        '''
        Array of (data) time points stored.
        '''
        max_tp = self.nr_time_points_stored
        return self.time_points[:max_tp]

    @property
    def mean_life_time_cell_size(self):
        '''
        Average cell size over the life time of the individual.
        '''
        max_tp = self.nr_time_points_stored
        return np.mean(self.cell_size_time_course[:max_tp]) if max_tp else self.volume

    def get_cell_size_time_course(self):
        '''
        Time course of cell size.
        '''
        max_tp = self.nr_time_points_stored
        return np.vstack((self.time_points[:max_tp],
                          self.cell_size_time_course[:max_tp]))

    def get_total_reaction_type_time_course_dict(self):
        '''
        Return a dictionary of summed time courses per reaction type.

        Gets the time courses per gene type and then sums concentrations of gene
        products with the same reaction (enzymes/pumps) or ligand (tfs).
        '''
        per_type = self.get_gene_type_time_course_dict()
        reac_tc_dict = dict()
        for _type, d in per_type.items():
            per_reaction = collections.defaultdict(list)
            for p, tc in d.items():
                if _type == 'enzymes':
                    per_reaction[p.reaction].append(tc)
                elif _type == 'pumps':
                    per_reaction[(p.reaction, p['exporting'])].append(tc)
                elif _type == 'tfs':
                    per_reaction[p.ligand_class].append(tc)
            for r, tcs in per_reaction.items():
                prot_tcs = np.vstack( tc[1] for tc in tcs)
                per_reaction[r] = np.vstack((self.get_time_points(),np.nansum(prot_tcs, axis=0)))
            reac_tc_dict[_type] = per_reaction
        return reac_tc_dict


    def get_gene_type_time_course_dict(self):
        '''
        Return a dictionary of concentration time course data for different gene types.
        '''
        gt_tc_dict = dict([('enzymes', dict()), ('tfs', dict()), ('pumps', dict())]) # NOTE: unordered ok
        for g, tc in self.get_gene_time_course_dict().items():
            if g['type'] == 'enz':
                gt_tc_dict['enzymes'][g] = tc
            elif g['type'] == 'tf':
                gt_tc_dict['tfs'][g] = tc
            elif g['type'] == 'pump':
                gt_tc_dict['pumps'][g] = tc
            else:
                raise Exception("Gene type not recognized")
        return gt_tc_dict

    def get_mol_concentration_dict(self):
        '''
        Mapping of internal molecule species to current concentrations.
        '''
        return dict([ (mol, self.get_small_mol_conc(mol))
                     for mol in self.small_mols] )

    def get_mol_time_course_dict(self):
        '''
        Mapping of internal molecule species to concentration time course.
        '''
        max_tp = self.nr_time_points_stored
        return dict([ (mol, np.vstack((self.time_points[:max_tp],
                                       self.molecules['small_molecules'][mol].time_course[:max_tp])))
                     for mol in self.small_mols] )

    def get_mol_diffusion_dict(self):
        '''
        Mapping of internal molecule species to diffusion rates.
        '''
        return dict([ (mol, self.molecules['small_molecules'][mol].diffusion)
                     for mol in self.small_mols] )

    def get_mol_degradation_dict(self):
        '''
        Mapping of internal molecule species to degradation rates.
        '''
        return dict([ (mol, self.molecules['small_molecules'][mol].degradation)
                     for mol in self.small_mols] )

    def get_gene_multiplicities_dict(self):
        '''
        Mapping of gene products to copy numbers in the genome.
        '''
        return dict([ (mol, self.molecules['gene_products'][mol].multiplicity)
                     for mol in self.gene_products ] )

    def get_gene_concentration_dict(self):
        '''
        Mapping of gene products to current concentration.
        '''
        return dict([ (gene, self.get_gene_prod_conc(gene))
                     for gene in self.gene_products] )

    def get_gene_time_course_dict(self):
        '''
        Fetches time courses for gene products (proteins)

        Returns
        -------
            dictionary of all time courses
        '''
        max_tp = self.nr_time_points_stored
        return dict([(gene, np.vstack((self.time_points[:max_tp],
                                       self.molecules['gene_products'][gene].time_course[:max_tp] )))
                     for gene in self.gene_products])

    def get_gene_diffusion_dict(self):
        '''
        Mapping of gene products to diffusion rates.
        '''
        return dict([ (mol, self.molecules['gene_products'][mol].diffusion)
                     for mol in self.gene_products] )

    def get_gene_degradation_dict(self):
        '''
        Mapping of gene products to degradation rates.
        '''
        return dict([ (mol, self.molecules['gene_products'][mol].degradation)
                     for mol in self.gene_products] )

    def _get_building_blocks(self):
        return sorted([ mol for mol in self.small_mols
                       if mol.is_building_block ], key=lambda x: x.name)

    def init_mutations_dict(self):
        '''
        Initialize a dictionary for storing the mutations in the life time of this cell.
        '''
        self.mutations = make_mutations_dict()
        self.inherited_hgt = make_inherited_hgt_dict()

    def init_mol_views(self):
        '''
        Initialize 'aliases' for the set of small molecules and that of gene products in the cell.
        '''
        self.small_mols, self.gene_products = (self.molecules['small_molecules'].viewkeys(),
                                               self.molecules['gene_products'].viewkeys())

    def nodes_edges(self, genes=None):
        '''
        Returns a list of nodes and edges of the individual's gene regulatory
        network.

        Nodes are simply all the genes. Edges are TF binding site to operator
        interactions between genes in the nodes list.

        Parameters
        ----------
        genes : list of :class:`VirtualMicrobes.virtual_cell.Gene.Gene`s
            genes for which to find nodes and edges. If None (default) all gene products in the cell
            that have copy nr > 0.

        Returns
        -------
        nodes(list),edges(list of tuples)
        '''

        if genes is None:
            genes = [ g for g in self.gene_products if self.molecules['gene_products'][g].multiplicity  > 0 ]
        nodes = [ (g, self.molecules['gene_products'][g].multiplicity) for g in genes]
        op_to_tfs_scores_dict = self.genome.op_to_tfs_scores_dict()
        edges = [ (tf, g) for g in genes for (tf,_score) in op_to_tfs_scores_dict[g.operator] ]
        return nodes,edges

    def GRN(self, genes=None, prot_color_func=lambda x: None,
            with_gene_refs=False, with_self_marker=False):
        '''
        Make Gene Regulatory Network representation of the regulated genome.

        First, the lists of nodes and edges is generated for the given genes.
        Then, nodes are added to a Directed Graph (networkx.DiGraph) object with
        attributes that distinguish the gene type and other characteristics.
        Finally, edges are added with attributes that indicate e.g. binding
        strength.

        Returns
        -------
        networkx.Digraph
        '''
        nodes, edges = self.nodes_edges(genes)
        id_gen = itertools.count()
        simple_dict = dict([(n[0].id, id_gen.next()) for n in nodes])
        G = nx.DiGraph() #graph={'overlap':'false','nodesep':'100', 'ranksep':100},
                            #node={'size':300})
        nx.set_node_attributes(G, 'color', 'blue')
        def gene_node_label(gene_node_id):
            return gene_node_id.strip("_").split('.')[0]

        for g, copy_nr in nodes:
            gene_node_id = simple_dict[g.id]
            G.add_node(gene_node_id,# size=30, #str(g.id).replace('.', '_')
                       color=prot_color_func(g),
                       copynr=copy_nr,
                       type=g['type'],
                       typeLabel=g.simple_str(),
                       label=gene_node_label(str(g.id)),
                       gene=g if with_gene_refs else None
                       )
            if g['type'] == 'pump':
                G.node[gene_node_id]['exporting'] = g['exporting']

        for tf, g in edges:
            tf_gene_node_id = simple_dict[tf.id]
            gene_node_id = simple_dict[g.id]
            G.add_edge(tf_gene_node_id, gene_node_id, #.replace('.','_'), str(g.id).replace('.','_')
                             {'effect':math.log(tf['eff_bound'],10),
                             'effectApo':math.log(tf['eff_apo'],10),
                             'strength':tf.promoter.strength})# * abs(tf['eff_bound']))
        if with_self_marker:
            G.add_node('self', marker=self.marker_dict['lineage'])
        return G

    def _check_gene_multiplicities(self): # NOTE: test not currently used
        for gene, mol_dict in self.molecules["gene_products"].items():
            gene_count = 0
            for chrom in self.genome.chromosomes:
                for g in chrom.positions:
                    if g == gene:
                        gene_count += 1
            if mol_dict.multiplicity != gene_count:
                raise Exception(" ".join(["gene_count:", str(gene_count), "is not multiplicity",
                                         str(mol_dict.multiplicity),
                                "for gene", str(gene), "with dict", str(mol_dict)]))
        for gene in set(self.genome):
            if gene not in self.molecules["gene_products"]:
                raise Exception('gene {} not in molecular products'.format(gene))

    def reproduce(self, spent_production, time, second_parent=None):
        '''
        Create a new child of this cell.

        Copies all relevant properties, including the genome.
        Divides the original cell volume between the parent and child.

        Parameters
        ----------
        spent_production : float
            amount of the production variable spent for reproduction
        time : int
            simulation time point
        second_parent : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            an (optional) second parent that contributes to reproduction

        Returns
        -------
        :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
        '''
        self.raw_production -= spent_production
        assert(self.raw_production >= 0)
        child = None
        if second_parent is None:
            child = self.asexual(time)
        else:
            child = self.hybridize(second_parent)
        if child is None:
            raise Exception('reproduction failed, child is None')
        child.time_birth = time
        child.iterage = self.iterage + 1
        if self.params.divide_cell_content:
            child._divide_concentrations()
            self._divide_concentrations()
        if self.params.cell_division_volume is not None:
            self.divide_volume()
            self.divided = True
            child.divide_volume()
        #self.raw_production /= 2.
        child.raw_production = self.raw_production
        child.alive = True
        return child

    def clone(self, time):
        '''
        Make a clone of this cell.

        Clones are identical, having no mutations, and maintain a reference to
        the parent.

        Parameters
        ----------
        time : int
            simulation time point

        Returns
        -------
        :class:`VirtualMicrobes.virtual_cell.Cell`
        '''
        clone = self.asexual(time)
        clone.time_birth = time
        return clone

    def asexual(self, time):
        '''
        Asexual reproduction.

        Parameters
        ----------
        time : int
            simulation time point

        Returns
        -------
        :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
        '''
        self.set_mol_concentrations_from_time_point()
        return self._reproduction_copy(time)

    def hybridize(self, second_parent, time):
        raise NotImplementedError("Hybridization has not been defined yet.")

    def divide_volume(self, factor=2.):
        '''
        Divide the volume of the cell.

        Parameters
        ----------
        factor : float
            division factor
        '''
        self.volume /= factor

    def _divide_concentrations(self, factor=2.):
        '''
        Divide all molecule concentrations by a factor.

        Parameters
        ----------
        factor : float
            factor to divide by
        '''

        for mol in self.small_mols:
            conc = self.get_small_mol_conc(mol)
            self.set_small_mol_conc(mol, conc/factor)
        for gene_prod in self.gene_products:
            conc = self.get_gene_prod_conc(gene_prod)
            self.set_gene_prod_conc(gene_prod, conc/factor)

    def die(self, time, verbose=False, clear_time_courses=False, wiped=False):
        '''
        Cell death.

        Informs genomic units of cell death.

        Parameters
        ----------
        time : float
            simulation time point
        verbose : mol : :class:`VirtualMicrobes.event.Molecule.Molecule`
            metabolitebool
            report on cell death
        clear_time_courses : bool
            set time courses to None
        wiped : bool
            set if cell death was due to wiping of (a fraction of) the population
        '''
        if clear_time_courses: # clears time course data to limit memory usage
            self.clear_mol_time_courses()
        else:
            self.truncate_time_courses()
        super(Cell, self).die(time=time)
        self.genome.die(time)
        if wiped:
            self.wiped = True
        if verbose:
            print self.id, ': "I died." raw death was', self.raw_death_rate

    def prune_dead_phylo_branches(self):
        '''
        Prune branches of phylogenetic trees of all phylogenetically tracked
        entities.

        Recursively, prunes phylogenetic branches of this individual if it is
        not alive. Also prunes phylogenies of phylogenetic entities in the
        genome.

        Returns
        -------
        pruned cells (set), pruned chromosomes (set), pruned genes (set)
        '''
        pruned_cells = super(Cell, self).prune_dead_branch()
        pruned_chromosomes, pruned_genes = self.genome.prune_genomic_ancestries()
        return pruned_cells, pruned_chromosomes, pruned_genes

    def add_small_molecules(self, env, conc, degr_const,
                            ene_degr_const, bb_degr_const):
        '''
        Add the metabolites in the environment as internal variables to this
        individual.

        Set a membraned diffusion rate and degradation rate for the molecules.
        Diffusion rates come from a dictionary of the environment. Degradation
        rates also come from a dictionary in the environment, but may be
        scaled with an 'internal' `degr_const` parameter to cause degradation
        rates to be different inside and outside of the cell.

        Parameters
        ----------
        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment containing metabolites
        conc : float
            start concentration of all metabolites
        degr_const : float
            degradation constant of metabolites
        ene_degr_const : float
            degradation constant of energy metabolites
        bb_degr_const : float
            degradation constant of building block metabolites
        '''

        for mol in env.internal_molecules:
            diff_rate = env.membrane_diffusion_dict[mol.paired]
            degr_rate = self.scale_mol_degr_rate(mol, env, degr_const,
                                                 ene_degr_const, bb_degr_const)
            self.add_small_molecule(mol, env, conc, diff_rate, degr_rate)

    def update_small_molecules(self, env, conc):
        '''
        Used when a new molecule enters the game
        '''
        verbal = False
        for mol in env.internal_molecules:
            if mol in self.molecules['small_molecules'].keys():
                continue
            else:
                if verbal: print mol.name + ' not yet in the cell, adding it with concentration of ' + str(conc)
            diff_rate = env.membrane_diffusion_dict[mol.paired]
            degr_rate = env.degradation_dict[mol.paired]
            self.add_small_molecule(mol, env, conc, diff_rate, degr_rate)

    def add_small_molecule(self, mol, env, concentration, diff_const, degr_const):
        '''
        Add a metabolite to the internal Cell molecules and set its state.

        Parameters
        ----------
        mol : :class:`VirtualMicrobes.event.Molecule.Molecule`
            metabolite to be added to this Cell
        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment containing metabolites
        conc : float
            start concentration of this metabolite
        diff_const : float
            diffusion constant of this metabolite
        degr_const : float
            degradation constant of this metabolite
        '''
        self.set_small_mol_diff(mol, env.diffusion_reactions[mol], diff_const)
        self.set_small_mol_degr(mol,  env.degradation_reactions[mol],  degr_const)
        self.init_mol_time_course(self.molecules["small_molecules"][mol])
        self.set_small_mol_conc(mol, concentration)

    def set_small_mol_diff(self, mol, reac, rate):
        '''
        Set metabolite diffusion parameter.

        Parameters
        ----------
        mol : :class:`VirtualMicrobes.event.Molecule.Molecule`
            metabolite
        reac : :class:`VirtualMicrobes.event.Reaction.Diffusion`
            diffusion reaction
        rate : float
            diffusion rate of this metabolite
        '''
        self.molecules['small_molecules'][mol].diffusion =  reac, rate

    def set_small_mol_degr(self, mol, reac, rate):
        '''
        Set metabolite degradation parameter.

        Parameters
        ----------
        mol : :class:`VirtualMicrobes.event.Molecule.Molecule`
            metabolite
        reac : :class:`VirtualMicrobes.event.Reaction.Degradation`
            degradation reaction
        rate : float
            degradation rate of this metabolite
        '''
        self.molecules['small_molecules'][mol].degradation =  reac, rate

    def scale_mol_degr_rate(self, mol, env, degr_const,
                            ene_degr_const, bb_degr_const):
        '''
        Return scaled internal rate of metabolite degradation, relative to its
        external rate.

        The base rate is the metabolite specific external degradation rate. If
        internal rates have been chosen (not None), the base rate will be scaled
        with the ratio of internal/external. Rates can be different for building
        block and energy metabolites.

        Parameters
        ----------
        mol : :class:`VirtualMicrobes.event.Molecule.Molecule`
            metabolite
        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment containing metabolites
        degr_const : float
            degradation constant of metabolites that are not bbs or energy
        ene_degr_const : float
            degradation constant of energy metabolites
        ene_degr_const : float
            degradation constant of building block metabolites

        Returns
        -------
        scaled degradation rate (float)
        '''
        degr_rate = env.degradation_dict[mol.paired]
        if mol.is_energy:
            if ene_degr_const is not None:
                degr_rate *= ene_degr_const / self.params.ene_ext_degr_const
        elif mol.is_building_block:
            if bb_degr_const is not None:
                degr_rate *= bb_degr_const / self.params.bb_ext_degr_const
        else:
            if degr_const is not None:
                degr_rate *= degr_const / self.params.small_mol_ext_degr_const
        return degr_rate

    def update_small_molecules_diff(self, env):
        '''
        Update membrane diffusion parameter of metabolites.

        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment containing reactions and membrane diffusion rates.
        '''
        for mol in env.internal_molecules:
            self.set_small_mol_diff(mol, env.diffusion_reactions[mol],
                                    env.membrane_diffusion_dict[mol.paired])

    def update_small_molecules_degr(self, env, degr_const, ene_degr_const,
                                    bb_degr_const ):
        '''
        Update membrane degradation parameter of metabolites.

        env : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment containing reactions and base degradation rates.
        '''
        for mol in env.internal_molecules:
            degr_rate = self.scale_mol_degr_rate(mol, env, degr_const,
                                                 ene_degr_const, bb_degr_const)
            self.set_small_mol_degr(mol, env.degradation_reactions[mol],  degr_rate)

    def set_small_mol_conc(self, mol, conc):
        '''
        Set the new concentration of a metabolite.

        The last concentration time point will be overwritten.

        Parameters
        ----------
        mol : :class:`VirtualMicrobes.event.Molecule.Molecule`
            metabolite
        conc : float
            new concentration
        '''

        if self.tp_index is not None:
            self.molecules['small_molecules'][mol].time_course[self.tp_index] = conc
        self.molecules['small_molecules'][mol].concentration = conc

    def set_gene_prod_conc(self, gene, conc):
        '''
        Set the new concentration of a gene product.

        The last concentration time point will be overwritten.

        Parameters
        ----------
        gene : :class:`VirtualMicrobes.virtual_cell.Gene.Gene`
            gene product
        conc : float
            new concentration
        '''
        if self.tp_index is not None:
            self.molecules['gene_products'][gene].time_course[self.tp_index] = conc
        self.molecules['gene_products'][gene].concentration = conc

    def get_small_mol_conc(self, mol):
        '''
        Get current metabolite concentration.

        Parameters
        ----------
        mol : :class:`VirtualMicrobes.event.Molecule.Molecule`
            metabolite

        Returns
        -------
        concentration value (float)
        '''
        if self.tp_index is not None:
            return self.molecules['small_molecules'][mol].time_course[self.tp_index]
        else:
            return self.molecules['small_molecules'][mol].concentration

    def get_total_expression_level(self, reaction, exporting=False):
        '''
        Get total expression of a certain type of reaction

        Parameters
        ----------
        reaction: :class:`VirtualMicrobes.event.Reaction`
                                or
                  :class:`VirtualMicrobes.event.MoleculeClass`
            reaction or moleculeclass for TFs
        exporting: :bool:
            whether pump is exporting
        Returns
        -------
        concentration valule (float)
        '''
        sumexpr = 0.0
        for gene in self.molecules['gene_products'].keys():
            if hasattr(gene, 'reaction'):
                if gene.reaction == reaction:
                    if gene.params["type"] == 'pump':
                        if gene.params["exporting"] == exporting:
                            sumexpr += self.molecules['gene_products'][gene].concentration * self.volume
                    elif gene.params["type"] == 'enz':
                        sumexpr += self.molecules['gene_products'][gene].concentration * self.volume
        return sumexpr

    def get_gene_prod_conc(self, gene):
        '''
        Get current gene product concentration.

        Parameters
        ----------
        gene : :class:`VirtualMicrobes.virtual_cell.Gene.Gene`
            gene product

        Returns
        -------
        concentration value (float)
        '''
        if self.tp_index is not None:
            return self.molecules['gene_products'][gene].time_course[self.tp_index]
        else:
            return self.molecules['gene_products'][gene].concentration

    @property
    def tp_index(self):
        '''
        Index of last time point stored.
        '''
        index = self.nr_time_points_stored - 1
        return index if index > -1 else None

    @property
    def raw_production(self):
        '''
        Current production value.
        '''
        if self.tp_index is not None:
            return self.raw_production_time_course[self.tp_index]
        else:
            return self._raw_production

    @raw_production.setter
    def raw_production(self,val):
        '''
        Sets current production value .
        '''
        self._raw_production = val
        if self.tp_index is not None:
            self.raw_production_time_course[self.tp_index] = val

    @property
    def raw_production_change_rate(self):
        '''
        Current production change rate value.
        '''
        if self.tp_index is not None:
            if self.tp_index == 0:
                return 0
            dt = self.time_points[self.tp_index] - self.time_points[0]
            dp = self.raw_production_time_course[self.tp_index] - self.raw_production_time_course[0]
            return dp/dt
        else:
            return self._raw_production_change_rate

    @raw_production_change_rate.setter
    def raw_production_change_rate(self, val):
        '''
        Sets current production change rate value.
        '''
        self._raw_production_change_rate = val

    @property
    def toxicity(self):
        '''
        Current toxicity value.
        '''
        if self.tp_index is not None:
            return self.toxicity_time_course[self.tp_index]
        else:
            return self._toxicity

    @toxicity.setter
    def toxicity(self, val):
        '''
        Sets current toxicity value.
        '''
        self._toxicity = val
        if self.tp_index is not None:
            self.toxicity_time_course[self.tp_index] = val

    @property
    def toxicity_change_rate(self):
        '''
        Current toxicity value change rate.
        '''
        if self.tp_index is not None:
            if self.tp_index == 0:
                return 0
            dt = self.time_points[self.tp_index] - self.time_points[0]
            dp = self.toxicity_time_course[self.tp_index] - self.toxicity_time_course[0]
            return dp/dt
        else:
            return self._toxicity_change_rate

    @toxicity_change_rate.setter
    def toxicity_change_rate(self, val):
        '''
        Sets current toxicity value change rate.
        '''
        self._toxicity_change_rate = val

    @property
    def pos_production(self):
        '''
        Current bruto production value.
        '''
        if self.tp_index is not None:
            return self.pos_prod_time_course[self.tp_index]
        else:
            return self._pos_production

    @pos_production.setter
    def pos_production(self, val):
        '''
        Sets current bruto production value.
        '''
        self._pos_production = val
        if self.tp_index is not None:
            self.pos_prod_time_course[self.tp_index] = val


    @property
    def volume(self):
        '''
        Current cell volume.
        '''
        if self.tp_index is not None:
            return self.cell_size_time_course[self.tp_index]
        else:
            return self._volume

    @volume.setter
    def volume(self, val):
        '''
        Sets current cell volume.
        '''
        self._volume = val
        if self.tp_index is not None:
            self.cell_size_time_course[self.tp_index] = val

    def set_state_from_ref_cell_tp(self, ref_cell, tp_index=0, verbose=False):
        '''
        Reset cell properties to the state of a reference cell at a chosen time
        point.

        Parameters
        ----------
        ref_cell : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            take values from this reference individual
        tp_index : int
            index of reference time point to take reset value
        verbose : bool
            verbosity flag
        '''
        self.toxicity = ref_cell.toxicity_time_course[tp_index]
        if verbose:
            print 'reseting toxicity to ', str(self.toxicity)
        self.volume = ref_cell.cell_size_time_course[tp_index]
        if verbose:
            print 'reseting volume to ', str(self.volume)
        self.raw_production = ref_cell.raw_production_time_course[tp_index]
        if verbose:
            print 'reseting raw_production to ', str(self.raw_production)
        for mol in self.small_mols:
            self.set_small_mol_conc(mol, ref_cell.molecules['small_molecules'][mol].time_course[tp_index])
            if verbose:
                print 'resetting mol ', mol, 'to', self.molecules['small_molecules'][mol].concentration
        for anc_g, cl_g in zip(ref_cell.gene_products, self.gene_products):
            self.set_gene_prod_conc(cl_g, ref_cell.molecules['gene_products'][anc_g].time_course[tp_index])
            if verbose:
                print 'resetting prod to', self.molecules['gene_products'][cl_g].concentration

    def set_mol_concentrations_from_time_point(self):
        '''
        Record cellular concentrations and values from time course arrays.

        During the integration step, for each molecule or other variable time
        course data is stored in an array. The position that was last filled is
        the new concentration. The value stored under index pos will be copied to
        a dedicated concentration or 'value' member.

        :param pos: position in array to
        '''
        for mol in self.small_mols:
            self.set_small_mol_conc(mol, self.get_small_mol_conc(mol))
        for gene_prod in self.gene_products:
            self.set_gene_prod_conc(gene_prod, self.get_gene_prod_conc(gene_prod))
        self.raw_production_change_rate = self.raw_production_change_rate
        self.raw_production = self.raw_production
        self.pos_production = self.pos_production
        self.toxicity_change_rate = self.toxicity_change_rate
        self.toxicity = self.toxicity
        self.volume = self.volume

    def init_cell_time_courses(self, length=None):
        '''
        Initialize arrays to hold time course data.

        Parameters
        ----------
        length : int
            initial length of array
        '''
        if length is None:
            length = self.max_time_course_length
        self.nr_time_points_stored = 0
        self.time_points = util.time_course_array(length)
        self.raw_production_time_course = util.time_course_array(length)
        self.pos_prod_time_course = util.time_course_array(length)
        self.toxicity_time_course = util.time_course_array(length)
        self.cell_size_time_course = util.time_course_array(length)

    def init_mol_time_course(self, mol_struct, length=None):
        '''
        Initialize an array for time course data in a molecule structure SmallMol or GeneProduct.

        Parameters
        ----------
        mol_struct : :class:`VirtualMicrobes.my_tools.utility.SmallMol`
            simple c-struct like object that holds data on small molecules or gene products
        length : int
             initial length of time course array
        '''
        if length is None:
            length = len(self.time_points) #self.max_time_course_length
        mol_struct.time_course = util.time_course_array(length)

    def init_time_courses(self):
        '''
        Initialize arrays that hold time course data for molecules and cell variables
        '''
        self.init_cell_time_courses()
        for property_dict in self.molecules["small_molecules"].values():
            self.init_mol_time_course(property_dict)
        for property_dict in self.molecules["gene_products"].values():
            self.init_mol_time_course(property_dict)

    def resize_time_courses(self, new_max_time_points):
        '''
        Set a new size for arrays that hold time course data.

        Parameters
        ----------
        new_max_time_points : int
            max number of time points
        '''
        if new_max_time_points > self.max_time_course_length:
            self.max_time_course_length = new_max_time_points
            self.init_time_courses()

    def clear_mol_time_courses(self):
        '''
        Set time course arrays to None.

        Notes
        -----
        Reduces memory footprint of cell, for example before saving cell
        objects.
        '''
        for property_dict in self.molecules["small_molecules"].values():
            property_dict.time_course = None
        for property_dict in self.molecules["gene_products"].values():
            property_dict.time_course = None
        self.raw_production_time_course = None
        self.pos_prod_time_course = None
        self.toxicity_time_course = None
        self.cell_size_time_course = None

    def truncate_time_courses(self, max_tp=None):
        '''
        Truncate the time course data.

        If no maximum is supplied, truncates time courses to the parts of the
        arrays that have actually been filled with time points, discarding the
        empty last part of the array.

        Intended to be called when a cell dies and no additional data points
        are expected to be stored.

        Parameters
        ----------
        max_tp : int
            maximum number of time points retained
        '''
        if max_tp is None:
            max_tp = self.nr_time_points_stored
        for property_dict in self.molecules["small_molecules"].values():
            property_dict.time_course = property_dict.time_course[:max_tp]
        for property_dict in self.molecules["gene_products"].values():
            property_dict.time_course = property_dict.time_course[:max_tp]
        self.time_points = self.time_points[:max_tp]
        self.raw_production_time_course = self.raw_production_time_course[:max_tp]
        self.pos_prod_time_course = self.pos_prod_time_course[:max_tp]
        self.toxicity_time_course = self.toxicity_time_course[:max_tp]
        self.cell_size_time_course = self.cell_size_time_course[:max_tp]
        self.max_time_course_length = len(self.time_points)

    def grow_time_course_arrays(self, factor=1.5):
        '''
        Grow time course arrays if they cannot hold enough new time points.

        Parameters
        ----------
        factor : float
            increase capacity with this factor
        '''
        # check if there is a chance to overflow the array on the next run
        # if so: we will resize the array. If this happens, we should trigger
        # reinitializing of memoryviews in odes.pyx
        current_len = len(self.time_points)
        if self.nr_time_points_stored >= current_len/2:
            for property_dict in self.molecules["small_molecules"].values():
                property_dict.time_course = util.grow_array(property_dict.time_course, factor)
            for property_dict in self.molecules["gene_products"].values():
                property_dict.time_course = util.grow_array(property_dict.time_course, factor)

            self.time_points = util.grow_array(self.time_points, factor)
            self.raw_production_time_course = util.grow_array(self.raw_production_time_course, factor)
            self.pos_prod_time_course =util.grow_array(self.pos_prod_time_course, factor)
            self.toxicity_time_course =util.grow_array(self.toxicity_time_course, factor)
            self.cell_size_time_course = util.grow_array(self.cell_size_time_course, factor)
            self.arrays_changed = True
            return True

    def init_gene_products(self, concentration =None):
        '''
        Initialize gene products from the genes in the genome.

        Gene products have a concentration and degradation rate. ODE system
        integration will use the gene products as input variables.

        Parameters
        ----------
        concentration : float
            initial concentration of gene products
        '''


        if concentration is None:
            concentration=self.params.init_prot_mol_conc

        if isinstance(concentration,dict):
            for g in self.genome:
                self.add_gene_copy(g, concentration=concentration[g])
        else:
            for g in self.genome:
                self.add_gene_copy(g, concentration=concentration)

    def add_gene_product(self, gene, concentration =None):
        '''
        Initialize gene products from the genes in the genome.

        Gene products have a concentration and degradation rate. ODE system
        integration will use the gene products as input variables.

        Parameters
        ----------
        concentration : float
            initial concentration of gene products
        '''


        if concentration is None:
            concentration=self.params.init_prot_mol_conc

        if isinstance(concentration,dict):
            self.add_gene_copy(gene, concentration=concentration[gene])
            self.molecules["gene_products"][gene].multiplicity = 0
        else:
            self.add_gene_copy(gene, concentration=concentration)
            self.molecules["gene_products"][gene].multiplicity = 0

    def add_gene_copy(self, gene, concentration=0., diff_constant=None, degr_constant=None):
        '''
        Add gene product to the cell. If the 'gene' is already present as a key in the subdictionary,
        adding it again means we have to increase the multiplicity of the gene product, since there
        are multiple genes coding for this gene product. Otherwise, we add an entry for this gene product.

        Parameters
        ----------
        gene : :class:`VirtualMicrobes.virtual_cell.Gene.Gene`
            The gene for which copy number is increased.
        concentration : float
            Initial concentration of gene product.
        diff_constant : float
            Diffusion constant of gene product over the cell membrane. (If None, no diffusion is modeled)
        degr_constant : float
            Degradation constant of gene product.
        '''

        if diff_constant is None:
            diff_constant = self.params.prot_diff_const
        if degr_constant is None:
            degr_constant=self.params.prot_degr_const

        if gene in self.molecules["gene_products"]:
            self.molecules["gene_products"][gene].multiplicity += 1
        else:
            if diff_constant is not None:
                self.molecules["gene_products"][gene].diffusion = Diffusion(gene), diff_constant
            self.molecules["gene_products"][gene].degradation = Degradation(gene), degr_constant
            self.molecules["gene_products"][gene].multiplicity = 1
            self.init_mol_time_course(self.molecules["gene_products"][gene])
            self.set_gene_prod_conc(gene, concentration)

    def remove_unproduced_gene_products(self, conc_cutoff=None):
        '''
        Remove gene products when they are no longer produced and have a below
        threshold concentrations.

        Parameters
        ----------
        conc_cutoff : float
            threshold concentration below which gene product is removed

        Returns
        -------
        bool
            True if any product was removed
        '''
        if conc_cutoff is None:
            conc_cutoff = self.params.gene_product_conc_cutoff

        removed_gene_prod = False
        for gene_prod in self.gene_products:
            if ( self.molecules['gene_products'][gene_prod].multiplicity < 1 and
                self.get_gene_prod_conc(gene_prod) < conc_cutoff):
                    del self.molecules["gene_products"][gene_prod]
                    removed_gene_prod = True
        return removed_gene_prod

    def reduce_gene_copies(self, gene):
        '''
        Reduce the copy number for a gene.

        Parameters
        ----------
        gene : :class:`VirtualMicrobes.virtual_cell.Gene.Gene`
            The gene for which copy number is reduced.

        '''
        self.molecules["gene_products"][gene].multiplicity -= 1

    def update_mutated_gene_product(self, old, new):
        '''
        Decrease the copy number of the old gene and increase/initialize the new
        gene.

        Parameters
        ----------
        old : :class:`VirtualMicrobes.virtual_cell.Gene.Gene`
            pre mutation gene
        new : :class:`VirtualMicrobes.virtual_cell.Gene.Gene`
            post mutation gene
        '''
        self.add_gene_copy(new)
        self.reduce_gene_copies(old)
        self.genome.update_genome_removed_gene(old)


    def compute_product_toxicity(self, toxicity_func=None):
        # TODO: see if this can be refactored, calculating product tox in odes.pyx
        '''
        Set toxicity effect of product.
        '''
        if toxicity_func is None:
            toxicity_func = self.toxicity_func
        self.production_toxic_effect = toxicity_func(self.raw_production, self.params.product_toxicity)

    def calculate_raw_death_rate(self, base_rate, toxicity_scaling,
                                 toxic_effect_func=None):
        '''
        Raw death rate based on a base rate and the toxic effects of internal
        molecule concentrations.

        Parameters
        ----------
        base_rate : float
            base death rate
        toxicity_scaling : float
            scaling constant for toxic effect
        toxic_effect_func : func
            calculates surplus death rate due to toxicity

        '''
        if toxic_effect_func is None:
            toxic_effect_func = self.toxic_effect_func
        # NOTE: test simple raw_death calculation
        self.compute_product_toxicity()
        self.raw_death_rate = toxic_effect_func(base_rate, self.toxicity +
                                                self.production_toxic_effect,
                                                toxicity_scaling )
        return self.raw_death_rate

    def tandem_duplicate_stretch(self, chrom, start_pos, end_pos, time, verbose=False):
        '''
        Duplicate a stretch of genes in the genome in place.

        The chromosome, start position and end position (exclusive) uniquely
        determine a sequence of genes that will be duplicated and inserted
        immediately behind the original stretch. A Mutation object will be
        returned.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            target chromosome
        start_pos : int
            position index of the start of the stretch
        end_pos : int
            position index of the end of the stretch
        time : int
            simulation time
        verbose : bool
            verbosity

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.TandemDuplication`
        '''
        tandem_dup = TandemDuplication(chrom, self.genome, start_pos, end_pos)
        if verbose:
            print 'duplicating stretch'
            print 'start_pos', start_pos, 'end_pos', end_pos
        tandem_dup.mutate(time)
        for g in tandem_dup.stretch:
            if verbose:
                print "adding", g
            self.add_gene_copy(g)
        self.mutations['stretch'].append(tandem_dup)
        return tandem_dup

    def delete_stretch(self, chrom, start_pos, end_pos, time, verbose=False):
        '''
        Delete a stretch of genes in the genome.

        The chromosome, start position and end position (exclusive) uniquely
        determine a sequence of genes that will be deleted. The copy number of
        gene products in the cell is reduced. A Mutation object will be
        returned.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            target chromosome
        start_pos : int
            position index of the start of the stretch
        end_pos : int
            position index of the end of the stretch
        time : int
            simulation time
        verbose : bool
            verbosity

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.StretchDeletion`
        '''
        stretch_del = StretchDeletion(chrom, self.genome, start_pos, end_pos)
        if verbose:
            print 'deleting stretch'
            print 'start_pos', start_pos, 'end_pos', end_pos
        stretch_del.mutate(time)
        for g in stretch_del.stretch:
            if verbose:
                print "removing", g
            self.reduce_gene_copies(g)
        self.mutations['stretch'].append(stretch_del)
        return stretch_del

    def invert_stretch(self, chrom, start_pos, end_pos, time, verbose=False):
        '''
        Invert a stretch of genes in the genome in place.

        The chromosome, start position and end position (exclusive) uniquely
        determine a sequence of genes that will be inverted. A Mutation object
        will be returned.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            target chromosome
        start_pos : int
            position index of the start of the stretch
        end_pos : int
            position index of the end of the stretch
        time : int
            simulation time
        verbose : bool
            verbosity

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.Inversion`
        '''
        stretch_invert = Inversion(chrom, self.genome, start_pos, end_pos)
        if verbose:
            print 'inverting stretch'
            print 'start_pos', start_pos, 'end_pos', end_pos
        stretch_invert.mutate(time)
        self.mutations['stretch'].append(stretch_invert)
        return stretch_invert

    def insert_stretch(self, chrom, insert_pos, stretch, time, is_external, verbose=False):
        '''
        Insert a stretch of exogenous genomic material.
        Also adds product to the dict of to proteins made by the cell
        '''
        insertion = Insertion(chrom, self.genome, stretch, insert_pos, is_external)
        if verbose:
            print 'inserting stretch'
            print 'insert_pos', insert_pos
        insertion.mutate(time)
        for g in insertion.stretch:
            if verbose:
                print 'adding', g
            self.add_gene_copy(g)
        self.mutations['stretch'].append(insertion)
        return insertion

    def translocate_stretch(self, chrom, start_pos, end_pos, target_chrom,
                            insert_pos, invert, time, verbose=False):
        '''
        Translocate a stretch of genes in the genome in place.

        The chromosome, start position and end position (exclusive) uniquely
        determine a sequence of genes that will be excised and inserted at a new
        position in target chromosome. A Mutation object will be returned.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            chromosome with the original stretch
        start_pos : int
            position index of the start of the stretch
        end_pos : int
            position index of the end of the stretch
        target_chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            target chromosome for insertion
        insert_pos : int
            position index where stretch will be inserted
        time : int
            simulation time
        verbose : bool
            verbosity

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.Translocation`
        '''
        stretch_translocate = Translocation(chrom, self.genome, start_pos, end_pos,
                                            target_chrom, insert_pos, invert)
        if verbose:
            print 'translocating stretch'
            print 'start_pos', start_pos, 'end_pos', end_pos, 'insert_pos', insert_pos
        stretch_translocate.mutate(time)
        self.mutations['stretch'].append(stretch_translocate)
        return stretch_translocate

    def duplicate_chromosome(self, chrom, time):
        '''
        Chromosome duplication.

        Creates a mutation object that is then responsible for calling the
        appropriate genomic operations (duplication methods in chromosome and
        genome updation functions of genome. The Cell then updates its gene
        product counts accordingly.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            chromosome to be duplicated
        time : int
            simulation time

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.ChromosomeDuplication`
        '''
        dup = ChromosomeDuplication(chrom, self.genome)
        dup.mutate(time)
        for g in chrom.positions:
            self.add_gene_copy(g)
        self.mutations['chromosomal'].append(dup)
        return dup

    def delete_chromosome(self, chrom, time):
        '''
        Chromosome deletion.

        Creates a mutation object that is then responsible for calling the
        appropriate genomic operations (deletion methods of chromosome and
        genome updation functions of genome. The Cell then updates its gene
        product counts accordingly.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            chromosome to be deleted
        time : int
            simulation time

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.ChromosomeDeletion`
        '''
        deletion = ChromosomeDeletion(chrom, self.genome)
        deletion.mutate(time)
        for g in chrom.positions:
            self.reduce_gene_copies(g)
        self.mutations['chromosomal'].append(deletion)
        return deletion

    def fuse_chromosomes(self, chrom1, chrom2, end1, end2, time):
        '''
        Fusion of two chromosomes.

        Two chromosomes are fused end to end. The new product replaces the
        original two chromosomes in the genome.

        chrom1 : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            first chromosome to be fused
        chrom2 : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            second chromosome to be fused
        end1 : bool
            indicate end or start of the first chromosome will be fused
        end2 : bool
            indicate end or start of the second chromosome will be fused
        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.Fusion`
        '''
        fusion = Fusion(chrom1, chrom2, self.genome, end1, end2)
        fusion.mutate(time)
        self.mutations['chromosomal'].append(fusion)
        return fusion

    def fiss_chromosome(self, chrom, pos, time):
        '''
        Chromosome fission.

        Breaks apart a chromosome at a given position. The two resulting parts
        will become new chromosome replacing the original in the genome. Creates
        a mutation object that is then responsible for calling the appropriate
        genomic operations.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            chromosome to be broken
        pos : int
            position in chromosome of the break
        time : int
            simulation time

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.Fission`
        '''
        fission = Fission(chrom, self.genome, pos)
        fission.mutate(time)
        self.mutations['chromosomal'].append(fission)
        return fission

    def is_clone(self, ref_cell):
        '''
        Is clone

        Using string representation of genome to see if cells have the same genome

        Parameters
        ----------
        ref_cell : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`

        Returns
        -------
        bool
        '''
        if self == ref_cell: raise Exception("Comparing a cell with itself, are you sure that's your idea?")
        return str(ref_cell.genome) == str(self.genome)

    def hgt_external(self, hgt_rate, global_mut_mod, environment, time,
                     rand_gene_params, rand_gen):
        '''
        Insert a randomly generated (external) gene into the genome.

        Gene is created with random parameters and inserted (as a stretch) into
        a randomly picked chromosome and position.

        Parameters
        ----------
        hgt_rate : float
            probability external hgt
        global_mut_mod : float
            mutation scaling parameter of all mutation rates
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            simulation environment containing all possible reactions to draw a
            random gene for external HGT.
        time : int
            simulation time
        rand_gene_params : dict
            parameter space for properties of externally HGTed genes
        rand_gen : RNG

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.Insertion`
        '''
        if (rand_gen.uniform(0,1) > hgt_rate * global_mut_mod
            or not len(self.genome.chromosomes)):
            return
        hgt_gene = Gene.random_gene(environment, rand_gene_params, rand_gen,
                                    params=self.params, keep_transport_direction=False)
        stretch = [hgt_gene]
        chrom = rand_gen.choice(self.genome.chromosomes)
        insert_pos = rand_gen.randint(0, len(chrom)-1) if len(chrom) else 0
        prev_size = self.genome_size
        insertion = self.insert_stretch(chrom, insert_pos, stretch, time, is_external=True, verbose=False)
        assert self.genome_size == prev_size + len(stretch)
        return insertion

    def hgt_internal(self, hgt_rate, global_mut_mod, gp, time,
                     rand_gene_params, rand_gen):
        '''
        Insert a randomly chosen gene (stretch) from a neighboring individual
        into the genome.

        Potential donor individuals come from the neighbourhood of a focal grid
        point. Once a donor individual is selected, a random gene is chosen to
        be transferred to this individual.

        Parameters
        ----------
        hgt_rate : float
            probability external hgt
        global_mut_mod : float
            mutation scaling parameter of all mutation rates
        gp : :class:`VirtualMicrobes.environment.Grid.GridPoint`
            focal grid point to select donor individual
        time : int
            simulation time
        rand_gene_params : dict
            parameter space for properties of externally HGTed genes
        rand_gen : RNG

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.Insertion`
        '''

        # NOTE: we implemented as a 1 gene only HGT. Could later be changed to stretch HGT !!

        if (rand_gen.uniform(0,1) > hgt_rate * global_mut_mod or not len(self.genome.chromosomes) ):
            return

        potential_donors = []
        '''Taking a set ensures that we do not look at the same locality more than once due to grid wrapping.'''
        neighborhood_localities = orderedset.OrderedSet(gp.neighbors('hgt'))
        for locality in neighborhood_localities:
            potential_donors += locality.get_cells()
        '''Do not take "self" as a donor'''
        potential_donors = [ c for c in potential_donors if c != self ]
        if not len(potential_donors):
            return
        donor = rand_gen.choice(potential_donors)
        potential_chromosomes = [ chrom for chrom in donor.genome.chromosomes if len(chrom) > 0 ]
        if not len(potential_chromosomes):
            return
        donor_chrom = rand_gen.choice(potential_chromosomes)
        hgt_gene = rand_gen.choice(donor_chrom.positions)._hgt_copy(time)
        acceptor_chrom = rand_gen.choice(self.genome.chromosomes)
        insert_pos = rand_gen.randint(0, len(acceptor_chrom) - 1) if len(acceptor_chrom) else 0
        stretch = [hgt_gene]
        prev_size = self.genome_size
        insertion =  self.insert_stretch(acceptor_chrom, insert_pos, stretch, time, is_external=False, verbose=False)
        assert self.genome_size == prev_size + len(stretch)
        return insertion

    def point_mutate_gene_param(self, chrom, pos, param, mut_modifier,
                                environment, mutation_param_space,
                                rand_gene_params, time, rand_gen):
        '''
        Mutate a particular parameter of a gene at a particular position.

        A random new value is drawn for the parameter. Then the point mutation
        is initialized and applied. The Cell's gene products are updated to
        reflect the introduction of a new, mutated protein.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            chromosome that holds the gene
        pos : int
            position index of the gene to mutate
        param : str
            name of parameter to mutate
        mut_modifier : func
            function that from parameter value to new parameter value
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment holds Metabolites that can be potential ligands
        mutation_param_space : :class:`VirtualMicrobes.my_tools.utility.MutationParamSpace`
            parameter space and bounds for mutation effect
        rand_gene_params : :class:`VirtualMicrobes.my_tools.utility.ParamSpace`
            parameter space to draw new random parameter values
        time : int
            simulation time point that mutation is applied
        rand_gen : RNG

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.PointMutation`
        '''
        gene = chrom.positions[pos]
        new_val = None
        if param == "bind":
            change_magnitude = mut_modifier
            binding_sequence = gene.binding_sequence._mutation_copy()
            binding_sequence.mutate(rand_gen=rand_gen,
                                    change_magnitude=change_magnitude)
            new_val = binding_sequence
        elif param == "operator":
            change_magnitude = mut_modifier
            operator = gene.operator._mutation_copy()
            operator.mutate(rand_gen=rand_gen, change_magnitude=change_magnitude)
            new_val = operator
        elif param == 'promoter':
            promoter = gene.promoter._mutation_copy()
            promoter.strength = mut_modifier(promoter.strength, rand_gen,
                                             mutation_param_space)
            new_val = promoter
        elif param == 'exporting' or param == 'sense_external':
            new_val = mut_modifier(gene[param])
        elif param =='ligand_class':
            current = gene.ligand_class
            choices = list(environment.molecule_classes)
            choices.remove(current) # make sure we cannot select the old ligand_class
            new_class = rand_gen.choice(choices)
            new_ligand_ks_dict = Gene.init_molecule_ks(new_class, 1.)
            for l in new_ligand_ks_dict:
                new_ligand_ks_dict[l] = Gene.randomized_param(rand_gene_params,
                                                              rand_gen)
            new_val = new_class, new_ligand_ks_dict
        else:
            old_copy = deepcopy(gene[param])
            new_val = mut_modifier(old_copy, rand_gen,
                                   mutation_param_space)
        point_mut = PointMutation(gene, chrom, param, new_val, pos)
        point_mut.mutate(time)
        self.update_mutated_gene_product(point_mut.genomic_target,
                                         point_mut.post_mutation)
        return point_mut

    def point_mutate_gene(self, chrom, pos, mut_dict, point_mut_ratios,
                          environment, mutation_param_space, rand_gene_params,
                          time, rand_gen):
        '''
        Mutate a gene at a particular position of a chromosome.

        Depending on the 'type' of the gene, a different set of parameters may
        be mutated. One parameter of the gene randomly selected to be mutated,
        according to a weighted roulette wheel draw, with the probabilities
        given by the `point_mut_ratios` associated with each parameter. The
        selected parameter for the gene will be modified using a particular
        `mut_modifier` function for this parameter type. A
        :class:`VirtualMicrobes.mutate.Mutation.PointMutation` object is constructed that holds
        references to the original and mutated gene and the old and new
        parameter value, and allowing for reversal of the mutation operation.
        Finally, append the mutation in the Cell's list of single gene
        mutations.

        Parameters
        ----------
        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            chromosome that holds the gene to be mutated
        pos : int
            position index of the gene to mutate
        mut_dict : dict
            maps gene types to type specific parameter-> modifier-function mapping
        point_mut_ratios : dict
            mapping from parameter type to type specific relative mutation ratio
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment holds Metabolites that can be potential ligands
        mutation_param_space : :class:`VirtualMicrobes.my_tools.utility.MutationParamSpace`
            parameter space and bounds for mutation effect
        rand_gene_params : :class:`VirtualMicrobes.my_tools.utility.ParamSpace`
            parameter space to draw new random parameter values
        time : int
            simulation time point that mutation is applied
        rand_gen : RNG

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.PointMutation`
        '''
        gene = chrom.positions[pos]
        mutations_dict = mut_dict[gene["type"]]
        mut_probabilities = [ ((par,mut) , getattr(point_mut_ratios ,par) )
                             for (par,mut) in mutations_dict.items() ]
        (param, mut_modifier), _prob, _i = util.roulette_wheel_draw(mut_probabilities,
                                                                    rand_gen.uniform(0,1.) )
        point_mut = self.point_mutate_gene_param(chrom, pos, param,
                                                 mut_modifier, environment,
                                                 mutation_param_space,
                                                 rand_gene_params,
                                                 time, rand_gen)
        self.mutations['sg'].append(point_mut)
        return point_mut

    def point_mutate_genome(self, p_mutate, mut_dict, global_mut_mod,
                            point_mut_ratios, excluded_genes, environment,
                            mutation_param_space, rand_gene_params,
                            time, rand_gen):
        '''
        Apply point mutations to genes in the genome, according to point mutation rate.

        p_mutate : float
            point mutation probability
        mut_dict : dict
            maps gene types to type specific parameter-> modifier-function mapping
        global_mut_mod : float
            modifier for Cell wide mutation rate
        point_mut_ratios : dict
            mapping from parameter type to type specific relative mutation ratio
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment holds Metabolites that can be potential ligands
        mutation_param_space : :class:`VirtualMicrobes.my_tools.utility.MutationParamSpace`
            parameter space and bounds for mutation effect
        rand_gene_params : :class:`VirtualMicrobes.my_tools.utility.ParamSpace`
            parameter space to draw new random parameter values
        time : int
            simulation time point that mutation is applied
        rand_gen : RNG

        Returns
        -------
        list of mutations applied in this round
        '''
        if excluded_genes is None:
            excluded_genes = []
        mutations = []
        for chrom in self.genome.chromosomes:
            for pos in range(len(chrom.positions)):
                if chrom.positions[pos].params["type"] not in excluded_genes:
                    if rand_gen.uniform(0, 1) < p_mutate * global_mut_mod:
                        point_mut = self.point_mutate_gene(chrom, pos, mut_dict,
                                                       point_mut_ratios,
                                                       environment,
                                                       mutation_param_space,
                                                       rand_gene_params,time,
                                                       rand_gen)
                        mutations.append(point_mut)
        return mutations

    def regulatory_region_mutate(self, chrom, genome, pos, mut_dict,
                                      mut_ratios, stretch_exp_lambda,
                                      time, rand_gen, rand_gen_np):
        '''
        Mutate part of the sequence of a regulatory region of a gene.

        The mutation may be either a copying and translocation of an existing
        sequence somewhere in the genome to new position, or the insertion of a
        random sequence.

        chrom : :class:`VirtualMicrobes.virtual_cell.Chromosome.Chromosome`
            chromosome that holds the gene to be mutated
        genome : :class:`VirtualMicrobes.virtual_cell.Genome.Genome`
            full genome to find donor sequence
        pos : int
            position on chromosome of gene to be mutated
        mut_dict : dict
            maps gene types to type specific parameter-> modifier-function mapping
        mut_ratios : dict
            mapping from parameter type to type specific relative mutation ratio
        stretch_exp_lambda : float
            geometric distribution parameter that determines expected stretch length
        time : int
            simulation time
        rand_gen : RNG
        rand_gen_np : RNG
            numpy random number generator

        Returns
        -------
        :class:`VirtualMicrobes.mutation.Mutation.OperatorInsertion`
        '''
        gene = chrom.positions[pos]
        mutations_dict = mut_dict[gene["type"]]
        mut_probabilities = [ ((par,mut) , getattr(mut_ratios ,par) )
                             for (par,mut) in mutations_dict.items() ]
        (param, _mut_modifier), _prob, _i = util.roulette_wheel_draw(mut_probabilities,
                                                                     rand_gen.uniform(0,1.) )
        operator = gene.operator._mutation_copy()
        if param == 'translocate':
            # select donor chromosome with non-zero length
            donor_chrom = rand_gen.choice([ c for c in genome.chromosomes if len(c) ])
            # select donor gene
            donor_gene = rand_gen.choice(donor_chrom.positions)
            donor_sequence = list(donor_gene.operator.sequence)
            if rand_gen.choice([True,False]):
                # reverse donor sequence
                donor_sequence.reverse()
            start = rand_gen.randint(0,len(donor_sequence) - 1)
            ideal_stretch_len = rand_gen_np.geometric(stretch_exp_lambda)
            sequence_stretch = donor_sequence[start:start + ideal_stretch_len]
            insert_pos = rand_gen.randint(0,len(operator.sequence) - 1)
            # insert sequence
            operator.insert_mutate(insert_pos, sequence_stretch)
        elif param == 'random_insert':
            ideal_stretch_len = rand_gen_np.geometric(stretch_exp_lambda)
            insert_pos = rand_gen.randint(0,len(operator.sequence) - 1)
            sequence_stretch = operator.random_sequence(ideal_stretch_len, rand_gen)
            operator.insert_mutate(insert_pos, sequence_stretch)
        new_val = operator
        op_insert = OperatorInsertion(gene, chrom, new_val, pos)
        op_insert.mutate(time)
        self.update_mutated_gene_product(op_insert.genomic_target, op_insert.post_mutation)
        self.mutations['sg'].append(op_insert)
        return op_insert

    def regulatory_region_mutate_genome(self, mutation_rates, mut_dict,
                                        global_mut_mod, reg_mut_ratios,
                                        time, rand_gen, rand_gen_np):
        '''
        Apply regulatory region mutations to genes in the genome.

        mutation_rates : attr_dict
            dict with all mutation rates
        mut_dict : dict
            maps gene types to type specific parameter-> modifier-function mapping
        global_mut_mod : float
            modifier for Cell wide mutation rate
        reg_mut_ratios : dict
            mapping from parameter type to type specific relative mutation ratio
        time : int
            simulation time point that mutation is applied
        rand_gen : RNG
        rand_gen_np : RNG
            numpy random number generator

        Returns
        -------
        list of mutations applied in this round
        '''
        p_mutate = mutation_rates.regulatory_mutation
        stretch_exp_lambda = mutation_rates.reg_stretch_exp_lambda
        mutations = []
        for chrom in self.genome.chromosomes:
            for pos in range(len(chrom.positions)):
                if rand_gen.uniform(0, 1) < p_mutate * global_mut_mod:
                    regulatory_mut = self.regulatory_region_mutate(chrom, self.genome,
                                                                        pos, mut_dict,
                                                                        reg_mut_ratios,
                                                                        stretch_exp_lambda,
                                                                        time, rand_gen,
                                                                        rand_gen_np)
                    mutations.append(regulatory_mut)
        return mutations

    def stretch_mutate_genome(self, time, mutation_rates, global_mut_mod,
                              rand_gen, rand_gen_np,
                              mut_types = ['tandem_dup','stretch_del',
                                           'stretch_invert', 'stretch_translocate'],
                              verbose=False):
        '''
        Iterate over chromosomes and positions to select stretches of genes for
        mutational events.

        For every chromosome, iterate over positions and select front and end
        positions of stretch mutations. The direction of iteration is randomly
        chosen (back-to-front or front-to-back). Multiple mutations per
        chromosome may occur. Every position may be independently selected as
        the front site of a stretch mutation. The length of the stretch is a
        geometrically distributed random variable, using a lambda parameter. The
        end position is the minimum of the remaining chromosome length and the
        randomly drawn stretch length. If any positions remain in the chromosome
        after the stretch mutation, these positions are then iterated over in a
        random direction (direction of iteration is reversed at random after the
        application of the stretch mutation). Reversing direction is
        significant, because it randomizes the locations of 'truncated'
        stretches when reaching the end of a chromosome.

        Parameters
        ----------
        time : int
            simulation time
        mutation_rates : attr_dict
            dict with all mutation rates
        mut_dict : dict
            maps gene types to type specific parameter-> modifier-function mapping
        global_mut_mod : float
            modifier for Cell wide mutation rate
        rand_gen : RNG
        rand_gen_np : RNG
            numpy random number generator
        mut_types : list of str
            mutation types to apply
        '''
        mutation_dict = mutation_rates._asdict()
        prev_size = self.genome_size
        size_change = 0
        for chrom in self.genome.chromosomes:
            front, back = 0, len(chrom) # determine the (reversion-independent) front and back of chromosome
            while len(chrom) and front < back:
                positions = range(front, back + 1) # include a 'past-the-end' index
                reverse = rand_gen.choice([True, False])
                if reverse:
                    positions.reverse()
                positions_iter = iter(positions)
                mutated = False
                for pos in positions_iter:
                    if pos == positions[-1]: # we are past the end
                        break
                    potential_muts = []
                    for mut_type in mut_types:
                        if rand_gen.uniform(0,1) < mutation_dict[mut_type] * global_mut_mod:
                            potential_muts.append(mut_type)
                    if not potential_muts:
                        continue
                    mut_type = rand_gen.choice(potential_muts)
                    start_pos = pos
                    ideal_stretch_len = rand_gen_np.geometric(mutation_rates.stretch_exp_lambda)
                    end_pos = pos

                    if isinstance(chrom.positions, util.CircularList):
                        # stretch_len bounded by size of chromosome
                        ideal_stretch_len = min( len(chrom), ideal_stretch_len )
                        if reverse:
                            end_pos -= ideal_stretch_len
                        else:
                            end_pos += ideal_stretch_len
                    else:
                        #try to reach ideal stretch length and set end_pos
                        for _ in range(ideal_stretch_len):
                            try:
                                end_pos = positions_iter.next()
                            except StopIteration:
                                break
                        if end_pos == start_pos: # don't mutate when stretch length == 0
                            continue
                    if reverse: # reverse the chosen start and end position
                                # indices, because the
                                # actual mutation functions take positive stretches
                                # only ( start_pos < end_pos )
                        start_pos, end_pos = end_pos, start_pos

                    if mut_type == 'tandem_dup':
                        self.tandem_duplicate_stretch(chrom, start_pos, end_pos,
                                                      time, verbose=verbose)
                        size_change += end_pos - start_pos
                        if reverse:
                            back = start_pos - 1 # the back of the remainder of 'unseen' chromosome positions is 1 pos before
                            # the start of the selected stretch
                        else:
                            front = end_pos + (end_pos - start_pos)  # go beyond the inserted stretch copy
                    elif mut_type == 'stretch_del':
                        self.delete_stretch(chrom, start_pos, end_pos, time,
                                            verbose=verbose)
                        size_change -= end_pos - start_pos
                        if reverse:
                            back = start_pos -1 # see tandem_dup
                        else:
                            front = start_pos
                            back -= (end_pos - start_pos) # move the last chromosome position more frontal by the stretch length
                            # because that many positions were deleted
                    elif mut_type == 'stretch_invert':
                        self.invert_stretch(chrom, start_pos, end_pos, time,
                                            verbose=verbose)
                        if reverse:
                            back = start_pos -1 # see tandem_dup
                        else:
                            front = end_pos # inverted positions remain in chromosome, therefore front moves ahead 1 position
                    elif (mut_type == 'stretch_translocate'
                          and len(self.genome.chromosomes) > 1):
                        invert = rand_gen.choice([False, True])
                        target_chroms = self.genome.chromosomes[:]
                        target_chroms.remove(chrom)
                        target_chrom = rand_gen.choice(target_chroms)
                        insert_pos = rand_gen.randint(0, (len(target_chrom)))
                        self.translocate_stretch(chrom, start_pos, end_pos,
                                                  target_chrom, insert_pos,
                                                  invert, time, verbose=verbose)
                        if reverse:
                            back = start_pos -1 # see tandem_dup
                        else:
                            front = start_pos
                            back -= (end_pos - start_pos) # see stretch_del
                    mutated = True
                    break # break to restart mutation processes with new front and end vals
                if not mutated: # reached here by iterating to the end, so break
                    break
        assert self.genome_size == prev_size + size_change

    def chromosome_mutate_genome(self, time, mutation_rates, global_mut_mod,
                                 rand_gen, rand_gen_np, verbose):
        '''
        Apply chromosomal mutations to the genome.

        Each type of chromosome mutation is applied independently. When a
        mutation is selected, one or two random chromosomes are chosen for the
        mutation. The mutation method return a Mutation instance, that is appended
        to a list of chromosome mutations. This list is returned.

        Parameters
        ----------
        time : int
            simulation time
        mutation_rates : attr_dict
            dict with all mutation rates
        global_mut_mod : float
            modifier for Cell wide mutation rate
        rand_gen : RNG
        rand_gen_np : RNG
            numpy random number generator
        verbose : bool
            verbosity

        Returns
        -------
        list of Mutation objects
        '''
        chromosome_muts = []
        if (len(self.genome.chromosomes) and
            rand_gen.uniform(0, 1) < mutation_rates.chrom_dup * global_mut_mod):
            chrom = rand_gen.choice(self.genome.chromosomes)
            dup = self.duplicate_chromosome(chrom, time)
            chromosome_muts.append(dup)
        if (len(self.genome.chromosomes) and
            rand_gen.uniform(0, 1) < mutation_rates.chrom_del * global_mut_mod):
            chrom = rand_gen.choice(self.genome.chromosomes)
            dele = self.delete_chromosome(chrom, time)
            chromosome_muts.append(dele)
        if (len(self.genome.chromosomes) > 1 and
            rand_gen.uniform(0, 1) < mutation_rates.chrom_fuse * global_mut_mod):
            chrom1, chrom2 = rand_gen.sample(self.genome.chromosomes, 2)
            end1, end2 = rand_gen.randint(0, 1), rand_gen.randint(0, 1)
            fuse = self.fuse_chromosomes(chrom1, chrom2, end1, end2, time)
            chromosome_muts.append(fuse)
        if (len(self.genome.chromosomes) and
            rand_gen.uniform(0, 1) < mutation_rates.chrom_fiss * global_mut_mod):
            chrom = rand_gen.choice(self.genome.chromosomes)
            if len(chrom) > 1:
                if verbose:
                    print len(chrom), "positions in chromosome"
                pos = rand_gen.randint(1, len(chrom) - 2) if len(chrom) > 2 else 1
                fiss = self.fiss_chromosome(chrom, pos, time)
                chromosome_muts.append(fiss)
            else:
                if verbose:
                    print "no fission on chromosome with length", len(chrom)
        return chromosome_muts

    def mutate(self, time, environment, rand_gene_params=None,
               mutation_rates=None, mutation_param_space=None,
               global_mut_mod=None, excluded_genes=None,
               point_mutation_dict=None, point_mutation_ratios=None,
               regulatory_mutation_dict=None, regulatory_mutation_ratios=None,
               rand_gen=None, rand_gen_np=None, verbose=False):
        '''
        Apply mutations to the genome.

        In turn, chromosome mutations, gene stretch mutations, point mutations
        and regulatory region mutations are applied. Mutations happen with
        probabilities supplied in a mutation_rates dict. The parameter spaces
        of the different types of mutations are supplied in the `mutation_param_space`

        Parameters
        ----------
        time : int
            simulation time
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            environment holds Metabolites that can be potential ligands
        rand_gene_params : :class:`VirtualMicrobes.my_tools.utility.ParamSpace`
            parameter space to draw new random parameter values
        mutation_rates : attr_dict
            dict with all mutation rates
        mutation_param_space : :class:`VirtualMicrobes.my_tools.utility.MutationParamSpace`
            parameter space and bounds for mutation effect
        global_mut_mod : float
            modifier for Cell wide mutation rate
        point_mutation_dict : dict
            maps gene types to type specific parameter-> modifier-function mapping
        point_mutation_ratios : dict
            mapping from parameter type to type specific relative mutation ratio
        regulatory_mutation_dict : dict
            maps gene types to type specific parameter-> modifier-function mapping
        regulatory_mutation_ratios : dict
            mapping from parameter type to type specific relative mutation ratio
        rand_gen : RNG
        rand_gen_np : RNG
            numpy random number generator
        verbose : bool
            verbosity

        Returns
        -------
        list of mutations
        '''
        if mutation_param_space is None:
            mutation_param_space = self.params.mutation_param_space
        if mutation_rates is None:
            mutation_rates = self.params.mutation_rates
        if global_mut_mod is None:
            global_mut_mod = self.params.universal_mut_rate_scaling
        if point_mutation_ratios is None:
            point_mutation_ratios = self.params.point_mutation_ratios
        if point_mutation_dict is None:
            point_mutation_dict = self.params.point_mutation_dict
        if regulatory_mutation_ratios is None:
            regulatory_mutation_ratios = self.params.regulatory_mutation_ratios
        if regulatory_mutation_dict is None:
            regulatory_mutation_dict = self.params.regulatory_mutation_dict
        if rand_gene_params is None:
            rand_gene_params = self.params.rand_gene_params
        if excluded_genes is None:
            excluded_genes = self.params.exclude_gene_from_mutation

        if verbose:
            print "mutating cell", self.id
        self.chromosome_mutate_genome(time, mutation_rates, global_mut_mod,
                                      rand_gen, rand_gen_np, verbose)
        self.stretch_mutate_genome(time, mutation_rates, global_mut_mod,
                                   rand_gen, rand_gen_np)
        self.point_mutate_genome(mutation_rates.point_mutation,
                                 point_mutation_dict, global_mut_mod,
                                 point_mutation_ratios, excluded_genes, environment,
                                 mutation_param_space, rand_gene_params,
                                 time, rand_gen=rand_gen)
        self.regulatory_region_mutate_genome(mutation_rates,
                                             regulatory_mutation_dict,
                                             global_mut_mod,
                                             regulatory_mutation_ratios,
                                             time, rand_gen, rand_gen_np )
        self.update_grn()
        return self.mutations

    def apply_hgt(self, time, gp, environment, rand_gene_params=None,
               mutation_rates=None, global_mut_mod=None, rand_gen=None,
               verbose=False):
        '''
        Applies HGT to a cell, and updates the GRN.

        If applied HGT is applied, the gp updated flag is set to True, to inform
        integrator update in next timestep.

        Parameters
        ----------
        time : int
            time point in the simulation
        gp : :class:`VirtualMicrobes.environment.Grid.GridPoint`
            location of cell on the grid
        environment : :class:`VirtualMicrobes.environment.Environment.Environment`
            simulation environment containing all possible reactions to draw a
            random gene for external HGT
        rand_gene_params : dict
            parameter space for properties of externally HGTed genes
        mutation_rates : dict
            contains rates for eHGT and iHGT
        global_mut_mod : double
            scaling factor for all mutation rates
        rand_gen: RNG

        Returns
        -------
        The applied mutations are returned
        '''

        if mutation_rates is None:
            mutation_rates = self.params.mutation_rates
        if global_mut_mod is None:
            global_mut_mod = self.params.universal_mut_rate_scaling
        if rand_gene_params is None:
            rand_gene_params = self.params.rand_gene_params

        if verbose:
            print "\n\nApplying HGT for cell", self.id, '(before HGT)'

        applied = False
        if self.hgt_external(mutation_rates.external_hgt, global_mut_mod, environment,
                          time, rand_gene_params, rand_gen) is not None:
            applied = True
            self.update_grn()    # Recalculate GRN for permuted genome
            if verbose: print "Applied eHGT"
        if self.hgt_internal(mutation_rates.internal_hgt, global_mut_mod, gp,
                          time, rand_gene_params, rand_gen) is not None:
            applied = True
            self.update_grn()    # Recalculate GRN for permuted genome
            if verbose: print "Applied iHGT"
        return applied

    def get_ancestor(self, gen_back, verbose=False):
        for lod in self.lods_up(): # in theory, multiple lods exist for each cell, but just take the first..
            cells = list(lod)
            cells.reverse()
            for gen, parent in enumerate(cells):
                if gen > gen_back:
                    if verbose:
                        print 'Found '
                    return parent

    def get_ancestor_at_time(self, time):
        if time > self.time_birth:
            warnings.warn('Cannot retrieve ancestor from the future {}')
        for lod in self.lods_up(): # in theory, multiple lods exist for each cell, but just take the first..
            cells = list(lod)
            cells.reverse()
            for parent in cells:
                if parent.time_birth <= time:
                    return parent

    def delete_genes(self, genes, time):
        deleted = set()
        for chrom in self.genome.chromosomes:
            pos = 0
            while pos < len(chrom):
                gene = chrom.positions[pos]
                if gene in genes:
                    self.delete_stretch(chrom, pos, pos+1, time, verbose=True)
                    deleted.add(gene)
                else:
                    pos +=1
        self.update_grn()
        if set(genes) - deleted:
            warnings.warn('some genes could not be deleted')
            for gene in set(genes) - deleted:
                print gene


    @classmethod
    def __unique_id(cls, gen_id=None):
        '''
         a classmethod that should be called whenever a new 'unique' cell is created to
         increase the cell count. It returns this number so that the cell can acquire
         this unique id.

        :return int :
        :author
        '''
        if gen_id is None:
            gen_id = _gen_id_func
        cls.uid = gen_id(cls.uid)
        return cls.uid

    def __str__(self):
        out_str = "cell" + str(self.id) + ":\n" + str(self.genome)
        return out_str

    def _reproduction_add_gene_products(self, previous_mol_dict, orig_copy_genes_map):
        '''
        Add the reproduction copies of original genes back to the molecules dictionary.

        Puts new gene products in the `molecules` map that represent copies of
        the parental genes. If no copy was made a KeyError raised, meaning that
        the gene is no longer present in the genome (due to deletion or
        mutation), but the gene product is still present. In that case we use
        the original gene as a key for the mapping.

        Parameters
        ----------
        previous_mol_dict : dictionary of dictionaries
            Mapping from molecules/ genes to the gene products present in the cell.
        orig_copy_genes_map : dictionary
            Mapping from original genes to the copies resulting from copying the
            cell's :class:`VirtualMicrobes.virtual_cell.Genome.Genome`
        '''
        for gene_prod, mol_struct in previous_mol_dict["gene_products"].items():
            try:
                new_copy = orig_copy_genes_map[gene_prod]
                self.molecules["gene_products"][new_copy] = copy(mol_struct)
            except KeyError: # The gene is no longer in the genome, but the gene product is still
                # present in the cell
                self.molecules["gene_products"][gene_prod] = copy(mol_struct)

    def _reproduction_copy_molecule_dict(self):
        '''
        Copying of the molecule dictionary.

        The result should be a new
        independent dict, where the molecules used as keys are the exact same
        objects as in the parent's dictionary. In other words, it avoids making
        copies of the actual molecules used as keys to index the dict.

        Returns
        -------
        new internal molecule dictionary
        '''
        new_molecules = dict() # NOTE: unordered ok
        new_molecules["small_molecules"] = OrderedDefaultdict(SmallMol)
        new_molecules["gene_products"] = OrderedDefaultdict(GeneProduct)
        for mol, mol_struct  in self.molecules["small_molecules"].items():
            new_molecules["small_molecules"][mol] = copy(mol_struct)  # deepcopy(mol_struct)
        return new_molecules

    def _update_inherited_hgt(self, mut_dict):
        self.inherited_hgt['external'] += [ s for s in mut_dict['stretch']
                                          if isinstance(s, Insertion) and s.is_external ]
        self.inherited_hgt['internal'] += [ s for s in mut_dict['stretch']
                                          if isinstance(s, Insertion) and not s.is_external ]


    def _reproduction_copy(self, time):
        child = super(Cell, self)._copy(new_id=True, flat_id=True)
        for k, v in self.__dict__.items():
            if k in child.__dict__:
                continue  # taken care of by super call

            if k == "genome":
                new_genome = v._reproduction_copy(time)
                setattr(child, k, new_genome)
            elif k == "molecules":
                new_molecules = self._reproduction_copy_molecule_dict()
                setattr(child, k, new_molecules)
            elif k in ["mutations", 'production_toxic_effect']:
                # print "skpping copying of", k
                atr_cls = v.__class__
                setattr(child, k, atr_cls.__new__(atr_cls))
            elif k in ['params', 'init_rand_gen', 'toxicity_func', 'toxic_effect_func',
                        'product_toxicity_func', 'production_function',
                        'transcription_cost', 'energy_transcription_cost',
                        'energy_transcription_scaling', 'homeostatic_bb_scaling',
                        '_volume', 'max_volume', 'growth_rate','shrink_rate',
                        'growth_cost', 'energy_for_growth',
                         'v_max_growth', 'building_blocks_dict','energy_mols',
                         'iterage', 'max_time_course_length', 'version']:
                setattr(child, k, v)
            elif k in ["small_mols", "gene_products", '_raw_production',
                       '_raw_production_change_rate', '_pos_production',
                       '_toxicity', '_toxicity_change_rate', 'raw_death_rate',
                       'wiped', 'time_points', 'toxicity_time_course',
                       'raw_production_time_course', 'cell_size_time_course',
                       'pos_prod_time_course','arrays_changed',
                       'nr_time_points_stored', 'divided', 'inherited_hgt']:
                pass
            else:
                print "deep copying", k , "of cell", self.id
                setattr(child, k, deepcopy(v))
        child._reproduction_add_gene_products(self.molecules, child.genome.orig_copy_genes_map)
        child.init_mol_views()
        child.init_time_courses()
        child.init_mutations_dict()
        child._update_inherited_hgt(self.mutations)
        child.arrays_changed = False
        child.raw_production = 0.
        child.pos_production = 0.
        child.raw_production_change_rate = 0.
        child.toxicity = 0.
        child.toxicity_change_rate = 0.
        child.production_toxic_effect = 0.
        child.raw_death_rate = 0.
        child.wiped = False
        child.divided = False
        child.remove_unproduced_gene_products()
        return child

    def update(self, state):
        version = float(state.get('version', '0.0'))
        if version < 2.0:
            del state['nr_time_points_stored']
            self.nr_time_points_stored = 0

    def upgrade(self):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added.
        '''
        version = float(self.version)
        if version < 1.1:
            self.init_time_courses()
            self.pos_production = 0.
        if version < 2.0:
            self.divided = False
            self.arrays_changed = False
            for attr in ['cum_time_points', 'cum_toxicity_time_course',
                         'cum_raw_production_time_course',
                         'cum_cell_size_time_course', 'cum_pos_prod_time_course']:
                delattr(self, attr)
        if version < 2.1:
            self.homeostatic_bb_scaling = 0
        if version < 2.2:
            for tf in self.tfs:
                tf.params['binding_coop'] = 1
        if version < 2.3:
            self.inherited_hgt = make_inherited_hgt_dict()
        if version < 2.4:
            if not self.alive:
                self.truncate_time_courses()
        if version < 2.5:
            for tf in self.tfs:
                tf.params['ligand_coop'] = 1.
        if version < 2.6:
            self.toxic_effect_func = self.toxicity_effect_func
            try:
                del self.toxicity_effect_func
            except AttributeError:
                pass

        self.version = self.class_version
        #print 'upgraded class', self.__class__.__name__,
        #print 'from version', version ,'to version', self.version

    def __setstate__(self, state):
        self.update(state)
        super(Cell, self).__setstate__(state)
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()

    #===========================================================================
    # def __setstate__(self, obj_dict):
    #     self.__dict__ = obj_dict
    #     if not hasattr(self, 'version'):
    #         self.version = '0.0'
    #     if self.version != self.class_version:
    #         self.upgrade()
    #
    #===========================================================================
