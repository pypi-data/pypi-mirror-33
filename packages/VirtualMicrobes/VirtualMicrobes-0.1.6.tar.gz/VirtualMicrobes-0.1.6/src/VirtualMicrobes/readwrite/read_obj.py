from collections import OrderedDict
import re
import warnings

from VirtualMicrobes.event.Molecule import Molecule, MoleculeClass
from VirtualMicrobes.event.Reaction import Transport, ClassConvert, Convert
from VirtualMicrobes.my_tools.utility import OrderedSet
import VirtualMicrobes.my_tools.utility as util

'''

Reads plain text files to generate VirtualMicrobes.Cell objects or VirtualMicrobes.Environment objects.

The cell file is an accurate representation, containing everything to clone a VirtualMicrobes.Cell, and
can be used to start the simulation, or to do competition experiments.

The environment file contains not only the reaction universe, but also the influx rates, the grid size,
and the molecule properties.

(read-obj.py is the complementary part of write-obj)

'''

def parse_cell_stringrepr(filename):
    '''
    Takes cell-file (*.cell) as input, and makes a dictionary with all the features needed to make a VirtualMicrobe.Cell
    '''
    print "\n--------------------------------------------------------------------------------------"
    print "constructing cell from file ", filename
    print "--------------------------------------------------------------------------------------\n"

    cell_dict = {}  # Empty dict
    f = open(filename)
    lines = f.readlines()
    multilist = ['subs_ks', 'ligand_ks', 'ene_ks']
    floats = ['v_max', 'eff_bound', 'binding_coop', 'eff_apo', 'Prom_str',
              'ligand_coop', 'raw_death_rate', 'raw_production',
              'volume', 'raw_production_change_rate', 'pos_production',
              'toxicity_change_rate', 'toxicity', 'k_bind_op', 'version']  # These values are read as floats
    bools = ['wiped', 'divided', 'alive']
    ints = ['iterage']
    # simple_vals = ['membrane diffusion rates', 'degradation rates']
    f.close()

    def line_to_gene_dicts(line):
        gene_pat = re.compile(r'\[(.+)\],\[(.+)\]')
        m = gene_pat.match(line)
        gene_product, properties = m.group(1), m.group(2)
        return str_to_dict(gene_product), str_to_dict(properties)

    for line in lines:
        if line.startswith('#'):  # These lines are not parsed. Used for comments :)
            continue
        else:
            line = line.split('#')[0].strip()  # Remove inline comments
        if line.startswith('<'):
            section = ''.join(c for c in line if  c not in '<>\n')
            cell_dict[section] = {}
            continue
        if section == 'genes':
            genedict = {}
            gene_prod_dict, prop_dict = line_to_gene_dicts(line)

            for label, val in prop_dict.items():
                label = label.strip()
                if label in multilist:
                    subs_dict = str_to_dict(val.strip('{}'), item_split=' ',cast=float)
                    genedict[label] = subs_dict
                else:
                    genedict[label] = float(val) if label in floats else val

            if gene_prod_dict['concentration'] == 'nan':
                print 'found nan as gene conc, setting it to 0.0'
                genedict['concentration'] = 0.0
            else:
                genedict['concentration'] = float(gene_prod_dict['concentration'])
            genedict['reaction'] = gene_prod_dict['reaction']  # lastly, concentration and reaction from the geneproduct

            cell_dict[section][gene_prod_dict['id']] = genedict
        if section == 'genome':
            num, beads = line.split(':')
            beads = beads.strip()
            num = ''.join(c for c in num if  c not in 'abcdefghijklmnopqrstuvwxyz\n')
            cell_dict[section][num] = beads.split(' ')
        if section == 'cell_properties':
            list_properties = line.split(',')
            for prop in list_properties:
                label, value = prop.split('=')
                label, value = label.strip(), value.strip()
                if label in floats:
                    value = float(value)
                elif label in bools:
                    value = value == 'True'
                elif label in ints:
                    value = int(value)
                cell_dict[section][label] = value
        if section == 'molecule_concs':
            molname, conc = map(lambda s: s.strip(), line.split('='))
            cell_dict[section][molname] = float(conc)

    return cell_dict

