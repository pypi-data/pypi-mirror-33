================
WORK IN PROGRESS
================

Author's notice
===============

** THIS REPOSITORY IS BEING CREATED IN MY SPARE TIME. I WILL REMOVE THIS NOTICE WHEN FULLY FUNCTIONAL. **

This is also my first true Python package, so I am still learning how to do it *The Right Way (TM)*.

I am figuring out how to configure all the stuff the mighty `cookiecutter-pylibrary <https://github.com/ionelmc/cookiecutter-pylibrary>`_ created for me.

TODO
====

Stuff to do to have a working repository:

#.  Write some tests for `pytest`.
#.  Configure and verify `tox`.
#.  Write the documentation for `sphinx`.
#.  Drop any current CLI (based on `argparse` and very rough) and add a CLI with `click`.
#.  Configure and verify `travis` and stuff
#.  Configure and verify `ReadTheDocs` and stuff
#.  Remove this stuff from the readme.
#.  Integrate with `PyPI`


========
Overview
========



Library to handle hexadecimal record files

* Free software: BSD 2-Clause License

Installation
============

::

    pip install hexrec

Documentation
=============

https://hexrec.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox


Changelog
=========

0.0.1 (2018-06-27)
------------------

* First release on PyPI.


