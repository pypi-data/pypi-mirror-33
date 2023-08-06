from __builtin__ import int
import collections
import copy
import glob
import os
import random
import re
import shutil

from VirtualMicrobes.cython_gsl_interface import integrate
from VirtualMicrobes.environment.Environment import Locality
from VirtualMicrobes.readwrite import write_obj
import VirtualMicrobes.my_tools.utility as util
from VirtualMicrobes.plotting.Graphs import BindingNetwork, MetabolicNetwork, Genome, PhyloTreeGraph
import VirtualMicrobes.simulation.Simulation as simu
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def _plot_cell_graphs(cell, GRN_grapher, metabolome_grapher, genome_grapher, max_genome_size, suffixes):
    '''
    Draw all graphs for cell

    Parameters
    ----------
    cell : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
    GRN_grapher : :class:`VirtualMicrobes.plotting.Graphs.BindingNetwork`
        draws gene regulatory network graphs
    metabolome_grapher : :class:`VirtualMicrobes.plotting.Graphs.MetabolicNetwork`
        draws metabolic network
    genome_grapher : :class:`VirtualMicrobes.plotting.Graphs.Genome`
        draws genome layout graphs
    '''
    #for nodes in cell.nodes_edges():
    #    print str(nodes[1])

    GRN_grapher.init_network(cell)
    GRN_grapher.layout_network_positions(prog='nwx')
    GRN_grapher.redraw_network()
    GRN_grapher.update_figure()

#    label_set.append('apo')

    for suffix in suffixes:
        GRN_grapher.save_fig(labels=[str(cell.time_birth).zfill(10), 'nwx'], suffix=suffix, bbox_inches='tight')
    GRN_grapher.layout_network_positions(prog='dot')
    GRN_grapher.redraw_network()
    GRN_grapher.update_figure()
    for suffix in suffixes:
        GRN_grapher.save_fig(labels=[str(cell.time_birth).zfill(10), 'bound', 'dot'], suffix=suffix, bbox_inches='tight')

    GRN_grapher.redraw_network(edge_effect='effectApo')
    GRN_grapher.update_figure()
    for suffix in suffixes:
        GRN_grapher.save_fig(labels=[str(cell.time_birth).zfill(10), 'apo', 'dot'], suffix=suffix, bbox_inches='tight')

    GRN_grapher.write_to_file(labels=[str(cell.time_birth).zfill(10), 'apo','dot'],suffix='.dot')
# grn.init_network(cell)
# grn.layout_network_positions(prog=prog)
# for effect in edge_effects:
#     grn.redraw_network(self_marker=True, edge_effect=effect)
#     grn.update_figure()
#     if save:
#         saved = []
#         for ext, label_sets in fig_ext_label_dict.items():
#             fn = grn.save_fig2(ext,title=title)
#             for label_set in label_sets:
#                 label_set = label_set[:]
#                 if effect == 'effect_apo':
#                     label_set.append('apo')
#                 label_set.append(prog)
#                 save_file = "_".join([fn] + map(str,label_set)) + '.' + ext
#                 shutil.copy2(fn, save_file)
#                 saved.append(save_file)
#             os.remove(fn)
#
#         if video is not None:
#             for save_file in saved:
#                 if os.path.basename(save_file) ==  video_frame_name:
#                     grn.save_video(video, frame=save_file)
#
#     if write:
#         for ext, label_sets in text_ext_label_dict.items():
#             for label_set in label_sets:
#                 if effect == 'effect_apo':
#                     label_set.append('apo')
#                 grn.write_to_file(labels=label_set, suffix=ext)

    GRN_grapher.clear_graph()
    #metabolome_grapher.redraw_network(reactions_dict=cell.reaction_set_dict,
    #                                  building_blocks=cell.building_blocks)
    #metabolome_grapher.update_figure()
    #for suffix in suffixes:
    #    metabolome_grapher.save_fig(labels=[str(cell.time_birth).zfill(10)], suffix=suffix, bbox_inches='tight')

    genome_grapher.plot_genome_structure(cell, labels=[str(cell.time_birth).zfill(10)],
                                         max_size=max_genome_size)
    genome_grapher.update_figure()
    for suffix in suffixes:
        genome_grapher.save_fig(labels=[str(cell.time_birth).zfill(10)], suffix=suffix)