def parse_environment_stringrepr(filename, verbose=True):
    '''
    Takes environment-file (*.env) as input, and makes a dictionary with all the features needed to generate
    a user-defined metabolic universe.
    '''
    print "\n--------------------------------------------------------------------------------------"
    print "constructing env from file ", filename
    print "--------------------------------------------------------------------------------------\n"
    composing_dict = {}  # Empty dict
    simple_vals = ['membrane diffusion rates', 'degradation rates']
    section = None
    mol_dict = OrderedDict()
    mol_class = None
    with open(filename) as f:
        while True:
            line = f.readline()
            if not line.strip():            # Ignore empty line
                break
            print line.strip()
            if line.startswith('#'):  # These lines are not parsed. Used for comments :)
                continue
            else:
                line = line.split('#')[0].strip()  # Remove inline comments
            if line.startswith('<'):
                section = line.strip('<>')
                if section in simple_vals + ['grid']:  # These values are simply dumped into dicts
                    composing_dict[section] = {}
                else:  # These more convoluted descriptions (e.g. molecules) are a list of lines, interpreted later
                    composing_dict[section] = list()
                continue

            if section in simple_vals:
                molname, val = line.split('=')
                composing_dict[section][molname] = val.strip()

            elif section == 'grid':  # List of influx dicts
                if line[0:3] == 'sub':
                    subrow, subcol = [subdiv.split('=')[1] for subdiv in line.strip().split(',')]
                    composing_dict[section]['subrows'] = int(subrow)
                    composing_dict[section]['subcols'] = int(subcol)
                    composing_dict[section]['subdicts'] = []
                elif line[0:3] == 'row':
                    row, col = [dim.split('=')[1] for dim in line.strip().split(',')]
                    composing_dict[section]['rows'] = int(row)
                    composing_dict[section]['cols'] = int(col)
                elif line[0:3] == 'col':
                    col, row = [dim.split('=')[1] for dim in line.strip().split(',')]
                    composing_dict[section]['rows'] = int(row)
                    composing_dict[section]['cols'] = int(col)
                else:
                    fluxdict = OrderedDict()
                    flux = line.split(':')[1]
                    flux = flux.split(',')
                    for mol in flux:
                        flux = mol.split('=')
                        fluxdict[flux[0]] = flux[1].strip()
                    composing_dict[section]['subdicts'].append(fluxdict)

            elif section == 'molecules':
                list_mol = line.strip('[]')
                obj_dict = dict()
                for k,v in (item.split("=") for item in list_mol.split(",")):
                    if k in ['is_energy', 'is_building_block']:
                        v = v == 'True'
                    elif k in ['energy_level', 'toxic_level']:
                        v = float(v)
                    obj_dict[k] = v
                if mol_class is None and not obj_dict.has_key('class'):
                    raise Exception('Expected a MoleculeClass line, but got\n{}'.format(line))
                elif obj_dict.has_key('class'): # this is a MoleculeClass line
                    mol_class = obj_dict['class']
                    del obj_dict['class']
                    obj_dict['name'] = mol_class
                    if not mol_dict.has_key(mol_class):
                        mol_dict[mol_class] = ( obj_dict, list() )
                    else:
                        raise Exception('Multiple definitions of MoleculeClass {}'.format(mol_class))
                else: # this is a Molecule line
                    mol_dict[mol_class][1].append(obj_dict)

            else:
                composing_dict[section].append(line.strip())
    composing_dict['molecules'] = mol_dict
    if verbose:
        print 'made composing dict'
    return composing_dict

