========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - build
      - | |travis| |requires| |codecov|
    * - package
      - | |wheel| |supported_versions|

.. |docs| image:: https://readthedocs.org/projects/dl-with-numpy/badge/?version=latest
    :target: https://dl-with-numpy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/jonathan-smith-1/dl_with_numpy.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/jonathan-smith-1/dl_with_numpy

.. |requires| image:: https://requires.io/github/jonathan-smith-1/dl_with_numpy/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/jonathan-smith-1/dl_with_numpy/requirements/?branch=master

.. |codecov| image:: https://codecov.io/gh/jonathan-smith-1/dl_with_numpy/branch/master/graph/badge.svg
    :alt: Coverage Status
    :target: https://codecov.io/gh/jonathan-smith-1/dl_with_numpy

.. |wheel| image:: https://img.shields.io/pypi/wheel/dl_with_numpy.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/dl_with_numpy

.. |supported_versions| image:: https://img.shields.io/pypi/pyversions/dl_with_numpy.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/dl_with_numpy

.. end-badges

A very simple deep learning library implemented in Numpy.


Installation
============

::

    pip install dl_with_numpy

Documentation
=============

https://dl-with-numpy.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Acknowledgements
================

Many thanks to Ionel Cristian Mărieș for

- His excellent `blog post <https://blog.ionelmc.ro/2014/05/25/python-packaging/>`_
  on packaging a python library.

- His `cookiecutter-pylibrary <https://github.com/ionelmc/cookiecutter-pylibrary>`_
  project on Github.  For this project I wanted to make my own mistakes but
  next time I would just fork his project and go from there.