def _plot_cell_time_course(cell, sim_graphs, save_dir, suffixes):
    '''
    Plot all time courses within the life span of an individual.

    Parameters
    ----------
    cell : :class:`VirtualMicrobes.virtual_cell.Cell.Cell`
    sim_graphs : :class:`VirtualMicrobes.plotting.Graphs.Graphs`
        simulation grapher object that draws the plots
    save_dir : str
    suffixes : list of file suffixes
    '''

    fig = plt.figure(figsize=(12,12))
    mol_ax = fig.add_subplot(321)
    mol_ax.set_title('internal molecule conc')
    prot_ax = fig.add_subplot(323)
    prot_ax.set_title('protein concentration')
    size_ax = fig.add_subplot(322)
    size_ax.set_title('cell size')
    tox_ax = fig.add_subplot(324)
    tox_ax.set_title('toxicity')
    prod_ax = fig.add_subplot(326)
    prod_ax.set_title('production')

    size_dat = cell.get_cell_size_time_course()
    if not len(size_dat[0,:]):
        return

    mol_dat = cell.get_mol_time_course_dict()
    prot_dat = cell.get_gene_type_time_course_dict()

    tox_dat = cell.get_toxicity_time_course()
    prod_dat = cell.get_raw_production_time_course()

    sim_graphs.plot_mol_class_data(mol_ax, mol_dat)
    sim_graphs.plot_prot_data(prot_ax, prot_dat)
    title = size_ax.get_title()
    size_ax.clear()
    size_ax.set_title(title)
    size_ax.plot(size_dat[0,:],size_dat[1,:])

    title = tox_ax.get_title()
    tox_ax.clear()
    tox_ax.set_title(title)
    tox_ax.plot(tox_dat[0,:], tox_dat[1,:])

    title = prod_ax.get_title()
    prod_ax.clear()
    prod_ax.set_title(title)
    prod_ax.plot(prod_dat[0,:], prod_dat[1,:])

    for suffix in suffixes:
        fig.savefig(os.path.join(save_dir,'time_course_'+str(cell.time_birth).zfill(10)+suffix),
                     bbox_inches='tight')

def _lod_time_course_data(ancestors, base_save_dir, viewer_path, chunk_size=100 ):
    '''
    Write time series data in the line of descent.

    Concatenates time courses of individuals along a :class:`LOD`.
    Concatenations are done in *chunks* of a chosen `chunk_size`. For each chunk
    **.csv** files are stored in a directory named part*n*, where *n* is the
    chunk number.

    Parameters
    ----------
    ancestors : list of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`\s
    base_save_dir : str
    viewer_path : str
        path to utility files for html data viewer
    chunk_size : int
        length of chunks of concatenated data
    '''

    # divide the ancestors in LOD into chunks; concatenate time courses per chunk
    for part, anc_chunk in enumerate(util.chunks(ancestors, chunk_size)):
        num = str(part).zfill(5)
        save_dir = os.path.join(base_save_dir, 'part{}'.format(num))
        util.ensure_dir(save_dir)

        for filename in glob.glob(os.path.join(viewer_path, '*')):
            shutil.copy2(filename, save_dir)

        prod_series = []
        cell_size_series = []
        tox_series = []
        mol_dfs = []
        prot_dfs = []
        for anc in anc_chunk:

            # production data
            ts_dat =  anc.get_raw_production_time_course()
            ts = pd.Series(data=ts_dat[1], index=ts_dat[0])
            prod_series.append(ts)

            # cell size data
            ts_dat =  anc.get_cell_size_time_course()
            ts = pd.Series(data=ts_dat[1], index=ts_dat[0])
            cell_size_series.append(ts)

            # toxicity data
            ts_dat =  anc.get_toxicity_time_course()
            ts = pd.Series(data=ts_dat[1], index=ts_dat[0])
            tox_series.append(ts)

            # metabolite data
            mol_time_courses = anc.get_mol_time_course_dict()
            mol_series = dict()
            for mol, tc in mol_time_courses.items():
                mol_series[mol] = pd.Series(data=tc[1], index=tc[0], name=mol)
            mol_df = pd.DataFrame(mol_series)
            mol_dfs.append(mol_df)

            # protein data
            prot_time_courses = anc.get_total_reaction_type_time_course_dict()
            prot_series = dict()
            for _reac_type, tc_dict in prot_time_courses.items():
                for reac, tc in tc_dict.items():
                    if isinstance(reac, tuple):
                        reac, exp = reac
                        name = str(reac)
                        name += '-e' if exp else '-i'
                    else:
                        name = str(reac)
                    prot_series[name] = pd.Series(data=tc[1],
                                                   index=tc[0],
                                                   name=name )
            prot_df = pd.DataFrame(prot_series)
            prot_dfs.append(prot_df)

        # concatenate each data type and write to file
        prod_series = pd.concat(prod_series)
        prod_series = prod_series[~prod_series.index.duplicated(keep='last')]
        ts_base_name = os.path.join(save_dir,'production_time_course')
        prod_series.to_csv(ts_base_name+'.csv', index_label='time point')

        cell_size_series = pd.concat(cell_size_series)
        cell_size_series = cell_size_series[~cell_size_series.index.duplicated(keep='last')]
        ts_base_name = os.path.join(save_dir,'cell_size_time_course')
        cell_size_series.to_csv(ts_base_name+'.csv', index_label='time point')

        tox_series = pd.concat(tox_series)
        tox_series = tox_series[~tox_series.index.duplicated(keep='last')]
        ts_base_name = os.path.join(save_dir,'toxicity_time_course')
        tox_series.to_csv(ts_base_name+'.csv', index_label='time point')

        mol_df_combine = pd.concat(mol_dfs)
        mol_df_combine = mol_df_combine[~mol_df_combine.index.duplicated(keep='last')]
        df_base_name = os.path.join(save_dir,'mol_time_courses')
        mol_df_combine.to_csv(df_base_name+'.csv', index_label='time point')

        prot_df_combine = pd.concat(prot_dfs)
        prot_df_combine = prot_df_combine[~prot_df_combine.index.duplicated(keep='last')]
        df_base_name = os.path.join(save_dir,'prot_time_courses')
        prot_df_combine.to_csv(df_base_name+'.csv', index_label='time point')