def parse_molecules(f):
    '''
    Takes environment-file and returns temporary dict of molecules
    '''
    mol_dict = OrderedDict()
    mol_class = None
    while True:
        line = f.readline()
        if not line or line.startswith('<'):
            break
        list_mol = line.strip('[]')
        obj_dict = dict(item.split("=") for item in list_mol.split(","))
        if mol_class is None and not obj_dict.has_key('class'):
            raise Exception('Expected a MoleculeClass line, but got\n{}'.format(line))
        elif obj_dict.has_key('class'): # this is a MoleculeClass line
            mol_class = obj_dict['class']
            if not mol_dict.has_key(mol_class):
                mol_dict[mol_class] = ( obj_dict, list() )
            else:
                raise Exception('Multiple definitions of MoleculeClass {}'.format(mol_class))
        else: # this is a Molecule line
            mol_dict[mol_class][1].append(obj_dict)
    return mol_dict


def str_to_dict(s, item_split=',',cast=lambda x:x):
    '''
    Converts string of comma seperated properties to dict
    '''
    item_list = [ item.split(':',1) for item in s.split(item_split)]
    item_list = [ map(lambda s: s.strip(), tup ) for tup in item_list ]
    return dict([ (k, cast(v)) for k,v in item_list ] )


def init_mol_classes(env, mol_dict, reset=True):
    '''
    This function uses the molecule_dict (from parse_molecules) to set the molecules for VirtualMicrobes.Environment
    '''
    verbose = False
    if reset: env.internal_molecules = []
    if reset: env.influxed_mols = []
    if reset: env.influx_dict = OrderedDict()

    existing_mol_dict = {}
    for mol in env.internal_molecules:  # Smallmol look-up dict
        existing_mol_dict[mol.name] = mol

    env.params.nr_building_blocks = 0
    env.params.nr_cell_building_blocks = 0

    print '>> Initializing molecules'
    for classname, (class_dict, mol_dicts) in mol_dict.items():
        is_energy = class_dict.get('is_energy',False)
        mol_class = None
        if classname in [c.name for c in env.molecule_classes]:
            warnings.warn('Found existing MoleculeClass with same name: {}'.format(classname))
            warnings.warn('Ignoring differing configuration properties.')
            if not is_energy:
                mol_class = env.resource_classes[classname]
            else:
                mol_class = env.energy_classes[classname]
        else:
            if verbose:
                print 'adding molecule', mol_dict['name'], 'to class', classname
            mol_class = MoleculeClass(**class_dict)
            if is_energy:
                env.energy_classes[mol_class.name] = mol_class
            else:
                env.resource_classes[mol_class.name] = mol_class

        for mol_dict in mol_dicts:
            if mol_dict['name'] not in existing_mol_dict.keys():
                if verbose:
                    print mol_dict['name'] + ' is not in the env yet '
            else:
                warnings.warn('Not adding molecule with existing name {}'.format(mol_dict['name']))
                continue

            newmolecule = Molecule(environment=env,**mol_dict)
            mol_class.add_molecule(newmolecule)
            env.internal_molecules += [newmolecule]  # Adding the new mol_dict to the internal molecules list
            if newmolecule.is_building_block:
                env.params.nr_building_blocks += 1
                env.params.nr_cell_building_blocks += 1

def init_membrane_diffusion_dict(env, env_dict):
    '''
    Initialises membrane diffusion dict for VirtualMicrobes.Environment
    '''
    env.membrane_diffusion_dict = OrderedDict()
    verbose = False
    print '>> Initializing diff. dict'
    for mol in env.internal_molecules:
        try: diff = env_dict[mol.name]
        except KeyError: print '\033[93mDiffusion: Could not find a key for ' + mol.name + 'in your env-file\033[0m'
        if not diff >= 0.0:  # A check that the user inputs the right stuff
            raise ValueError('\033[93mDiffusion should be positive\033[0m')
        if verbose: print mol.name, 'is assigned a diffusion rate of', diff
        env.membrane_diffusion_dict[mol.paired] = float(diff)

def init_degradation_dict(env, env_dict):
    '''
    Initialises degradation dictionary for VirtualMicrobes.Environment
    '''
    env.degradation_dict = OrderedDict()
    verbose = False
    print '>> Initializing degr. dict'
    for mol in env.internal_molecules:
        try: degr = env_dict[mol.name]
        except KeyError: print '\033[93mDegradation: Could not find a key for ' + mol.name + 'in your env-file\033[0m'
        ### FIRST CHECK THE INPUT FOR SANITY ###
        if not degr >= 0.0:  # A check that the user inputs the right stuff
            raise ValueError('\033[93mDegredation should be positive\033[0m')
        ### ################################ ###
        if verbose: print mol.name, 'is assigned a degradation rate of', degr
        env.degradation_dict[mol.paired] = float(degr)

