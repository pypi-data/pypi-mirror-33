.. ProsperCommon documentation master file, created by
   sphinx-quickstart on Thu Aug  3 18:26:52 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============
ProsperCommon
=============

|Build Status| |Coverage Status| |PyPI Badge| |Docs|


Common utilities for EVEProsper project. To reduce boilerplate across the shared projects in the `EVEProsper <http://www.eveprosper.com>`_ toolset

Quickstart
==========

Install ProsperCommon

    ``pip install ProsperCommon``

Features
========

* `prosper_logging`_: logging helpers/builders for Prosper projects
* `prosper_config`_: unified configparser to pick the right values and keep secrets off github
* `prosper_version`_: helpers to resolve correct package version 
* `prosper_cli`_: framework for creating CLI applications

Index
=====

.. toctree::
    :maxdepth: 2
    :caption: Contents:
 
    getting_started.rst
    prosper_logging.rst
    prosper_config.rst
    prosper_version.rst
    prosper_cli.rst

API Reference
=============

.. toctree::
    :maxdepth: 2
 
    source/common.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _prosper_logging: prosper_logging.html
.. _prosper_config: prosper_config.html
.. _prosper_version: prosper_version.html
.. _prosper_cli: prosper_cli.html

.. |Build Status| image:: https://travis-ci.org/EVEprosper/ProsperCommon.svg?branch=master
    :target: https://travis-ci.org/EVEprosper/ProsperCommon
.. |Coverage Status| image:: https://coveralls.io/repos/github/EVEprosper/ProsperCommon/badge.svg?branch=master
    :target: https://coveralls.io/github/EVEprosper/ProsperCommon?branch=master
.. |PyPI Badge| image:: https://badge.fury.io/py/ProsperCommon.svg
    :target: https://badge.fury.io/py/ProsperCommon
.. |Docs| image:: https://readthedocs.org/projects/prospercommon/badge/?version=latest
   :target: http://prospercommon.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status