class LOD_Analyser(object):
    '''
    Analyses the evolutionary history of a population by tracing ancestors in the
    line of descent.

    Loads a simulation save from a file, keeping a reference in :attr:`ref_sim`.
    From this, initialise :attr:`ref_pop_hist` as a :class:`PopulationHistory`
    object that analyses  the phylogenetic tree of the population.

    The :class:`PopulationHistory` generates a :class:`LOD` for 1 or more
    individuals in the saved population. For each :class:`LOD`, evolutionary
    data and network and genome plots can be produced.

    It is possible to load additional simulation snapshots that preceed the
    :attr:`ref_pop_hist` and compare individuals to their contemporaries present
    in the preceding populations. :attr:`compare_saves` contains a list of file
    names of populations-saves that should be compared.
    '''

    args = None
    '''config and command line arguments used for initialisation'''

    ref_sim = None
    ''':class:`VirtualMicrobes.simulation.Simulation` snapshot to analyse'''

    ref_pop_hist = None
    ''':class:`PopulationHistory` for the reference simulation (`ref_sim`) snapshot '''

    compare_saves = []
    '''names of snapshot files to copmare to `ref_sim`'''

    def __init__(self, args):
        '''
        Initialize the analyzer from an argument dictionary.

        Load the population save from file :param:`args`.pop_save and initialize
        special fields in its :class:`data_tools.store.DataStore` that can hold
        ancestor tracing data. From :attr:`ref_sim` initialize :attr:`ref_pop_hist`
        as a :class:`PopulationHistory` that can be used to generate and analyze
        the evolutionary history of the population stored in :attr:`ref_sim`.

        Parameters
        ----------
        args : dict
            arguments attribute dictionary
        '''

        self.args = args
        self.init_compare_saves(args.compare_saves)
        self.ref_sim = simu.load_simulation(args.pop_save, **vars(args))
        print 'historic maximum of production medium:', self.ref_sim.system.population.historic_production_max
        self.init_ref_history()


    def init_compare_saves(self, compare_saves):
        '''
        Parse and check compare saves parameter.

        Compare saves can be either a list of file names or a list of generation
        times (or None). In the latter case, the file names should be
        constructed using the time point and the file name of the reference
        simulation. Checks are made to ensure files exist and also to ensure
        that no compares save points come after the reference simulation save
        point, as this would not make sense in the comparison functions.
        '''
        gen_re = re.compile(r'(\d+)(?=\.sav)')
        if compare_saves is None:
            self.compare_saves = compare_saves
            return
        elif all(map(lambda v: isinstance(v, int), compare_saves)):
            sub = lambda i: gen_re.sub(str(i), self.args.pop_save)
            self.compare_saves = map(sub, compare_saves)
        else:
            self.compare_saves = compare_saves

        m = gen_re.search(self.args.pop_save)
        if m:
            ref_gen = int(m.group(0))
        else:
            raise Exception('Could not find a generation time for pop_save "{}"'.format(self.args.pop_save))
        for f in self.compare_saves:
            if not os.path.exists(f):
                raise Exception('compare save file "{}" could not be found'.format(f))
            m = gen_re.search(f)
            if m:
                gen = int(m.group(0))
                if gen > ref_gen:
                    raise Exception('Can not compare a save point "{}"'
                                    ' beyond the simulation time "{}" '
                                    'of the reference simulation'.format(gen, ref_gen))
            else:
                raise Exception('Could not find a generation time '
                                'for compare save "{}"'.format(f))

    def init_ref_history(self, ref_sim=None, nr_lods=None,
                         prune_depth=0, pop_hist_dir='population_history'):
        '''
        Create a :class:`PopulationHistory` from the :attr:`ref_sim`
        :class:`VirtualMicrobes.simulation.Simulation.Simulation` object.

        For the :class:`PopulationHistory` object constructs its phylogenetic tree
        and prune back the tree to a maximum depth of (max_depth - prune_depth)
        counted from the root. Then create :class:`LOD` objects representing
        the *line of descent* of the `nr_lods` *most diverged* branches in the tree.

        Parameters
        ----------

        ref_sim : :class:`VirtualMicrobes.simulation.Simulation.Simulation` object
            simulation snapshot that is the basis for `LOD` analysis

        nr_lods : int nr_lods
            nr of separate (most distant) :class:`LOD`\s to initialize

        prune_depth : int
            prune back the phylogenetic tree with this many timesteps

        pop_hist_dir : str
            name of directory to store lod analysis output

        '''
        if ref_sim is None:
            ref_sim = self.ref_sim
        if nr_lods is None:
            nr_lods = self.args.nr_lods
        tp = ref_sim.run_time
        save_dir = os.path.join(ref_sim.save_dir, pop_hist_dir+'_'+str(tp))
        self.ref_pop_hist = PopulationHistory(sim=self.ref_sim,
                                          params=self.ref_sim.params,
                                          save_dir=save_dir,
                                          prune_depth=prune_depth)
        self.ref_pop_hist.init_phylo_tree()
        self.ref_pop_hist.init_lods(nr_lods)
        self.ref_pop_hist._init_pop_hist_data_store()

    def compare_to_pops(self):
        '''
        Compare reference simulation to a set of previous population snapshots.

        Compares each of the simulation snapshot saves in :attr:`compare_saves`
        to the :attr:`ref_pop_hist`. A :class:`PopulationHistory` is constructed for
        each of the compare snapshots. Within the compare snapshot, individuals
        that correspond to the are part of (any of) the :class:`LOD`(s) of the
        :attr:`ref_pop_hist` will be identified. Properties of these *ancestors*
        will then be compare with their statistical values for the whole
        population.
        '''
        # TODO check that compare saves are not older than the reference
        # and raise error when it is the case:
        if not self.args.skip_store:
            self.ref_sim.data_store.init_ancestry_compare_stores(self.ref_pop_hist)
        for compare_save in sorted(self.compare_saves, key=lambda n: int(n.strip('.sav').split('_')[-1])):
            self.ref_pop_hist.compare_to_pop(compare_save)

    def lod_stats(self, stride=None, time_interval=None, lod_range=None):
        '''
        Write time series of evolutionary changes along all :class:`LOD`\s.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`
        '''
        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        print 'Running LOD stats'
        self.ref_pop_hist.lod_stats(stride, time_interval, lod_range)

    def lod_cells(self, stride=None, time_interval=None, lod_range=None, runtime=None):
        '''
        Write time series of evolutionary changes along all :class:`LOD`\s.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`
        '''
        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        if runtime is None:
            runtime=-1
        print 'Saving LOD cells'
        self.ref_pop_hist.lod_cells(stride, time_interval, lod_range, runtime)

    def pop_cells(self, runtime=None):
        if runtime is None:
            runtime = -1
        '''Dump all cells in this save file'''
        self.ref_pop_hist.dump_pop_cells(runtime)

    def lod_network_stats(self,stride=None, time_interval=None,
                          lod_range=None):
        '''
        Write time series for evolutionary network property changes along all :class:`LOD`\s.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        '''
        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        print 'Running LOD Network stats'
        self.ref_pop_hist.lod_network_stats(stride, time_interval, lod_range)

    def lod_binding_conservation(self,  stride=None, time_interval=None,
                                 lod_range=None):
        '''
        Write time series for TF binding conservation for :class:`LOD`\s.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        '''
        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        print 'Running LOD binding conservation'
        self.ref_pop_hist.lod_binding_conservation(stride, time_interval,
                                                   lod_range)

    def draw_ref_trees(self):
        '''Draw a reference phylogenetic tree, with individual, selected :class:`LOD`\s marked'''
        self.ref_pop_hist.draw_ref_trees()

    def lod_graphs(self, stride=None, time_interval=None, lod_range=None, formats=None):
        '''Draw network and genome graphs for :class:`LOD`\s

        It is possible to set an interval and a range to sample individuals in
        the :class:`LOD`.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        Note
        ----
        Either use a stride or a time interval to sample individuals from the lod.
        '''

        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        if formats is None:
            formats = self.args.image_formats
        self.ref_pop_hist.plot_lod_graphs(stride, time_interval, lod_range, formats)

    def lod_time_courses(self, lod_range=None, chunk_size=None):
        '''
        Write time series of molecule concentrations within the :class:`LOD`

        It is possible to set a range to sample individuals in
        the :class:`LOD`.

        Parameters
        ----------
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`
        chunk_size : int
            number of generations in LOD to concatenate per chunk
        '''
        if lod_range is None:
            lod_range = self.args.lod_range
        if chunk_size is None:
            chunk_size = self.args.time_course_chunk_size
        self.ref_pop_hist.lods_time_course_data(lod_range, chunk_size)

    def lod_time_course_plots(self, stride=None, time_interval=None, lod_range=None, formats=None):
        '''
        Draw time course diagrams for individuals in the :class:`LOD`\s.

        It is possible to set an interval and a range to sample individuals in
        the :class:`LOD`.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        Note
        ----
        Either use a stride or a time interval to sample individuals from the lod.
        '''
        if stride is not None and time_interval is not None:
            raise Exception('defining both lod_generation_interval and lod_time_interval is not allowed')
        if stride is None:
            stride = self.args.lod_generation_interval
        if time_interval is None:
            time_interval = self.args.lod_time_interval
        if lod_range is None:
            lod_range = self.args.lod_range
        if formats is None:
            formats = self.args.image_formats
        self.ref_pop_hist.lods_time_course_plots(stride, time_interval, lod_range, formats)

    def write_newick_trees(self):
        '''write newick trees for all phylogenies in attr:`ref_pop_hist`'''
        self.ref_pop_hist.write_newick_trees()

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        self.ref_sim.close_phylo_shelf()

    def __str__(self):
        return str(self.ref_pop_hist)

