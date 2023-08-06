***************
VirtualMicrobes
***************

VirtualMicrobes is a scientific Python package that can be used to do *in silico* evolutionary experiments with *Virtual Microbes*. 

Features
^^^^^^^^

* individual based, spatially extended model 
* explicit model of genome evolution
* gene regulatory network
* metabolic pathways
* cell growth and division
* variable, heterogeneous environment

Dependencies
^^^^^^^^^^^^

- `gsl <https://www.gnu.org/software/gsl/>`_
- `ete3 <http://etetoolkit.org/>`_ (tree drawing and phylogenetics)
- `cython <http://cython.org>`_
- `matplotlib <http://matplotlib.org>`_
- `networkx <http://networkx.github.io/>`_ (network analysis and drawing)
- others see requirements.txt


Quick Start
^^^^^^^^^^^

``pip install VirtualMicrobes``

``cd simulation_dir``

``virtualmicrobes.py evo --name MyFirstMicrobes``

|
Then direct ``firefox`` to file://.../simulation_dir/MyFirstMicrobes/00_webapplication.html
to observe the evolutionary trajectory of the population.

Custom initialization
^^^^^^^^^^^^^^^^^^^^^

``cd custom_sim``

``cp <INSTALL_LOCATION>/src/config_files/example_setup/* custom_sim``

``virtualmicrobes.py --env-from-file custom_sim/environment.env @custom_sim/general_options.cfg evo @custom_sim/evo_options.cfg --cells-from-files custom_sim/cell_1.cell custom_sim/cell_WGD.cell --name MyCustomMicrobes``

Again, observe the evolution of your microbes by directing ``firefox`` to file://.../custom_sim/MyCustomMicrobes/00_webapplication.html.


help
****

- ``virtualmicrobes.py --help``
- ``virtualmicrobes.py evo --help``

*************
Documentation
*************

A full description of the model is available here: https://bitbucket.org/thocu/virtualmicrobes/raw/develop/docs/virtual_microbes_methods.pdf

Further help with installing and documentation can be found on http://virtualmicrobes.readthedocs.io/en/latest/