def read_grid_params(env,env_dict):
    '''
    Reads the grid parameters from env-dict to set VirtualMicrobes.Environment.Grid
    '''
    if env_dict['rows'] is not None:
        env.params.grid_rows = env_dict['rows']
        env.params.grid_cols = env_dict['cols']
    if env_dict['subrows'] is not None:
        env.params['grid_sub_div'] = util.GridSubDiv(row=env_dict['subrows'], col=env_dict['subcols'])


def parse_reaction(reaction):
    '''
    Parse the string representation of a reaction to VirtualMicrobes.Reaction (left-hand-side and right-hand-side tuple)
    '''
    LHS, RHS = reaction.split('->')
    to_terms = lambda h: map(lambda s: s.strip(), h.split('+'))
    LHS, RHS = to_terms(LHS), to_terms(RHS)

    stoi_re = re.compile(r'(\d*)(.+)')
    to_stoi_tups = lambda t: stoi_re.match(t)
    LHS = [ (int(m.group(1)), m.group(2).strip()) for m in map(to_stoi_tups, LHS) ]
    RHS = [ (int(m.group(1)), m.group(2).strip()) for m in map(to_stoi_tups, RHS) ]
    return LHS, RHS

def init_reactions(env, env_dict, reset=True):
    '''
    Initialises VirtualMicrobes.Event.Reaction as part of VirtualMicrobe.Environment from dictionary file from parse_environment_stringrepr
    '''
    verbose = False

    if reset: env.conversions = []
    if reset: env.transports = []

    env.init_diffusion()
    env.init_degradation()

    internal_mol_dict = {}
    existing_reactions = []
    for mol in env.internal_molecules:
        internal_mol_dict[mol.name] = mol

    for rea in env.conversions:
        existing_reactions.append(rea.short_repr())
    for tra in env.transports:
        existing_reactions.append(tra.short_repr())

    # print existing_reactions
    print '>> Initializing reaction universe'
    for reaction in env_dict['conversion reactions']:
        if reaction in existing_reactions:
            continue
        else:
            if verbose: print 'transcribing reaction ' + reaction
        LHS, RHS = parse_reaction(reaction)
        substrates = []
        products = []
        stoichiometry = []
        LHS_energy = 0
        RHS_energy = 0

        if LHS[0][1] not in internal_mol_dict:  # this is a Conversion
            for stoi, rclass in LHS:
                if rclass in env.energy_classes.keys():
                    LHS_energy += env.energy_classes[rclass].energy_level * stoi
                    substrates.append(env.energy_classes[rclass])
                else:
                    LHS_energy += env.resource_classes[rclass].energy_level * stoi
                    substrates.append(env.resource_classes[rclass])
                if verbose: print 'adding ' +rclass + ' to list of substrates for reaction'
                stoichiometry.append(stoi)
            for stoi, pclass in RHS:
                if pclass in env.energy_classes.keys():
                    RHS_energy += env.energy_classes[pclass].energy_level * stoi
                    products.append(env.energy_classes[pclass])
                else:
                    RHS_energy += env.resource_classes[pclass].energy_level * stoi
                    products.append(env.resource_classes[pclass])
                stoichiometry.append(stoi)
                if verbose: print 'adding ' + pclass + ' to list of products for reaction'
            if verbose: print 'stoi: ' + str(stoi) + '\n'
            if RHS_energy > LHS_energy:
                raise ValueError(str('\033[93m' + reaction + ' This reaction generates energy out of nothing. Change it.\033[0m'))
            conversion = Convert(substrates, products, stoichiometry)
            env.conversions.append(conversion)

        else:  # This is a ClassConversion
            if len(RHS) > 1:
                print RHS
                raise ValueError('Too many products for type conversion.')
            (sub_stoi, substrate) , (ene_stoi, energy) = LHS
            substrate = internal_mol_dict[substrate]
            LHS_energy += substrate.energy_level * sub_stoi
            energy = env.energy_classes[energy]
            LHS_energy += energy.energy_level * ene_stoi
            prod_stoi, mol = RHS[0]
            product = internal_mol_dict[mol]
            RHS_energy = product.energy_level * prod_stoi
            if RHS_energy > LHS_energy:
                raise ValueError(str('\033[93m' + reaction + ' This reaction generates energy out of nothing. Change it.\033[0m'))
            class_convert = ClassConvert(substrate, energy, product)
            if verbose:
                print 'created class conversion', class_convert
            env.conversions.append(class_convert)

    for reaction in env_dict['transport reactions']: # TODO: do checks on wellformedness of LHS and RHS
        if reaction in existing_reactions:
            continue
        else:
            if verbose: print 'transcribing reaction ' + reaction
        LHS, RHS = parse_reaction(reaction)
        cost, energy = LHS[0]
        sub_stoi, substrate = RHS[0]
        substrate = env.resource_classes[substrate]
        energy = env.energy_classes[energy]
        env.transports.append(Transport(substrate, energy, sub_stoi, cost))

    if verbose: print 'finalizing reactions'
    env.init_influx()
    env.init_mols_to_reactions()

