from collections import defaultdict
import collections
import orderedset
import random

from VirtualMicrobes.Tree.PhyloTree import PhyloTree
import VirtualMicrobes.my_tools.utility as util
from VirtualMicrobes.virtual_cell.Cell import Cell
from VirtualMicrobes.virtual_cell.PhyloUnit import PhyloUnit
import itertools as it
import numpy as np


try:
    import bottleneck as bt # Optimised numpy functions
    np.nanmean = bt.nanmean
except ImportError:
    pass

class Population(object):
    class_version = '0.0'

    '''
    A population of individual Cells that reproduce and die during a Simulation.

    The class defines methods for life history events of the cell population:
        * death of individuals
        * competition and reproduction
        * population level gene exchange (HGT)

    Phylogenetic relationships between individuals in the
    population are tracked and a phylogenetic tree is maintained and pruned when
    individuals reproduce and die.

    Parameters
    ----------
    params : dict
        a dictionary of simulation parameters
    environment : :class:`VirtualMicrobes.environment.Environment`
        environment that is home to the population; determines molecular and reaction universe

    Attributes
    ----------
    params : dict
        reference of Simulation parameters
    historic_production_max : float
        historic maximum of production value in the population
    production_val_history : list of floats
        history of all population production maxima
    pop_rand_gen : RNG
        RNG for drawing population events
    evo_rand_gen : RNG
        RNG for drawing evolutionary events
    markers_range_dict : dict
        stores ranges for cell markers used in plotting
    value_range_dict : dict
        ranges of attributes on phylogenetic tree
    current_pop_size : int
        population size
    died : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s
        individuals that have died in the current simulation step
    cell_dict : dict
        mapping from :class:`VirtualMicrobes.virtual_cell.Cell.Cell` to attributes
    cells : view on keys
        the living :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s in the population
    new_offspring : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s
        individuals born in current time step
    pruned_cells : set of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s
        individuals that are dead and do not have living offspring
    current_ancestors : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s
        living individuals and ancestors that contribute offspring to current population
    roots : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s
        first common ancestors of current population
    phylo_tree : :class:`VirtualMicrobes.Tree.PhyloTree.PhyloTree`
        represent phylogenetic tree of current population
    pruned_cells : set of :class:`VirtualMicrobes.virtual_cell.PhyloUnit.PhyloUnit`
        cell phylo units to be pruned from global phylo dict
    pruned_chromosomes : set of :class:`VirtualMicrobes.virtual_cell.PhyloUnit.PhyloUnit`
        chromosome phylo units to be pruned from global phylo dict
    pruned_genes : set of :class:`VirtualMicrobes.virtual_cell.PhyloUnit.PhyloUnit`
        gene phylo units to be pruned from global phylo dict
    '''
    def __init__(self, params, environment):
        self.version = self.__class__.class_version
        self.params = params
        self.init_pop_rand_gen(self.params.pop_rand_seed)
        self.init_evo_rand_gens(self.params.evo_rand_seed)
        self.init_phylo_tree()
        self.init_pop(environment, self.params.init_pop_size, self.params)
        self.max_pop_size = self.params.max_cells_per_locality * len(environment.localities)
        self.historic_production_max = params.reset_historic_max
        self.production_val_history = []
        self.init_range_dicts()
        if not self.params.cells_from_files:
            self.mark_cells_lineage()

    def init_range_dicts(self):
        '''
        Initialise mappings used in colour coding individuals in graphical output.

        The `markers_range_dict` stores lower and upper bounds on discrete
        population statistics.

        The `metabolic_type_marker_dict` maps metabolic types to markers that
        are used for colour coding.

        The `value_range_dict` stores lower and upper limits on various celll
        properties that are represented on the phylogenetic tree.
        '''
        self.markers_range_dict = dict()  # NOTE: unordered ok
        self.markers_range_dict['metabolic_type'] = (0, self.max_pop_size * 2)
        self.markers_range_dict['lineage'] = (0, self.max_pop_size * 2)
        self.metabolic_type_marker_dict = util.ReusableIndexDict(fixed_length=self.max_pop_size * 2)
        self.value_range_dict = dict()  # NOTE: unordered ok

    def init_pop_rand_gen(self, pop_rand_seed=None):
        '''Initialise random generator for population events'''
        if pop_rand_seed is None:
            pop_rand_seed = self.params.pop_rand_seed
        self.pop_rand_gen = random.Random(int(pop_rand_seed))

    def init_evo_rand_gens(self, evo_rand_seed=None):
        '''Initialise random generator for evolutionary events'''
        if evo_rand_seed is None:
            evo_rand_seed = self.params.evo_rand_seed
        self.evo_rand_gen = random.Random(int(evo_rand_seed))
        self.evo_rand_gen_np = np.random.RandomState(int(evo_rand_seed))

    def init_pop(self, environment, pop_size = None, params_dict=None):
        '''
        Initialise the population.

        Population initialisation is determined by the set of simulation
        parameters available in the params_dict or the params stored during
        construction of the
        :class:`VirtualMicrobes.virtual_cell.Population.Population`. Several
        methods for creating a population are available:
            * a new population of unique individuals is created with randomised
            cell parameters.
            * individuals are initialised from a set of cell configuration
            files, describing their parameters
            * a population of identical clones is generated from a single
            randomly initialised individual.

        Initialise the phylogenetic tree.

        Parameters
        ----------
        environment : :class:`VirtualMicrobes.environment.Environment`
            environment that is home to the population; determines molecular and reaction universe
        pop_size : int, optional
            size of population
        params_dict : dict, optional
            a dictionary of simulation parameters

        Returns
        -------
        iterator of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` objects
            the newly created individuals
        '''

        if params_dict is None:
            params_dict = self.params
        if pop_size is None:
            pop_size = self.params.init_pop_size

        self.current_pop_size = 0
        self.cell_dict = collections.OrderedDict()
        self.init_cells_view()
        self.died = []
        self.new_offspring = []
        self.pruned_cells = set()
        if self.params.cells_from_files is not None:
            common_ancestors = self.cloned_pop_from_files(pop_size, environment)
            self.init_current_ancestors()
            self.init_roots(common_ancestors)
            for anc in common_ancestors:
                self.cell_death(anc, time=0)
        elif self.params.single_clone_init:
            common_ancestor = self.cloned_pop(pop_size, environment, params_dict)
            self.init_current_ancestors()
            self.init_roots([common_ancestor])
            self.cell_death(common_ancestor, time=0)
        else:
            self.unique_pop(pop_size, environment, params_dict)
            self.init_current_ancestors()
            self.init_roots()
        self.update_phylogeny(verbose=False)
        return self.cell_dict.keys()

    def unique_pop(self, pop_size, environment, params_dict ):
        '''
        Create population of unique, randomised individuals.

        Creates new class:`VirtualMicrobes.virtual_cell.Cell.Cell` individuals
        and initialises their genomes. Genome initialisation depends on the
        `environment`, because this determines the set of possible gene types and
        minimum viable metabolism that can be constructed.

        Parameters
        ----------
        pop_size : int
            population size
        environment : :class:`VirtualMicrobes.environment.Environment`
            environment that is home to the population; determines molecular and reaction universe
        params_dict : dict, optional
            a dictionary of simulation parameters

        Returns
        -------
        view keys of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` objects
            the newly created individuals
        '''
        for _ in range(pop_size):
            cell = Cell(params=params_dict, environment=environment,
                        rand_gen=self.pop_rand_gen, time_birth=-1)
            cell.init_genome(environment)
            self.add_cell(cell)
        return self.cells

    def cloned_pop(self, pop_size, environment, params_dict, time=0):
        '''
        Creates a single ancestor :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
        individual and initialises its genomes. Genome initialisation depends on
        the `environment`, because this determines the set of possible gene
        types and minimum viable metabolism that can be constructed.

        The population is then generated by cloning the ancestor individual.
        Clones are identical and store a reference to the ancestor.

        Parameters
        ----------
        pop_size : int
            population size
        environment : :class:`VirtualMicrobes.environment.Environment`
            environment that is home to the population; determines molecular and reaction universe
        params_dict : dict, optional
            a dictionary of simulation parameters
        time : int, optional
            time of birth of the clone

        Returns
        -------
        common ancestor : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            the common ancestor of the cloned population
        '''
        common_ancestor = Cell(params=params_dict, environment=environment,
                        rand_gen=self.pop_rand_gen, time_birth=-1)
        common_ancestor.init_genome(environment)
        self.add_cell(common_ancestor)
        for _ in range(pop_size):
            clone = common_ancestor.clone(time)
            self.add_cell(clone)
        return common_ancestor

    def cloned_pop_from_files(self, pop_size, environment,
                              cell_files = None, time=0):
        '''
        Create population of individuals initialised from cell parameter files.

        Creates :class:`VirtualMicrobes.virtual_cell.Cell.Cell` individuals
        and reads their genome and state from cell parameter files.

        Parameters
        ----------
        pop_size : int
            population size
        environment : :class:`VirtualMicrobes.environment.Environment`
            environment that is home to the population; determines molecular and reaction universe
        time : int, optional
            time of birth of the clone

        Returns
        -------
        common_ancestors : list of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` objects
            the common ancestors of the new population
        '''
        if cell_files is None:
            cell_files = self.params.cells_from_files

        common_ancestors = []
        for filename in cell_files:
            common_ancestor = Cell(self.params, environment=environment, rand_gen=self.pop_rand_gen)
            common_ancestor.set_state_from_file(environment, filename, max_lin_marker=2*pop_size)
            common_ancestors.append(common_ancestor)
            self.add_cell(common_ancestor) # Note: is it correct to add the ancestors to the population?
        for common_ancestor in common_ancestors:
            for _ in range(pop_size/len(cell_files)):
                clone = common_ancestor.clone(time)
                self.add_cell(clone)
        return common_ancestors

    def add_cell(self,cell):
        '''
        Add an individual to the population.

        A cell that is added is stored in a dictionary that maps the individual to
        a dictionary of properties, e.g. the numer of offspring.

        Increase the population size.

        Parameters
        ----------
        cell : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            the individual to add
        '''

        self.cell_dict[cell] = dict()  # NOTE: unordered ok
        self.cell_dict[cell]['child_count'] = 0
        self.current_pop_size += 1

    def init_current_ancestors(self):
        '''Initialise the current ancestors.'''
        self.current_ancestors = util.LinkThroughSet(self.cells)

    def init_roots(self, roots=None):
        '''
        Initialise the phylogenetic roots.

        If no `roots` are given, initialise roots with the `current_ancestors`.

        Parameters
        ----------
        roots : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`, optional
            roots ancestors of the population
        '''
        if roots is None:
            self.roots = self.current_ancestors.copy()
        else:
            self.roots = util.LinkThroughSet(roots)

    def init_phylo_tree(self, supertree=False):
        '''
        Initialise the phylogenetic tree of the population.

        Parameters
        ----------
        supertree : bool, optional
            if true create supertree of all independent phylogenetic lineages
        '''
        self.phylo_tree = PhyloTree(supertree=supertree)

    def update_phylogeny(self, new_roots=None, verbose=True):
        '''
        Update the phylogeny of the current population.

        `current_ancestors` contains all living individuals and those that have
        contributed to the current population.

        Individuals are only added to the `phylo_tree` representation after they
        have died. Nodes will only remain in the `phylo_tree` as long as the
        branch they're on contains a living individual in the current
        population. If a lineage dies out, its corresponding branch (and its
        constituent tree nodes) is pruned from the phylogenetic tree.

            * Add new offspring to the current ancestors.
            * Prune extinct branches in the phylogeny and remove ancestors
              without living offspring
            * Update the phylogenetic tree structure:
                * add new root nodes
                * add new intermediate nodes
                * prune dead branches and nodes

        Parameters
        ----------
        new_roots : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`, optional
            new roots in the `phylo_tree`
        verbose : bool, optional
            print tree changes

        Returns
        -------
        phylo_tree : :class:`VirtualMicrobes.Tree.PhyloTree.PhyloTree`
            phylogenetic tree representation of current population
        '''

        # add new offspring to the set of all ancestors
        self._update_current_ancestors(set(self.new_offspring))
        # prune dead branches of phylogenies
        self._clear_extinct_lineages()

        self.phylo_tree.clear()
        tree_nodes = [anc for anc in self.current_ancestors if not anc.alive]
        roots = [ r for r in self.roots if not r.alive]
        self.phylo_tree.update(new_phylo_units=set(tree_nodes) - set(roots) , new_roots=roots)

        self._clear_from_phylo_linker()
        if verbose:
            n = len(self.current_ancestors)
            print "%d ancestor%s" % (n, "s"[n==1:]) , 'and',
            n = len(self.roots)
            print "%d root%s in the population." % (n, "s"[n==1:])
        return self.phylo_tree

    def _update_current_ancestors(self, new_offspring):
        self.current_ancestors.update(new_offspring)

    def update_cell_params(self, cells=None):
        '''
        Update the the cell parameters.

        Sets cell parameters from the Simulation `params` dict.

        Parameters
        ----------
        cells : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`, optional
            the cells to update
        '''
        if cells is None:
            cells = self.cells
        for cell in cells:
            cell.init_cell_params()

    def _clear_extinct_lineages(self):
        '''Clear extinct lineages from the population and phylogeny'''
        self._prune_dead_branches()
        self._prune_current_ancestors()
        self._prune_roots()

    def _clear_from_phylo_linker(self):
        self._remove_pruned_from_phylo_linker()

    def _prune_dead_branches(self, dead_cells=None):
        '''Prune dead branches from the phylogenetic tree.'''
        if dead_cells is None:
            dead_cells = self.died
        self.pruned_cells = set()
        self.pruned_chromosomes = set()
        self.pruned_genes = set()
        for cell in dead_cells:
            cells, chromosomes, genes = cell.prune_dead_phylo_branches()
            self.pruned_cells.update(cells)
            self.pruned_chromosomes.update(chromosomes)
            self.pruned_genes.update(genes)
        print len(self.pruned_cells), 'cells', len(self.pruned_chromosomes), 'chromosomes',
        print len(self.pruned_genes), 'genes pruned from ancestry.'
        return self.pruned_cells, self.pruned_chromosomes, self.pruned_genes

    def _prune_current_ancestors(self):
        '''Prune current ancestors.'''
        self.current_ancestors -= self.pruned_cells

    def _prune_roots(self):
        '''Prune roots of poulation.'''
        self.roots &= self.current_ancestors

    def _remove_pruned_from_phylo_linker(self):
        '''Remove pruned :class:`VirtualMicrobes.virtual_cell.PhyloUnit.PhyloUnit
        from the global dict of phylogenetic units.
        '''
        phylo_units = self.pruned_cells | self.pruned_chromosomes | self.pruned_genes
        for phylo_unit in phylo_units:
            if isinstance(phylo_unit, PhyloUnit):
                phylo_unit._remove_from_linker_dict()

    def clear_pop_changes(self):
        '''Reset population change containers.'''
        self.new_offspring, self.pruned_cells, self.died = [], set(), []

    def reset_divided(self):
        '''Reset flag for recent cell division.'''
        for cell in self.cells:
            cell.divided = False

    def init_cells_view(self):
        '''Initialise the view on the keys of the cell dict.'''
        self.cells = self.cell_dict.viewkeys()

    def genome_sizes(self, cells=None):
        '''Return array of individual genome sizes.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.genome_size for cell in cells])

    def chromosome_counts(self, cells=None):
        '''Return array of individual chromosome counts.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.chromosome_count for cell in cells])

    def tf_counts(self, cells=None):
        '''Return array of individual transcription factor gene counts.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.tf_count for cell in cells])

    def enzyme_counts(self, cells=None):
        '''Return array of individual enzyme gene counts.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.enzyme_count for cell in cells])

    def exporter_counts(self, cells=None):
        '''Return array of individual exporting pump gene counts.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.eff_pump_count for cell in cells])

    def importer_counts(self, cells=None):
        '''Return array of individual importing pump gene counts.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.inf_pump_count for cell in cells])

    def point_mut_counts(self, cells=None):
        '''Return array of individual counts of life time point mutations.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.point_mut_count for cell in cells])

    def chromosomal_mut_counts(self, cells=None):
        '''Return array of individual counts of life time chromosomal mutations.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.chromosomal_mut_count for cell in cells])

    def death_rates(self, cells=None):
        '''Return array of individual death rate parameters.'''
        death_rate_dict = self.get_cell_death_rate_dict(cells)
        return np.array([ d for d in death_rate_dict.values() if d is not None ])

    def production_values(self, cells=None):
        '''Return array of individual production values.'''
        production_value_dict = self.get_cell_production_dict(cells)
        return np.array([ prod for prod in production_value_dict.values() if prod is not None ])

    def pos_production(self, cells=None):
        '''Return array of individual positive production rates.'''
        pos_production_dict = self.get_cell_pos_production_dict(cells)
        return np.array([ prod for prod in pos_production_dict.values() if prod is not None ])

    def production_rates(self, cells=None):
        '''Return array of individual netto production rates.'''
        production_rate_dict = self.get_cell_production_rate_dict(cells)
        return np.array([ prod for prod in production_rate_dict.values() if prod is not None ])

    def cell_sizes(self, cells=None):
        '''Return array of individual cell volumes.'''
        cell_size_dict = self.get_cell_size_dict(cells)
        return np.array([ size for size in cell_size_dict.values() if size is not None ])

    def toxicity_rates(self, cells=None):
        '''Return array of individual toxicity change rates.'''
        toxicity_change_dict = self.get_cell_toxicity_rate_dict(cells)
        return np.array([ prod for prod in toxicity_change_dict.values() if prod is not None ])

    def average_promoter_strengths(self, cells=None):
        '''Return array of individual average genomic promoter strength.'''
        if cells is None:
            cells = self.cells
        return np.array( [ cell.avrg_promoter_strengths for cell in cells] )

    def tf_average_promoter_strengths(self, cells=None):
        '''Return array of individual average transcription factor promoter strength.'''
        if cells is None:
            cells = self.cells
        return np.array( [ cell.tf_avrg_promoter_strengths for cell in cells] )

    def enz_average_promoter_strengths(self, cells=None):
        '''Return array of individual average enzyme promoter strength.'''
        if cells is None:
            cells = self.cells
        return np.array( [ cell.enz_avrg_promoter_strengths for cell in cells] )

    def pump_average_promoter_strengths(self, cells=None):
        '''Return array of individual average pump promoter strength.'''
        if cells is None:
            cells = self.cells
        return np.array( [ cell.pump_avrg_promoter_strengths for cell in cells] )

    def differential_regulation(self, cells=None):
        '''Return array of individual average differential regulation value.'''
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.tf_differential_reg) for cell in cells] )

    def pump_average_vmaxs(self, cells=None):
        '''Return array of individual average pump vmax values.'''
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.pump_vmaxs) for cell in cells] )

    def enzyme_average_vmaxs(self, cells=None):
        '''Return array of individual average enzyme vmax values.'''
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.enz_vmaxs) for cell in cells] )

    def tf_k_bind_operators(self, cells = None):
        '''Return array of individual average transcription factor operator binding strength values.'''
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.tf_k_bind_ops) for cell in cells])

    def tf_ligand_ks(self, cells = None):
        '''Return array of individual average transcription factor ligand binding strength values.'''
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.tf_ligand_ks) for cell in cells])

    def enzyme_substrate_ks(self, cells = None):
        '''Return array of individual average enzyme substrate binding strength values.'''
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.enz_subs_ks) for cell in cells])

    def pump_substrate_ks(self, cells = None):
        '''Return array of individual average pump substrate binding strength values.'''
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.pump_subs_ks) for cell in cells])

    def pump_energy_ks(self, cells = None):
        '''Return array of individual average pump energy binding strength values.'''
        if cells is None:
            cells = self.cells
        return np.array( [ np.nanmean(cell.pump_ene_ks) for cell in cells])


    def offspring_counts(self, cells=None):
        '''Return array of individual offspring counts.'''
        if cells is None:
            cells = self.cells
        return np.array([ len(c.living_offspring()) for c in cells ])

    def iterages(self, cells=None):
        '''Return array of individual line of descent ages.'''
        if cells is None:
            cells = self.cells
        return np.array([ cell.iterage for cell in cells])

    def regulator_score(self, cells = None):
        if cells is None:
            cells =  list(self.cells)
        clonedict = defaultdict(list)
        for cell in cells:
            clonedict[str(cell.genome)].append(cell)

        list_scores = []
        skip = 1
        for clones in sorted(clonedict.values(), key=len, reverse=True)[:10]:
            self.pop_rand_gen.shuffle(clones)                                # Shuffle comparison list to randomize comparison
            for cell in clones[:100]:                                        # Number of comparisons to make within clone
                for cell2 in clones[skip:100]:
                    list_scores.append(cell.qual_expr_diff(cell2))
                skip += 1                                                    # Ensures no comparison is made twice, and also avoids self-comparison.
        return np.array([np.nanmean(list_scores)])

    def pan_reactome_dict(self, cells=None):
        '''
        Return the pan reactome of the population.

        The pan-reactome is the combined set of reactions present in the
        population.

        Returns
        -------
        pan_reactome_dict : mapping of reaction type to sets of
        :class:`VirtualMicrobes.event.Reaction.Reaction` s

        Notes
        -----

        For historic reasons the set of all transport reactions, either
        importing or exporting are keyd under 'import'. This type as stored
        in the `type_` attribute of the
        :class:`VirtualMicrobes.event.Reaction.Reaction` and should not be
        confused with the `type_` attribute of the
        :class:VirtualMicrobes.virtual_cell.Gene.Gene` object.
        '''
        pan_reactome_dict = {'import':set(), 'conversion':set()}
        if cells is None:
            cells = self.cells
        for cell in cells:
            for (reac_type, reac_set) in cell.reaction_set_dict.items():
                pan_reactome_dict[reac_type].update(reac_set)
        return pan_reactome_dict

    def reaction_counts(self, cells=None):
        '''Return counts of all reactions found in the population.'''
        if cells is None:
            cells = self.cells
        all_reactions = []
        for cell in cells:
            for reac_set in cell.reaction_set_dict.values():
                all_reactions += list(reac_set)
        return collections.Counter(all_reactions)

    def trophic_type_counts(self, env, cells=None):
        '''Return counts of trophic types in the population.'''
        if cells is None:
            cells = self.cells
        return collections.Counter([ cell.trophic_type(env) for cell in cells ])

    def reaction_counts_split(self, cells=None):
        '''Return counts of all reactions found in the population per reaction type.'''
        if cells is None:
            cells = self.cells
        reaction_counts_split = collections.defaultdict(list)
        for cell in cells:
            for reac_type, reac_set in cell.reaction_set_dict2.items():
                reaction_counts_split[reac_type] += list(reac_set)
        return dict( [ (reac_type, collections.Counter(reacs)) for reac_type, reacs in reaction_counts_split.items() ])


    def metabolic_type_counts(self, cells=None):
        '''
        Return frequencies of cell sets with identical metabolic types.

        A metabolic type is defined on the bases of the full set of metabolic reactions
        that an individual can perform using its metabolic gene set.
        A frequency spectrum of these types is than produced in the form of a
        collections.Counter object. From this object we can ask things like:
        most_common(N) N elements etc.
        '''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( cell.metabolic_type for cell in cells )
        return type_counts

    def producer_type_counts(self, cells=None):
        '''Return counts of cell sets with equal production metabolomes.'''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( map(frozenset, ( c.produces for c in cells ) ) )
        return type_counts

    def consumer_type_counts(self, cells=None):
        '''Return counts of cell sets with equal consumption metabolomes.'''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( map(frozenset, ( c.consumes for c in cells ) ) )
        return type_counts

    def import_type_counts(self, cells=None):
        '''Return counts of cell sets with equal import genotypes'''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( map(frozenset, ( c.import_type  for c in cells ) ) )
        return type_counts

    def export_type_counts(self, cells=None):
        '''Return counts of cell sets with equal export genotypes'''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( map(frozenset, ( c.export_type for c in cells ) ) )
        return type_counts

    def genotype_counts(self, cells=None):
        '''Return counts of cell sets with equal genotypes'''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( cell.genotype for cell in cells )
        return type_counts

    def reaction_genotype_counts(self, cells=None):
        '''Return counts of cell sets with equal reaction genotypes'''
        if cells is None:
            cells = self.cells
        type_counts = collections.Counter( cell.reaction_genotype for cell in cells )
        return type_counts

    @classmethod
    def metabolic_complementarity(cls, cells, strict_providing=False, strict_exploiting=False):
        '''
        Determine for the list of cells what the overlap is in metabolites
        provided and exploited.

        To provide a metabolite a cell should simultaneous produce and export
        the metabolite. To exploit, it should be imported and consumed in a
        reaction.
        '''
        provided = set.union(set(),*[ c.strict_providing if strict_providing else c.providing  for c in cells ])
        exploited = set.union(set(),*[ c.strict_exploiting if strict_exploiting else c.exploiting for c in cells])
        return provided & exploited

    def metabolic_complementarity_pop(self, strict=False):
        '''
        Return the set of metabolites that are provided and exploited simultaneously by the population.


        See Also
        --------
        func:`metabolic_complementarity`
        '''
        return self.metabolic_complementarity(self.cells, strict)

    def get_cell_death_rate_dict(self, cells=None):
        return self._get_cell_property_dict("death_rate", cells)

    def get_cell_production_dict(self, cells=None, life_time_prod=None):
        '''
        Return a mapping of cells and their last or life time production value.

        Parameters
        ----------
        cells : sequence of Cell objects
            individuals to map, default is the current population
        life_time_prod : bool
            take life time mean production instead of current
        '''
        if cells is None:
            cells = self.cells
        if life_time_prod is None:
            life_time_prod = self.params.life_time_prod
        if life_time_prod:
            return collections.OrderedDict( [ (c, c.mean_life_time_production) for c in cells ] )
        return collections.OrderedDict( [ (c, c.raw_production) for c in cells ] )

    def get_cell_pos_production_dict(self, cells=None):
        '''Return dict of cell production values.'''
        if cells is None:
            cells = self.cells
        return collections.OrderedDict( [ (c, c.mean_life_time_pos_production) for c in cells ] )

    def get_cell_production_rate_dict(self, cells=None):
        '''Return dict of cell production rates.'''
        if cells is None:
            cells = self.cells
        return collections.OrderedDict( [ (c, c.raw_production_change_rate) for c in cells ] )

    def get_cell_size_dict(self, cells=None):
        '''Return dict of cell sizes.'''
        if cells is None:
            cells = self.cells
        return collections.OrderedDict( [ (c, c.volume) for c in cells ] )

    def get_cell_toxicity_rate_dict(self, cells=None):
        '''Return dict of cell toxicity change rates.'''
        if cells is None:
            cells = self.cells
        return collections.OrderedDict( [ (c, c.toxicity_change_rate) for c in cells ] )

    def get_cell_reproduction_dict(self, cells=None):
        '''
        Counts of the number of reproduction events for each cell (living and
        dead direct children)
        '''
        return self._get_cell_property_dict("child_count", cells)

    def _get_cell_property_dict(self, prop_name, cells=None):
        if cells is None:
            cells = self.cells
        cell_property_dict = collections.OrderedDict()
        for cell in cells:
            if self.cell_dict[cell].has_key(prop_name):
                cell_property_dict[cell] = self.cell_dict[cell][prop_name]
            else:
                cell_property_dict[cell] = None
        return cell_property_dict

    def update_ete_tree(self):
        '''Update the ete tree representation of the phylo_tree.'''
        return  self.phylo_tree.to_ete_trees()

    def metabolic_type_color(self, cell):
        mt_low, mt_high = self.markers_range_dict['metabolic_type']
        metabolic_type = cell.marker_dict.get('metabolic_type',0.)
        mt_color = metabolic_type/ float((mt_high - mt_low)) + mt_low
        return mt_color

    def annotate_phylo_tree(self, ete_tree_struct,
                             features=[], func_features=dict(), max_tree_depth=None,
                             prune_internal=False, cummulative=True, to_rate=False,
                             ete_root=None):
        '''
        Annotate the phylogenetic tree with cell data for tree plotting.

        Assumes that the ete_tree has been constructed/updated. Creates a
        dictionary of feature dictionaries, keyed by the cells in the tree.
        Attaches the feature dictionaries to nodes in the ete_tree
        (annotate_ete_tree). Transforms some data to cummulative data along the
        branches of the tree. Optionally, prunes internal tree nodes (this will
        greatly simplify the tree drawing algorithm). Finally, transforms some
        data to rate of change data, using branch length for rate calculation.

        Parameters
        ----------
        ete_tree_struct : :class:`VirtualMicrobes.my_tools.utility.ETETreeStruct`
            tuple holding ete_tree information
        features : list of str, optional
            features to annotate on tree nodes
        func_features : dict, optional
            functions to calculate features on the tree
        max_tree_depth : int, optional
            simulation time point to prune tree to
        prune_internal : bool, optional
            prune internal nodes
        cummulative : bool, optional
            annotate cummulative features on tree nodes
        to_rate : bool, optional
            add conversion to rates for features on tree nodes
        ete_root : :class:`ete3.TreeNode` , optional
            alternative root of the ete tree.

        Returns
        -------
        (phylotree, pruned) : (class:`ete3.TreeNode`,
                               set of :class:`ete3.TreeNode` s)
            the annotated tree structure, pruned tree nodes
        '''
        if ete_root is None:
            ete_root = ete_tree_struct.tree
        pruned = set()
        if max_tree_depth is not None:
            pruned |= self.phylo_tree.ete_prune_external(ete_tree_struct, max_tree_depth)
        self.phylo_tree.ete_annotate_tree(ete_tree_struct, features,
                                          func_features, ete_root)
        if cummulative:
            self.phylo_tree.ete_cummulative_features(ete_tree_struct, features,
                                                     func_features, ete_root)

        if prune_internal:
            pruned |= self.phylo_tree.ete_prune_internal(ete_tree_struct)
        if to_rate:
            max_rate_dict = self.phylo_tree.ete_rate_features(ete_tree_struct, features,
                                                              func_features, ete_root)
            self.value_range_dict.update( (feature, (0, max_rate)) for feature, max_rate in max_rate_dict.items() )
        return (ete_root, pruned)

    def print_state(self):
        '''Print population state.'''
        for c in self.cells:
            print "cell"+str(c.id)
            for m, conc in c.get_mol_concentration_dict().items():
                print "("+str(m), str(conc)+")",
            for g, conc in c.get_gene_concentration_dict().items():
                print "("+str(g.id)+g['type'], str(conc)+")",
            print '(tox', str(c.toxicity)+")",
            print '(prod', str(c.raw_production)+")"

    def best_producer(self):
        '''Return the individual and the value of highest production in the population.'''
        best_producer, production = None, 0
        for cell, prod in self.get_cell_production_dict().items():
            if prod is None:
                continue
            if prod > production:
                best_producer = cell
                production = prod
        if best_producer is None:
            raise Exception('No cell with positive production found')
        return best_producer, production

    def most_offspring(self):
        '''Return individual and value of highest offspring count.'''
        most_fecundant, offspring_count = None, 0
        for cell in self.cells:
            oc = len(cell.living_offspring())
            if oc >= offspring_count:
                most_fecundant, offspring_count = cell, oc
        return most_fecundant, offspring_count

    def oldest_cell(self):
        '''Return oldest living individual.'''
        bt_sorted = sorted(self.cells, key=lambda c: c.time_birth)
        oldest_cell = None
        try:
            oldest_cell = bt_sorted.pop(0)
        except:
            pass
        return oldest_cell

    def calculate_death_rates(self,base_death_rate=None, max_die_off_fract=None,
                              toxicity_scaling=None, cells=None):
        '''
        Calculate and store death rates of individuals.

        Uses a `base_death_rate` and `toxicity_scaling` parameter to calculate
        the death rate of individuals.

        Parameters
        ----------
        base_death_rate : float, optional
            base death rate for all individuals
        max_die_off_fract : float, optional
            maximum fraction of individuals that can die (stochastically)
        toxicity_scaling : float, optional
            scaling parameter for toxicity death rate effect
        cells : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            individuals in calculation

        Returns
        -------
        returns mapping of cells to death rates
        '''
        if cells is None:
            cells = self.cells
        if max_die_off_fract is None:
            max_die_off_fract = self.params.max_die_off_fraction
        if base_death_rate is None:
            base_death_rate = self.params.base_death_rate
        if toxicity_scaling is None:
            toxicity_scaling = self.params.toxicity_scaling
        for cell in cells:
            raw_death_rate = cell.calculate_raw_death_rate(base_rate=base_death_rate,
                                                           toxicity_scaling=toxicity_scaling)
            self.cell_dict[cell]["death_rate"] = raw_death_rate
        if max_die_off_fract:
            self.scale_death_rates(max_die_off_fract, cells)
        return self.get_cell_death_rate_dict(cells)

    def scale_death_rates(self, max_die_off_fract, cells=None):
        '''
        Scale death rates to give a maximum rate of dieing individuals.

        If individual death rate are too high, these are scaled to have a maximum
        fraction of deaths, on average, in the population.

        Parameters
        ----------
        max_die_of_fract : float
            maximum allowed fraction of deaths
        cells : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            individuals in calculation

        Returns
        -------
        returns mapping of cells to death rates
        '''

        util.within_range(max_die_off_fract, (0., 1.))
        if cells is None:
            cells = self.cells
        total_death = sum(self.death_rates(cells))
        raw_death_frac = total_death/float(len(cells))
        if raw_death_frac > max_die_off_fract:
            print "raw death fraction", raw_death_frac
            scaling = raw_death_frac/max_die_off_fract
            for cell in cells:
                self.cell_dict[cell]['death_rate'] /=scaling
        return self.get_cell_death_rate_dict(cells)

    def wipe_pop(self, fract, time, min_surv=None, cells=None):
        '''
        Kill a fraction of the individuals.

        Sets a flag on individuals that were killed by `wipe_pop`.

        Parameters
        ----------
        fract : float
            fraction to kill
        time : int
            simulation time
        min_surv : int, optional
            minimum number of surviving individuals
        cells : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            individuals in calculation

        Returns
        -------
        list of individuals that were killed
        '''
        if cells is None:
            cells = list(self.cells)
        self.pop_rand_gen.shuffle(cells)
        kill_num = int(fract*len(cells)) # Number of cells that will die
        if min_surv is not None and len(cells) - kill_num < min_surv:
            kill_num -=  (min_surv - (len(cells) - kill_num))
        cells_to_kill = cells[:kill_num]
        for cell in cells_to_kill:
            self.cell_death(cell, time, wiped=True)
        return cells_to_kill

    def cell_death(self, cell, time, wiped=False):
        '''
        Kill an individual.

        Updates the population size. Sets the time of death of individual.

        Parameters
        ----------
        cell : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            individual that is killed
        time : int
            simulation time
        wiped : bool
            indicate if cell died by `wipe_pop`
        '''
        del self.cell_dict[cell]
        self.current_pop_size -= 1
        cell.die(time, wiped=wiped)
        self.died.append(cell)

    def die_off(self,time, max_die_off_frac=None, min_cell_volume=None,
                stochastic_death=None, cells=None):
        '''
        Kill individual cells.

        Individuals die deterministically if their cell volume is too low, or
        stochastically, with a probability : `death_rate` .

        Parameters
        ----------
        time : int
            simulation time
        max_die_off_frac : float, optional
            maximum fraction of individuals that can die
        min_cell_volume : float, optional
            minimum cell volume for survival
        stochastic_death : bool, optional
            if true, cells die stochastically, according to a `death_rate`
        cells : sequence of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            individuals that can die
        '''
        if cells is None:
            cells = self.cells
        if max_die_off_frac is None:
            max_die_off_frac = self.params.max_die_off_fraction
        if min_cell_volume is None:
            min_cell_volume = self.params.min_cell_volume
        if stochastic_death is None:
            stochastic_death = self.params.stochastic_death
        max_die = len(cells)
        if max_die_off_frac is not None:
            max_die = int(max_die * max_die_off_frac)
        death_count = 0
        for cell in cells:
            if death_count >= max_die:
                break
            if min_cell_volume is not None and cell.volume < min_cell_volume:
                death_count+=1
                self.cell_death(cell, time)
            elif stochastic_death:
                if self.evo_rand_gen.uniform(0,1.) < self.cell_dict[cell]['death_rate']:
                    death_count+=1
                    self.cell_death(cell, time)


    def reproduce_cell(self,cell, time, spent_production=0., report=False):
        '''
        Reproduction of individual cell.

        Parameters
        ----------
        cell : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            reproducing individual
        time : int
            simulation time
        spent_production : float, optional
            production spent on reproducing
        report : bool, optional
            reporting

        Returns
        -------
        offspring : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            new individual
        '''
        if report:
            print str(cell.id)+": reproducing. Production reached:", cell.raw_production
        offspring = cell.reproduce(spent_production=spent_production, time=time)
        self.cell_dict[cell]['child_count'] += 1
        self.add_cell(offspring)
        return offspring

    def select_reproducing_cell(self, cells_competition_value, rand_nr, non=0.,
                                competition_scaling_fact=None):
        '''
        Select a competing individual for reproduction.

        Parameters
        ----------
        cells_competition_value : list of (class:`VirtualMicrobes.virtual_cell.Cell.Cell`, float)
            competing cells with competition values
        rand_nr : float
            randomly drawn value between 0 and 1.
        non : float, optional
            value between 0 and 1 that represents no individual is chosen
        competition_scaling_fact : float, optional
            factor that can skew competition to be more or less severe

        Returns
        -------
        (chosen individual, competition_value, index in competition list)
        '''
        if competition_scaling_fact is None:
            competition_scaling_fact = self.params.competition_scaling
        competition_scaling = lambda p, n : p ** n
        cells_competition_value = [ (c, competition_scaling(p, competition_scaling_fact))
                                   for (c,p) in cells_competition_value ]
        non = competition_scaling(non, competition_scaling_fact)
        return util.roulette_wheel_draw(cells_competition_value, rand_nr, non)

    def prune_metabolic_types(self, cells=None):
        if cells is None:
            cells = self.cells
        cell_metabolic_types = self.metabolic_type_counts(cells).keys()
        extinct = set(self.metabolic_type_marker_dict.keys()) - set(cell_metabolic_types)
        for met_type in extinct:
            self.metabolic_type_marker_dict.remove_key(met_type)

    def store_pop_characters(self):
        self.mark_cells_metabolic_type()

    def reproduce_at_minimum_production(self, time, competitors=None,
                                        max_reproduce=None, reproduction_cost=None):
        if competitors is None:
            competitors = self.cells
        if max_reproduce is None:
            max_reproduce = self.max_pop_size - len(self.cells)
        if reproduction_cost is None:
            reproduction_cost = self.params.reproduction_cost
        new_offspring = []
        cells_production = [ (c,p) for (c,p) in self.get_cell_production_dict(competitors).items()
                                   if p >= reproduction_cost]
        while cells_production:
            if len(new_offspring) >= max_reproduce:
                break
            rand = self.evo_rand_gen.uniform(0,1)
            the_one, production, index = self.select_reproducing_cell(cells_production, rand)
            if production < reproduction_cost:
                raise Exception("cost to reproduce %f higher than cell production %f"%(reproduction_cost, production))
            new_offspring.append(self.reproduce_cell(cell=the_one, time=time,
                                                     spent_production=reproduction_cost))
            if the_one.raw_production >= reproduction_cost:
                cells_production[index] = (the_one, the_one.raw_production )
            else:
                del cells_production[index]
        self.new_offspring += new_offspring
        return new_offspring

    def reproduce_production_proportional(self, time, competitors, max_reproduce=None,
                                          production_spending_fract=None, non=0.):
        '''
        Individuals compete and reproduce proportional to their production value.

        Parameters
        ----------
        time : int
            simulation time
        competitors : list of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            competing individuals
        max_reproduce : int, optional
            maximum allowed reproduction events
        production_spending_fract : float, optional
            fraction of cell production value spent on reproduction
        non : float, optional
            chance of no competitor winning competition

        Returns
        -------
        new_offspring : list of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s
            new offspring produced in this function
        '''
        if max_reproduce is None:
            max_reproduce = self.max_pop_size - len(self.cells)
        if production_spending_fract is None:
            production_spending_fract = self.params.product_spending_fraction

        util.within_range(production_spending_fract, (0., 1.))
        new_offspring = []
        cells_production = self.get_cell_production_dict(competitors).items()
        if not cells_production:
            return new_offspring
            raise Exception("No cells available for reproduction")
        for _ in range(max_reproduce):
            rand = self.evo_rand_gen.uniform(0,1.)
            the_one, production, index = self.select_reproducing_cell(cells_production,
                                                                      rand_nr=rand,
                                                                      non=non)
            if the_one is None:
                continue
            reproduction_cost = production_spending_fract * production
            new_offspring.append(self.reproduce_cell(cell=the_one, time=time,
                                                     spent_production=reproduction_cost))
            cells_production[index] = (the_one, the_one.raw_production)
        self.new_offspring += new_offspring
        return new_offspring

    def reproduce_size_proportional(self, time, competitors, max_reproduce=None,
                                   non=0.):
        '''
        Individuals compete and reproduce proportional to their cell size.

        Parameters
        ----------
        time : int
            simulation time
        competitors : list of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
            competing individuals
        max_reproduce : int, optional
            maximum allowed reproduction events
        non : float, optional
            chance of no competitor winning competition

        Returns
        -------
        new_offspring : list of :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s
            new offspring produced in this function
        '''
        if max_reproduce is None:
            max_reproduce = self.max_pop_size - len(self.cells)
        new_offspring = []
        for _ in range(max_reproduce):
            if not competitors:
                break
            cells_volumes = [ (cell, cell.volume) for cell in competitors ]
            rand = self.evo_rand_gen.uniform(0,1.)
            the_one, _prod, _index = self.select_reproducing_cell(cells_volumes, rand_nr=rand, non=non)
            if the_one is None:
                continue
            new_offspring.append(self.reproduce_cell(cell=the_one, time=time))
            if the_one.volume < self.params.cell_division_volume:
                competitors.remove(the_one)
        self.new_offspring += new_offspring
        return new_offspring

    def calculate_reference_production(self, pressure=None, historic_production_weight=None):
        '''
        Calculates a reference production value for competition.

        Reference production is used to scale the reproductive potential of
        cells during competition to reproduce.

        Parameters
        ----------
        pressure : str
            type of selection pressure scaling
        historic_production_weight : float, optional
            weighting of historic production values
        '''
        if historic_production_weight is None:
            historic_production_weight = self.params.historic_production_weight
        if pressure is None:
            pressure = self.params.selection_pressure
        if pressure == 'current_scaled':
            self.historic_production_max = np.median(self.production_values())
        elif pressure == 'historic_scaled':
            self.historic_production_max = max(self.historic_production_max,
                                           (self.historic_production_max*(historic_production_weight) +
                                            np.median(self.production_values())) / (historic_production_weight+1))
        elif pressure == 'historic_window_scaled':
            missing =  self.params.historic_production_window - len(self.production_val_history)
            historic_average = np.mean(self.production_val_history + [self.historic_production_max] * missing )
            self.historic_production_max = max(self.historic_production_max, historic_average)
        elif pressure in ['historic_fixed', 'constant']:
            pass
        else:
            raise Exception, 'selection pressure {0} not recognized'.format(pressure)
        if (self.params.max_historic_max is not None and
            self.historic_production_max > self.params.max_historic_max):
            self.historic_production_max = self.params.max_historic_max

    def update_prod_val_hist(self, hist_prod_func=np.median, historic_production_window=None,
                             pop_size_scaling=None):
        '''
        Keep a sliding window view on historic production values.

        Parameters
        ----------
        hist_prod_func : func, optional
            calculates the population production value
        historic_production_window : int, optional
            length of the sliding window
        pop_size_scaling : bool, optional
            scale production value by population size
        '''
        if historic_production_window is None:
            historic_production_window = self.params.historic_production_window
        if pop_size_scaling is None:
            pop_size_scaling = self.params.scale_prod_hist_to_pop
        current_prod_val = hist_prod_func(self.production_values())
        if pop_size_scaling:
            current_prod_val *= self.current_pop_size / float(self.max_pop_size)
        self.production_val_history = self.production_val_history[-historic_production_window:]
        self.production_val_history.append(current_prod_val)

    def make_anc_clones(self,generations_ago,density):
        self.clear_pop_changes()
        if density == 0.0:
            density = len(self.cells)/float(self.max_pop_size)
        cells_pop = list(self.cells)
        cell_temp = cells_pop[0].get_ancestor(3)
        cell_anc = cells_pop[0].get_ancestor_from_time(generations_ago)
        #cell_anc = cell_temp      # You can use this if you want a control experiment, compete with self
        nr_of_clones = int(self.max_pop_size * density / 2)
        cells = [cell_temp.clone(0) for _ in range(nr_of_clones)]

        for cell in cells:
            cell.set_state_from_ref_cell_tp(cell_temp, 0)
            cell.mark('lineage', int(0.6*2*self.max_pop_size))

        ancs = [cell_anc.clone(0) for _ in range(nr_of_clones)]

        for anc in ancs:
            anc.set_state_from_ref_cell_tp(cell_anc, 0)
            anc.mark('lineage', int(0.125*2*self.max_pop_size))

        return cells + ancs # List of cell-clones, and ancestors of the clone

    def make_cell_clones(self,environment,list_of_cell_files,density):
        print 'Creating cell clones from files', ', '.join(map(str,list_of_cell_files))
        self.clear_pop_changes()
        cells = []
        clones = []
        if density is None:
            density = 1.0
        numtypes = len(list_of_cell_files)

        for i,filename in enumerate(list_of_cell_files):
            cell = Cell(self.params, environment=environment, rand_gen=self.pop_rand_gen)
            color = i * 2 * (len(environment.localities)/ numtypes) + 1
            color = (color+200)%(2*len(environment.localities))
            cell.set_state_from_file(environment, filename, max_lin_marker=int(len(environment.localities) ) )
            cells.append(cell)

        for cell in cells:
            clones += [cell.clone(0) for _ in range(int(len(environment.localities)*density/numtypes))]

        return clones   # List of cell (and clones of it)

    def reproduce_on_grid(self, grid, max_pop_per_gp, time, neighborhood='competition',
                          non=None, selection_pressure=None):
        '''
        Reproduction of the population on the spatial grid.

        Parameters
        ----------
        grid : :class:`VirtualMicrobes.Environment.Grid.Grid`
            spatial grid environment
        max_pop_per_gp : int
            maximum number of individuals per grid point
        time : int
            simulation time
        neighborhood : str, optional
            key to select neighborhood shape
        non : float, optional
            chance of no competitor winning competition
        selection_pressure : str
            type of selection pressure

        Returns
        -------
        new_offspring_gp_dict : :class:`VirtualMicrobes.virtual_cell.Cell.Cell` ->
                                :class:`VirtualMicrobes.environment.Grid.GridPoint`
            mapping of new offspring to the spatial grid point that they are born in.
        '''
        if non is None:
            non = self.params.non
        if selection_pressure is None:
            selection_pressure = self.params.selection_pressure
        self.calculate_reference_production(selection_pressure)
        if selection_pressure != 'constant' and not self.params.reproduce_size_proportional:
            non = non * self.historic_production_max
        # update the production_val_history
        self.update_prod_val_hist()
        new_offspring_gp_dict = collections.OrderedDict()
        gps = list(grid.gp_iter)
        self.pop_rand_gen.shuffle(gps)
        for gp in gps:
            nr_cells_in_gp = len(gp.content.get_cells())
            if nr_cells_in_gp >= max_pop_per_gp:
                continue
            competitors = []
            #get neighborhood localities
            neighborhood_localities = orderedset.OrderedSet(gp.neighbors(neighborhood))
            '''Ensuring that we do not look at the same locality more than once due to grid wrapping.'''
            for locality in neighborhood_localities:
                competitors += locality.get_cells()
            if self.params.cell_division_volume is not None:
                competitors = [ c for c in competitors if c.volume >= self.params.cell_division_volume ]
            new_gp_offspring = []
            # scale non with size of the neighborhood and the maximum density per gp
            gp_non = non * len(neighborhood_localities) * self.params.max_cells_per_locality
            if self.params.reproduce_size_proportional:
                new_gp_offspring = self.reproduce_size_proportional(time=time, competitors=competitors,
                                                                 max_reproduce=(max_pop_per_gp - nr_cells_in_gp),
                                                                 non=gp_non)
            elif self.params.reproduction_cost is None or time < self.params.grace_time:
                new_gp_offspring = self.reproduce_production_proportional(time=time,competitors=competitors,
                                                                          max_reproduce=(max_pop_per_gp - nr_cells_in_gp),
                                                                          non=gp_non)
            else:
                new_gp_offspring = self.reproduce_at_minimum_production(time=time,competitors=competitors,
                                                                          max_reproduce=max((max_pop_per_gp - nr_cells_in_gp),0)
                                                                          )
            for cell in new_gp_offspring:
                new_offspring_gp_dict[cell] = gp
        return new_offspring_gp_dict

    def mutate_new_offspring(self, time, environment,
                             rand_gen=None, rand_gen_np=None):
        if rand_gen is None:
            rand_gen = self.evo_rand_gen
        if rand_gen_np is None:
            rand_gen_np = self.evo_rand_gen_np
        for cell in self.new_offspring:
            cell.mutate(time=time, environment=environment,
                        rand_gen=rand_gen, rand_gen_np=rand_gen_np)

    def horizontal_transfer(self, time, grid, environment, rand_gen=None, rand_gen_np=None):
        """
        Applies HGT to all cells in the grid

        Parameters
        ----------
        grid : needed for internal HGT and setting the update-flags
        environment: contains all possible reactions to draw a random gene for external HGT
        rand_gen: RNG

        Returns
        -------
        -
        """
        if rand_gen is None:
            rand_gen = self.evo_rand_gen
        hgt_gp_dict = collections.OrderedDict()
        gps = list(grid.gp_iter)    # Iterator for all GPs
        for gp in gps:
            for cell in gp.content.get_cells():

                applied = cell.apply_hgt(time=time, gp=gp,
                                         environment=environment, rand_gen=rand_gen, verbose=False)
                if applied:
                    hgt_gp_dict[cell] = gp
        return hgt_gp_dict


    def update_offspring_regulatory_network(self, min_bind_score=None): # if min_bind_score is None, it will default to the parameter
        for cell in self.new_offspring:
            cell.update_grn(min_bind_score)

    def grow_time_course_arrays(self):
        for cell in self.cells:
            cell.grow_time_course_arrays()

    def clear_mol_time_courses(self, ):
        for cell in self.cells:
            if not cell.alive:
                cell.clear_mol_time_courses()

    def resize_time_courses(self, new_max_time_points):
        '''resize the arrays that can hold time course information
        of cellular concentrations etc.

        :param new_max_time_points: new length of time course array
        '''
        for cell in self.cells:
            cell.resize_time_courses(new_max_time_points)

    def reset_production_toxicity_volume(self, cells=None):
        if cells is None:
            cells = self.cells
        for cell in cells:
            cell.raw_production = 0.
            cell.toxicity = 0.
            cell.volume = self.params.cell_init_volume

    def mark_cells_metabolic_type(self, cells=None):
        if cells is None:
            cells = self.cells
        min_mark, max_mark = self.markers_range_dict['metabolic_type']
        for cell in cells:
            try:
                mark = self.metabolic_type_marker_dict.index_key(cell.metabolic_type)
            except (StopIteration, IndexError):
                self.prune_metabolic_types()
                mark = self.metabolic_type_marker_dict.index_key(cell.metabolic_type)

            cell.mark('metabolic_type', mark)
            if mark < min_mark:
                min_mark = mark
            if mark > max_mark:
                max_mark = mark
        self.markers_range_dict['metabolic_type'] = (min_mark, max_mark)
        return min_mark, max_mark

    def cell_markers(self,marker,cells=None):
        if cells is None:
            cells = self.cells
        return orderedset.OrderedSet([cell.marker_dict[marker] for cell in cells])

    def update_lineage_markers(self, cells=None, min_nr_marks=None):
        if min_nr_marks is None:
            min_nr_marks = self.params.min_lineage_marking
        if cells is None:
            cells = self.cells
        if len(self.cell_markers('lineage', cells)) <= min_nr_marks:
            self.mark_cells_lineage(cells)

    def mark_cells_lineage(self, cells=None):
        min_mark, max_mark = self.markers_range_dict['lineage']
        marker_iter = it.count()
        if cells is None:
            cells = self.cells
        for cell in cells:
            mark = marker_iter.next()
            if mark < min_mark:
                min_mark = mark
            if mark > max_mark:
                max_mark = mark
            cell.mark('lineage', mark)
        self.markers_range_dict['lineage'] = (min_mark, max_mark)
        return (min_mark, max_mark)

    def average_death_rate(self, cells=None):
        return np.average(self.death_rates(cells))

    def average_production(self, cells=None):
        return np.average(self.production_values(cells))

    def marker_counts(self, marker, cells=None):
        return self.pop_marker_counts(marker, cells)

    def pop_marker_counts(self, marker_name, cells=None):
        if cells is None:
            cells = self.cells
        return collections.Counter([cell.marker_dict[marker_name] for cell in cells])

    def most_abundant_marker(self, marker_name, cells=None):
        if cells is None:
            cells = self.cells
        most_abundant = self.pop_marker_counts(marker_name, cells).most_common(1)
        if most_abundant:
            return most_abundant[0][0]
        else:
            return -1

    def upgrade(self):
        '''
        Upgrading from older pickled version of class to latest version. Version
        information is saved as class variable and should be updated when class
        invariants (e.g. fields) are added.
        '''
        version = float(self.version)
        if version < 1.:
            pass
        self.version = self.class_version
        if version > float(self.class_version):
            print 'upgraded class',
        else:
            print 'reset class',
        print self.__class__.__name__, ' from version', version ,'to version', self.version

    def __getstate__(self):
        odict = dict()  # NOTE: unordered ok
        for k, v in self.__dict__.iteritems():
            if k in ['current_ancestors', 'roots']:
                odict[k] = v._pickle_repr()
            elif k in ['cells', 'phylo_tree']:
                pass
            else:
                odict[k] = v
        return odict

    def __setstate__(self, obj_dict):
        for k, v in obj_dict.iteritems():
            if k in ['current_ancestors', 'roots']:
                setattr(self, k, util.LinkThroughSet._unpickle_repr(v))
            else:
                setattr(self, k, v)
        self.init_cells_view()
        self.init_phylo_tree()
        if not hasattr(self, 'version'):
            self.version = '0.0'
        if self.version != self.class_version:
            self.upgrade()

    def __getitem__(self, key):
        return self.params[key]