class PopulationHistory(object):
    '''
    Performs and stores evolutionary history analysis of
    :class:`VirtualMicrobes.simulation.Simulation.Simulation` snapshots.

    Generates :class:`LOD`\s for 1 or more individuals in the population.
    Reconstruct the evolutionary events along the line of descent.

    A reference :class:`PopulationHistory` can also be compared to *population
    history* at earlier simulation time points. In this case the ancestors of
    individuals in the reference *population history* will be identified and
    compared to the rest of the population at that point in time. In this way,
    evolutionary biases on the line of descent can be brought to light.
    '''

    sim = None
    '''The :class:`VirtualMicrobes.simulation.Simulation.Simulation` snapshot for which this pophist was made.'''

    params = None
    '''The (updated) simulation parameters.'''

    prune_depth = 0
    '''Number of generations from leaves to prune the phylogenetic tree of the pophist.'''

    population = None
    '''Short cut to :class:`VirtualMicrobes.virtual_cell.Population.Population` of `sim`.'''

    environment = None
    '''Short cut to :class:`VirtualMicrobes.environment.Environment` of `sim`.'''

    time_point = None
    '''Last simulation time of the `sim`.'''

    tree_lods = []
    '''List of lists of :class:`LOD`\s. One list for each independent phylogenetic tree within the population.'''

    def __init__(self, sim, params, save_dir=None ,prune_depth=None):
        '''
        Set parameters for phylogenetic analysis.

        Parameters
        ----------
        sim : :class:`VirtualMicrobes.simulation.Simulation.Simulation
        params : dict
            the simulation parameters
        save_dir : str
            path to save analysis data to
        prune_depth : int
            number of generations to prune from the leafs of phylogenetic tree
        '''

        self.save_dir = save_dir
        if self.save_dir is not None:
            util.ensure_dir(self.save_dir)
        self.sim = sim
        self.params = params
        self.prune_depth = prune_depth
        self.population = sim.system.population
        for anc in self.population.current_ancestors:
            if self.params.reconstruct_grn:
                anc.update_grn()
        self.environment = sim.system.environment
        self.time_point = sim.run_time
        self._init_rand_gens()
        self._init_test_bed()
        self.tree_lods = list()

    def init_phylo_tree(self, prune_depth=None):
        '''
        Update the phylogenetic tree of the population.

        Clears the change in the population of the final regular simulation
        step. Prunes back the tree to a maximum depth.

        Parameters
        ----------
        prune_depth : int
            number of generations to prune from the leafs of phylogenetic tree
        '''

        if prune_depth is None:
            prune_depth = self.prune_depth
        self.population.clear_pop_changes()
        self.population.update_phylogeny()
        self.population.phylo_tree.to_ete_trees()
        for root_id, ete_tree_struct in self.population.phylo_tree.ete_trees.items():
            print 'pruning ete tree', root_id
            if prune_depth is not None:
                max_depth = self.population.phylo_tree.max_depth
                print 'tree has depth', max_depth
                self.population.phylo_tree.ete_prune_external(ete_tree_struct, max(0, max_depth - prune_depth))

    def init_lods(self, nr_lods, save_dir=None,
                  stride=None, time_interval=None, lod_range=None):
        '''
        Initialize the line of descent (:class:`LOD`) container objects.

        Iterate over the phylogenetic trees of the :attr:`population` and for
        each tree select `nr_lods` leaf nodes that are at maximum phylogenetic
        distance.

        For each of the selected leafs, construct a line of descent object
        (:class:`LOD`).

        Parameters
        ----------
        nr_lods : int
            number of :class:`LOD` objects per phylogenetic tree
        save_dir : str
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`
        '''

        if save_dir is None:
            save_dir = self.save_dir
        if stride is None:
            stride = self.params.lod_generation_interval
        if time_interval is None:
            time_interval = self.params.lod_time_interval
        if lod_range is None:
            lod_range = self.params.lod_range

        # iterate (potentially multiple) phylogenetic trees for the population
        for root_id, ete_tree_struct in self.population.phylo_tree.ete_trees.items():

            tree_save_dir = root_id.split('_')[0]

            print 'constructing lines of descent for ete tree', root_id
            leafs = self.population.phylo_tree.ete_n_most_distant_phylo_units(ete_tree_struct, nr_lods)
            if sum( [ not leaf.has_living_offspring() for (leaf, _ete_node) in leafs ]):
                raise Exception('leaf with no living offspring found')
            print 'done'
            lods = collections.OrderedDict()

            # print information on the phylogenetic distances between leafs
            for l1, l2, t_dist, top_dist in self.population.phylo_tree.distances(ete_tree_struct.tree,leafs):
                print l1.id, '-->', l2.id, ': time_dist :', t_dist, 'topology_dist :', top_dist

            for leaf, _ete_node in leafs:
                for lod in leaf.lods_up(): # in a clonal (the default) population, there is only 1 lod per leaf
                    name = str(leaf.id)
                    lod_save_dir = os.path.join(save_dir, tree_save_dir, name)
                    lods[leaf] = LOD(list(lod), name=name, save_dir = lod_save_dir,
                                          stride=stride, time_interval=time_interval, lod_range=lod_range)
                    break # record 1 lod per leaf (in clonal pop, there is only 1 per leaf)
            self.tree_lods.append((ete_tree_struct,lods))

    def _init_pop_hist_data_store(self):
        '''Configure the DataStore for PopulationHistory data.'''
        self.sim.data_store.init_phylo_hist_stores(phylo_hist=self)

    def identify_lod_ancestor(self, ete_tree_struct, lod):
        '''
        Identify the individual in the population that is on the line of descent
        (lod) under consideration.

        The nodes in the ete tree corresponding to the *lod* will be annotated
        with a tag.

        Parameters
        ----------
        ete_tree_struct : :class:`VirtualMicrobes.my_tools.utility.ETEtreeStruct`
            container structure for phylogenetic tree representations
        lod :  :class:`LOD`
            line of descent

        Returns
        -------
        (:class:`VirtualMicrobes.virtual_cell.Cell.Cell`, :class:`ete3.TreeNode`)
        (oldest ancestor cell, its tree node representation)
        '''
        last, last_ete = None, None

        phylo2ete_dict = self.population.phylo_tree.ete_get_phylo2ete_dict(ete_tree_struct)
        phylo_id2phylo = dict([ ( (str(phylo_unit.id),phylo_unit.time_birth), phylo_unit)
                          for phylo_unit in phylo2ete_dict ])

        for anc in lod.lod: # going from oldest to youngest
            anc_id = (str(anc.id), anc.time_birth)
            if anc_id not in phylo_id2phylo:  # reached an ancestor that lives later than the leafs in the tree
                break
            last = phylo_id2phylo[anc_id]
            last_ete = phylo2ete_dict[last][0]
            for ete_node in phylo2ete_dict[last]:
                ete_node.add_feature('lod', True) # annotate the ete nodes as being on the lod
        return last, last_ete

    def _init_rand_gens(self, rand_seed=None):
        if rand_seed is None:
            test_rand_seed = self.params.test_rand_seed
        self.test_rand = random.Random(int(test_rand_seed))

    def _init_test_bed(self):
        self.test_bed = Locality(self.params,
                                 internal_molecules=self.environment.internal_molecules,
                                 influx_reactions=self.environment.influx_reactions,
                                 degradation_reactions=self.environment.degradation_reactions,
                                 env_rand=self.test_rand )

    def _init_integrator(self, diffusion_steps=None, between_diffusion_reports=None,
                        max_retries=3, retry_steps_factor=2.):
        if diffusion_steps is None:
            diffusion_steps = self.params.diffusion_steps
        if between_diffusion_reports is None:
            between_diffusion_reports = self.params.between_diffusion_reports
        max_time_steps_store = max(int(diffusion_steps * between_diffusion_reports
                                * retry_steps_factor ** (max_retries)), 1)
        integrator = integrate.Integrator(locality = self.test_bed, # @UndefinedVariable
                                          nr_time_points=max_time_steps_store,
                                          nr_neighbors=0,
                                          num_threads=1,
                                          step_function=self.params.step_function,
                                          hstart=self.params.init_step_size,
                                          epsabs=self.params.absolute_error,
                                          epsrel=self.params.relative_error,
                                          init_time=0.)
        return integrator

    def write_newick_trees(self):
        '''
        Write newick representation of phylogenetic trees to files.
        '''
        for ete_tree_struct, _lods in self.tree_lods:
            name = ete_tree_struct.tree.name.split('_')[0]
            filename = 'tree' + '_' + name
            suffix = '.nw'
            ete_tree_struct.tree.write(format=1,
                                       outfile=os.path.join(self.save_dir,
                                                            filename + suffix))

    def lod_stats(self, stride, time_interval, lod_range):
        '''
        Write time series for line of descent properties such as network
        connectivity, protein expression etc.

        Either use a stride or a time interval to sample individuals from the lod.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`
        '''
        cumulative_features = self.sim.data_store.mut_stats_names + self.sim.data_store.fit_stats_names + ['iterage']
        simple_features = self.sim.data_store.functional_stats_names
        for ete_tree_struct, lods in self.tree_lods:
            self.population.annotate_phylo_tree(ete_tree_struct=ete_tree_struct,
                                                 features=cumulative_features)
            self.population.annotate_phylo_tree(ete_tree_struct=ete_tree_struct,
                                                 features=simple_features, cummulative=False)
            for ref, lod in lods.items():
                print ref.id
                self.sim.data_store.add_lod_data(ete_tree_struct, lod,
                                                 self.population, self.environment,
                                                 stride, time_interval, lod_range)
        print 'done'

    def lod_cells(self, stride, time_interval, lod_range, runtime):
        '''
        Write cell files for line of descent

        The leaf of the tree is saved as CellLeaf<LOD_ID>, and all it's ancestors are saved as CellNode<BIRTHTIME>_<LOD_ID>.cell

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`
        '''
        for _, lods in self.tree_lods:
            for ref, lod in lods.items():
                print 'saving cells for ' , ref.id
                self.sim.data_store.save_lod_cells(lod, stride, time_interval, lod_range,runtime)
        print 'done'



    def lod_network_stats(self, stride, time_interval, lod_range):
        '''
        Write time series for line of descent properties such as network
        connectivity, protein expression etc.

        Either use a stride or a time interval to sample individuals from the lod.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        '''
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'lod', ref.id
                self.sim.data_store.add_lod_network_data(lod, stride,
                                                         time_interval,
                                                         lod_range)
        print 'done'

    def lod_binding_conservation(self, stride, time_interval, lod_range):
        '''
        Write time series for line of descent properties such as network
        connectivity, protein expression etc.

        Either use a stride or a time interval to sample individuals from the lod.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        '''
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'lod', ref.id
                self.sim.data_store.add_lod_binding_conservation(lod, stride,
                                                                 time_interval,
                                                                 lod_range)
        print 'done'

    def plot_lod_graphs(self, stride, time_interval, lod_range, formats):
        '''
        Output metabolic, GRN and genome graphs for the line of descent.

        Either use a stride or a time interval to sample individuals from the lod.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        '''
        metabolites = self.environment.mols_per_class_dict
        conversions = self.environment.reactions_dict['conversion']
        imports = self.environment.reactions_dict['import']

        suffixes = map(lambda fmt: '.'+fmt, formats)
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'adding network graphs for lod', str(ref.id)
                attr_dict = self.sim.graphs.attribute_mapper
                GRN_grapher = BindingNetwork(lod.save_dir, 'GRN', attribute_dict=attr_dict, show=False)
                metabolome_grapher = MetabolicNetwork(lod.save_dir, 'Metabolome',
                                                      mol_class_dict=metabolites,
                                                      conversions=conversions,
                                                      imports=imports,
                                                      attribute_dict=attr_dict, show=False)
                genome_grapher = Genome(lod.save_dir, 'Genome', attribute_dict=attr_dict, show=False) # Initialise grapher for genome structure (and make directory)
                ancestors = lod.strided_lod(stride, time_interval, lod_range)
                max_genome =  max( [ anc.genome_size for anc in ancestors ] )
                for anc in ancestors:
                    _plot_cell_graphs(anc, GRN_grapher, metabolome_grapher, genome_grapher, max_genome, suffixes)

    def lods_time_course_plots(self, stride, time_interval, lod_range, formats):
        '''
        Output time course graphs for the line of descent.

        Either use a stride or a time interval to sample individuals from the lod.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        '''
        suffixes = map(lambda fmt: '.'+fmt, formats)
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'lod', ref.id
                save_dir = os.path.join(lod.save_dir, 'time_course_plots')
                util.ensure_dir(save_dir)
                ancestors = lod.strided_lod(stride, time_interval, lod_range)
                for anc in ancestors:
                    _plot_cell_time_course(anc, self.sim.graphs,
                                         save_dir = save_dir, suffixes=suffixes)

    def lods_time_course_data(self, lod_range, chunk_size):
        '''
        Write time series data in the line of descent to files.

        Concatenates time courses of individuals along a :class:`LOD`.
        Concatenations are done in *chunks* of a chosen `chunk_size`. For each chunk
        **.csv** files are stored in a directory named part*n*, where *n* is the
        chunk number.

        Parameters
        ----------
        ancestors : list of :class:`VirtualMicrobes.virtual_cell.Cell.Cell`\s
        base_save_dir : str
        viewer_path : str
            path to utility files for html data viewer
        chunk_size : int
            length of chunks of concatenated data
        '''
        for ete_tree_struct, lods in self.tree_lods:
            print 'ete_tree', ete_tree_struct.tree.name
            for ref, lod in lods.items():
                print 'lod', ref.id
                save_dir = os.path.join(lod.save_dir, 'time_courses')
                util.ensure_dir(save_dir)
                ancestors = lod.strided_lod(stride=None, time_interval=None, lod_range=lod_range)
                _lod_time_course_data(ancestors, base_save_dir = save_dir,
                                     viewer_path=os.path.join(self.sim.utility_path, 'time_course_viewer'),
                                     chunk_size=chunk_size)

    def draw_ref_trees(self, rescale=False):
        '''
        Output reference trees for phylogenetic trees with lods labeled.

        Uses phylogenetic tree drawing methods to annotate the leaf nodes of
        lods. Reference trees give a visual overview of the position of the lods
        that are analysed in the tree.
        '''
        for ete_tree_struct, lods in self.tree_lods:

            save_loc = os.path.join(self.save_dir,
                        ete_tree_struct.tree.name.split('_')[0],
                        'ancestry_plots')

            util.ensure_dir(os.path.join(save_loc+'/reftree_cells'))
            cells_in_tree = self.population.phylo_tree.ete_nodes_to_phylo_units(ete_tree_struct)
            for cell in cells_in_tree:
                for parent in cell.parents:
                    write_obj.write_cell(cell, os.path.join(save_loc, 'reftree_cells/Node_'  + str(parent.id)+ '_' + str(cell.time_birth) + '.cell'), alive=True)

            for leaf, lod in lods.items():
                self.population.phylo_tree.annotate_phylo_units_feature(ete_tree_struct,
                                                                        lod.lod, 'in_lod')
                self.population.phylo_tree.annotate_leafs(ete_tree_struct, leaf)

            self.population.phylo_tree.ete_prune_internal(ete_tree_struct)

            func_features={'metabolic_type':self.population.metabolic_type_color}
            self.population.annotate_phylo_tree(ete_tree_struct,
                                                func_features=func_features,
                                                cummulative=False,
                                                prune_internal=True,
                                                to_rate=False
                                                )
            attr_dict = self.sim.graphs.attribute_mapper
            rescale_factor = None
            if rescale:
                rescale_factor = 500.0 / self.population.phylo_tree.ete_calc_lca_depth(ete_tree_struct.tree)
            print 'rescale factor is ', rescale_factor
            phylo_grapher = PhyloTreeGraph(save_loc, name='Phylotree', attribute_dict=attr_dict, show=False)
            phylo_grapher.update(ete_tree_struct.tree)
            phylo_grapher.save_fig(feature='metabolic_with_lod', name='lodstree',
                                   rescale=rescale_factor, dpi=10, suffix=".svg")
            print 'Plotted reference tree'

    def dump_pop_cells(self,time):
        # use dump_pop in simulation instead
        '''
        Output current population cells as cellfiles
        '''
        print 'Now saving all cellfiles of loaded population'
        directory = os.path.join(self.save_dir, 'pop_cells/', str(time))
        print directory
        util.ensure_dir(directory)
        for i,cell in enumerate(self.population.cells):
            write_obj.write_cell(cell, os.path.join(directory+'/Cellfile_inpop_'  + str(i)+'.cell'), alive=True)
        print 'Saved all cellfiles'

    def compare_to_pop(self, compare_save, prune_depth=None, leafs_sample_size=None):
        '''
        Compare the reference :class:`PopulationHistory` to an earlier population-save.

        Parameters
        ----------

        compare_save : str
            file location of population-save

        prune_depth : int
            prune back phylogeny of the :param:compare_save with this many timesteps

        leafs_sample_size : int
            maximum number of phylogenetic tree leafs to use for comparison
        '''
        if prune_depth is None:
            prune_depth = self.params.prune_compare_pop
        if leafs_sample_size is None:
            leafs_sample_size = self.params.leafs_sample_size

        params = copy.copy(self.params)
        params['name'] = os.path.join(params['name'], 'temp')
        compare_sim = simu.load_simulation(compare_save, **params)
        comp_pop_hist = PopulationHistory(sim=compare_sim,
                                     params=self.sim.params,
                                     prune_depth=prune_depth)
        comp_pop_hist.init_phylo_tree()
        comp_phylo_tree = comp_pop_hist.population.phylo_tree
        time_point = int(compare_save.strip('.sav').split('_')[-1])
        cumulative_features = (self.sim.data_store.mut_stats_names +
                               self.sim.data_store.fit_stats_names + ['iterage'] )
        for ref_ete_tree_struct, ref_lods in self.tree_lods:

            for comp_ete_tree_struct in comp_phylo_tree.ete_trees.values():
                if ref_ete_tree_struct.tree.name != comp_ete_tree_struct.tree.name:
                    # not comparing trees with the same root
                    continue

                comp_pop_hist.population.annotate_phylo_tree(ete_tree_struct=comp_ete_tree_struct,
                                                              features=cumulative_features)
                comp_dat = comp_ete_tree_struct, comp_pop_hist
                self.sim.data_store.add_ancestry_data_point(comp_dat, ref_lods,
                                                            time_point,
                                                            leafs_sample_size)
        compare_sim.close_phylo_shelf()

    def __str__(self):
        return '\n'.join([ str(lod) for tree_lods in self.tree_lods
                          for lod in tree_lods[1] ])