def init_influx_dicts(env, flux_dicts, flux=1.0, verbose=True):
    '''
    Uses env-dict to set influx dictionary for VirtualMicrobes.Environment
    '''
    ### FIRST CHECK THE INPUT FOR SANITY ###
    rows, cols, subdicts = flux_dicts['subrows'], flux_dicts['subcols'], flux_dicts['subdicts']
    if not len(subdicts) == rows * cols:  # A check that the user inputs the right stuff
        raise AssertionError('Number of influx dicts is not equal to rows*cols, but should be')
    ### ################################ ###

    print '>> Initialising (sub)influx dicts\n'

    if verbose:
        print '[subenvs made with {} rows and {} cols]'.format(rows, cols)
    external_mol_dict = { mol.name:mol for mol in env.external_molecules}
    influxed_mols = OrderedSet()
    for flux_dict in subdicts:
        influxed_mols |= OrderedSet([ external_mol_dict[mol] for mol in flux_dict])
    env.influxed_mols = list(influxed_mols)
    env.init_global_influx_dict()
    env.subenvs = []
    env.subgrids = list(env.subgrids_gen(rows, cols))
    for i, flux_dict in enumerate(subdicts):
        influx_dict = OrderedDict()
        for mol, val in flux_dict.items():
            ### FIRST CHECK THE INPUT FOR SANITY ###
            try:
                mol = external_mol_dict[mol]
            except KeyError:
                raise TypeError(str('Could not match' + mol + 'to a molecule..'))
            try:
                val = float(val)
            except ValueError:
                if val == 'True':                           # get value from global influx dict
                    val = env.influx_dict[mol]
                    print '\n\n\n'
                elif val == 'False':
                    continue
                elif val == 'Global_highest':
                    val = pow(env.params.influx_range.base, env.params.influx_range.upper)
                elif val == 'Global_lowest':
                    val = pow(env.params.influx_range.base, env.params.influx_range.lower)
                else:
                    raise TypeError('Influx value is not a float or boolean string ... Something is wrong with your .env-file')
            ### ################################ ###

            if flux is None:
                flux = 1.0
            if verbose:
                print 'setting influx for', mol.name, 'to', val*flux, ' for subenv', i
            influx_dict[mol] = val*flux

        sub_env = util.SubEnv(sub_grid=env.subgrids[i], influx_dict=influx_dict)
        subrows, subcols = sub_env.sub_grid
        env.func_on_grid(lambda l: l.update_small_mol_influxes(sub_env.influx_dict), subrows, subcols)
        env.subenvs.append(sub_env)

    if verbose:
        print ' > subenvs made'
