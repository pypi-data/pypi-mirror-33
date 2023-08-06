=============================
pyparserchemicalformula
=============================

.. image:: https://img.shields.io/pypi/v/pyparserchemicalformula.svg
   :alt: Latest release on the Python Cheeseshop (PyPI)
   :target: https://pypi.python.org/pypi/pyparserchemicalformula

.. image:: https://travis-ci.org/hobbestigrou/pyparserchemicalformula.svg?branch=master
    :alt: Build status of perf on Travis CI
    :target: https://travis-ci.org/hobbestigrou/pyparserchemicalformula

A simple library to parse chemical string formula.

Documentation
-------------

The full documentation is at https://pyparserchemicalformula.readthedocs.io.

Quickstart
----------

Install pyparserchemicalformula::

    pip install pyparserchemicalformula

To run test::

    make test

That use tox to run test.

Usage example:

.. code-block:: python

    from pyparserchemicalformula.parser import parse_molecule

    parse_molecule('H2O')

Return a dict with the result of the formula.

Features
--------

* Parse a chemical formula string