class LOD(object):
    '''
    classdocs
    '''

    def __init__(self, lod, name, stride, time_interval, lod_range,  save_dir=None):
        '''
        Store the line of descent to analyse.
        '''
        self.lod = lod
        self.name = name
        self.stride = stride
        self.time_interval = time_interval
        self.lod_range = lod_range
        self.save_dir = save_dir
        if self.save_dir is not None:
            util.ensure_dir(self.save_dir)

    def standardized_production(self, test_params):
        for c in self.lod:
            self.test_bed.clear_locality()
            self.test_bed.add_cell(c)
            integrator = self._init_integrator()
            self.run_system(integrator)

    def strided_lod(self, stride, time_interval, lod_range):
        '''
        Sample individuals within a range of the LOD at regular intervals.

        Either use a stride or a time interval to sample individuals from the
        lod. If a time interval is provided, ancestors are sampled that have a
        time of birth that is approximately separated by `time_interval` in the
        evolutionary simulation.

        Parameters
        ----------
        stride : int
            stride in generations for sampling individuals along the :class:`LOD`
        time_interval : int
            interval in simulation time for sampling individuals along the
            :class:`LOD`
        lod_range : (float,float)
            bounds in fractions of the total range of the :class:`LOD`

        Returns
        -------
        list of ancestor :class:`VirtualMicrobes.virtual_cell.Cell.Cell` s
        '''
        if lod_range is None:
            lod_range = (0.,1.)
        if stride is not None and time_interval is not None:
            raise Exception('defining both stride and time_interval is not allowed')
        lod_all = list(self)
        if stride is not None:
            ancestors = lod_all[::stride]
        elif time_interval is not None:
            ancestors = list(self.t_interval_iter(time_interval))
        else:
            ancestors = lod_all
        if ancestors[-1] != lod_all[-1]:
            ancestors.append(lod_all[-1])

        from_root, from_leaf = int(lod_range[0]*len(ancestors)), int(lod_range[1]*len(ancestors))
        return ancestors[from_root:from_leaf]

    def t_interval_iter(self, time_interval):
        '''
        Iterate ancestors that are approximately 'time_interval' timesteps apart
        in their time of birth.
        '''
        mod_time = time_interval
        for anc in self:
            prev_mod_time = mod_time
            mod_time = anc.time_birth % time_interval
            if mod_time > prev_mod_time:
                continue
            yield anc


    def __iter__(self):
        return iter(self.lod)

    def __str__(self):
        return '\t'+'\n\t'.join([ str(c) for c in self.lod ])
