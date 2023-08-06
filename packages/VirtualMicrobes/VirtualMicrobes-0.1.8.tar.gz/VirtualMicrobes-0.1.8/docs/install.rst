**********
Installing
**********

Before installing VirtualMicrobes, you need to have
`setuptools <https://pypi.python.org/pypi/setuptools>`_ installed.

Quick install
=============

Get VirtualMicrobes from the Python Package Index at
http://pypi.python.org/pypi/VirtualMicrobes

or install it with

::

   pip install VirtualMicrobes

and an attempt will be made to find and install an appropriate version
that matches your operating system and Python version.

The project can be cloned from bitbucket with:

::

  git clone https://thocu@bitbucket.org/thocu/virtualmicrobes.git


Requirements
============

Installing the project via ``pip``, the required packages will be checked 
against your installation and installed if necessary. 

Python
------

To use VirtualMicrobes you need Python 2.7

ete3
----------

This is a package for drawing and manipulating phylogenetic trees. It is used to 
keep track of phylogenetic relationships between ``Virtual Microbes``.

- Download: http://etetoolkit.org/download/

ete3 has its own dependency on pyqt. 

Matplotlib
----------
Used for generating various plots during the simulation.

  - Download: http://matplotlib.sourceforge.net/

Gnu Scientific Library
----------------------

  
Other
-----

* networkx
* attrdict
* blessings
* networkx
* pandas
* psutil
* errand_boy
* orderedset
* pyparsing
* setproctitle
* sortedcontainers
* mpl

Optional packages
=================

Cython and CythonGSL
--------------------

The package includes a few C Extension modules, originally written in the 
`Cython <http://cython.org/>`_ language. If during the install both Cython 
and the CythonGSL package
are detected, the extensions will be build from the original ``.pyx`` sources. 
Otherwise, the included pre-generated ``.c`` files will be used to build the 
extension.

  - Download: http://http://cython.org/#download
  
  - Download: https://github.com/twiecki/CythonGSL (follow the ``build`` and ``install`` instructions in the README) 
