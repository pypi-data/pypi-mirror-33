pisnrs
============

pisnrs is a Python module for NR inhibitors prediction built on top of
RDKit, scikit-learn and distributed under the MIT license.


Installation
------------

Dependencies
~~~~~~~~~~~~

pisnrs requires:

- Python (>= 2.6)
- rdkit (>= 2018.03.2.0)
- scikit-learn (>= 0.19.1)
- pandas (>= 0.23.1)


User installation
~~~~~~~~~~~~~~~~~

You can install pisnrs using anaconda.

### Introduction to anaconda

Conda is an open-source, cross-platform, software package manager. It supports the packaging and distribution of software components, and manages their installation inside isolated execution environments. It has several analogies with pip and virtualenv, but it is designed to be more "python-agnostic" and more suitable for the distribution of binary packages and their dependencies.

### How to get conda

The easiest way to get Conda is having it installed as part of the [Anaconda Python distribution](https://conda.io/docs/user-guide/install/index.html). A possible (but a bit more complex to use) alternative is provided with the smaller and more self-contained [Miniconda](https://conda.io/miniconda.html). The conda source code repository is available on [github](https://github.com/conda) and additional documentation is provided by the project [website](https://conda.io/docs/).

### How to install RDKit with Conda

Creating a new conda environment with the RDKit installed requires one single command similar to the following::

  $ conda create -c rdkit rdkit

### Install scikit-learn

Install scikit-learn using pip::
    pip install -U scikit-learn

or ``conda`` ::
    conda install scikit-learn

### Install pisnrs

If you already have a working installation of rdkit and scikit-learn, the easiest way to install pisnrs is using ``pip`` ::

    pip install pisnrs

Important links
~~~~~~~~~~~~~~~

- Official source code repo: https://github.com/pisnrs/pisnrs
- Download releases: https://pypi.python.org/pypi/pisnrs

Source code
~~~~~~~~~~~

You can check the latest sources with the command::

    git clone https://github.com/pisnrs/pisnrs.git
