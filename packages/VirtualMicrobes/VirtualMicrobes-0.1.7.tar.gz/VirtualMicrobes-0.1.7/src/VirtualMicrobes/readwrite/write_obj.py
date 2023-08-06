
'''
Writes plain text files that can be used to generate VirtualMicrobes.Cell objects or VirtualMicrobes.Environment objects.

The cell file is an accurate representation, containing everything to clone a VirtualMicrobes.Cell, and
can be used to start the simulation, or to do competition experiments.

The environment file contains not only the reaction universe, but also the influx rates, the grid size,
and the molecule properties.

(write_obj.py is complementary to read_obj.py)
'''

def string_to_file(string, filename):
    '''
    Writes stringrepresentation of object to a file
    '''
    f = open(filename, 'w')
    f.write(string)
    f.close()

def write_env(environment, filename = None):
    '''
    Makes string representation of a environment object.

    If no filename is given, it just returns the string.
    Otherwise, the file is written to <save_dir>/<filename>
    (default = <save_dir>/environment.env)
    '''
    out=""
    out+= '<molecules>\n'

    for rclass in environment.resource_classes.values():
        out+= rclass.short_repr() + '\n'
        for mol in rclass.molecules.values():
            out+= mol.short_repr() + '\n'
    for eclass in environment.energy_classes.values():
        out+= eclass.short_repr() + '\n'
        for mol in eclass.molecules.values():
            out+= mol.short_repr()+'\n'
    out+='<conversion reactions>\n'
    for c in environment.conversions:
        out+= c.short_repr()+'\n'
    out+=  '<transport reactions>\n'
    for t in environment.transports:
        out+=  t.short_repr()  +'\n'
    out+= '<degradation rates>\n'
    for mol_ext in environment.external_molecules:
        out+= mol_ext.name +'='+str(environment.degradation_dict[mol_ext])+'\n'
    out+= '<membrane diffusion rates>\n'
    for mol_ext in environment.external_molecules:
        out+= mol_ext.name +'='+str(environment.membrane_diffusion_dict[mol_ext])+'\n'
    out+= '<grid>\n'
    rows = environment.params.grid_rows
    cols = environment.params.grid_cols
    subrows = environment.params.grid_sub_div.row
    subcols = environment.params.grid_sub_div.col
    out+= 'rows='+str(rows)
    out+= ',cols='+str(cols)
    out+='\n'
    out+= 'subrows='+str(subrows)
    out+= ',subcols='+str(subcols)
    out+='\n'
    num = 0
    for sub in environment.subenvs:
        if num+1 > rows*cols: break
        out+='influx'+str(num)+':'
        num+=1
        influxlist = []
        for mol_ext, influx in sub.influx_dict.items():
            influxlist+=[mol_ext.name+'='+str(influx)]
        out+=','.join(influxlist)
        out+='\n'

    if filename is not None:
        print "saving stringrepresentation of env in", filename
        string_to_file(out,filename)
    else:
        print "\n\n\n\n\n\n\n NOT saving stringrepresentation of env in\n\n\n\n\n\n", filename
        return out

def write_cell(cell, filename = None, alive = False):
    '''
    Makes string representation of a cell object.
    The cell's properties are taken as they were at birth.

    If no filename is given, it just returns the string.
    Otherwise, the file is written to <save_dir>/<filename>
    (default = <save_dir>/data/best_dat/generation_bests<time>.cell)

    '''
    out=""
    unique_gene_id = 0
    unique_ids = dict()
    metabolic_genes = ['enz','pump']
    out+= '# This is a cell representation. Be careful to retain the structure in terms of brackets/spaces etc, as not every fallback is accounted for by mediocre programming\n'
    out+= '<genes>\n'
    for gene in cell.molecules["gene_products"]:
        unique_gene_id += 1
        reaction = ''
        if gene["type"] in metabolic_genes:
            reaction = ',reaction:' + gene.reaction.short_repr()
        else:
            reaction = ',reaction:None'

        out+= ('[id:'+str(unique_gene_id) + ','
                + 'concentration:' + str(cell.molecules['gene_products'][gene].concentration)
                + reaction+'],' + str(gene) + '\n'
                )
        unique_ids[gene] = unique_gene_id

    out+= '<genome>\n'
    for i, chrom in enumerate(cell.genome.chromosomes):
        out+= 'chrom'+str(i)+':'
        for gene in chrom:
            out+= ' ' + str(unique_ids[gene])
        out += '\n'

    out+= '<molecule_concs>\n'
    mollist = []
    for mol,mol_str in cell.molecules["small_molecules"].items():
        mollist+= [mol.name+'='+str(mol_str.concentration)]
    out+='\n'.join(mollist)

    out+= '\n<cell_properties>\n'
    out += 'volume='+str(cell.volume)+'\n'
    out += 'raw_production='+str(cell.raw_production)+'\n'
    out += 'pos_production='+str(cell.pos_production)+'\n'
    out += 'raw_production_change_rate='+str(cell.raw_production_change_rate)+'\n'
    out += 'toxicity='+str(cell.toxicity)+'\n'
    out += 'toxicity_change_rate='+str(cell.toxicity_change_rate)+'\n'
    out += 'raw_death_rate='+str(cell.raw_death_rate)+'\n'
    out += 'alive='+str(alive)+'\n'
    out += 'divided='+str(cell.divided)+'\n'
    out += 'wiped='+str(cell.wiped)+'\n'
    out += 'iterage='+str(cell.iterage)+'\n'
    out += 'lineage='+str(cell.marker_dict['lineage'])+'\n'
    out += 'version='+str(cell.version)

    if filename is not None:
        #print "saving stringrepresentation of cell in", filename
        string_to_file(out,filename)
    else:
        print "\n\n\n\n\n\n\n NOT saving stringrepresentation of cell in\n\n\n\n\n\n", filename
        return out
