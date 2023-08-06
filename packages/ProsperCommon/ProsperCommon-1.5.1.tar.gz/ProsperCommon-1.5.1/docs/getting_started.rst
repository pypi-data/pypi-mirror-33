===============
Getting Started
===============

ProsperCommon is a group of utilities we expect nearly every `Prosper`_ project to use.  These libraries are designed to be easy and uniform.

Using ProsperCommon
===================

    ``pip install ProsperCommon``

It's worth noting that nearly every `Prosper`_ project requires a ``app_config.cfg`` file.  Some libraries will expect certain namespaces be reserved.

EX: ``prosper.common.prosper_logging.ProsperLogger()`` expects to use ``[LOGGING]`` section for config keeping

Please review documentation carefully to avoid namespace collisions

Updating ProsperCommon
======================

If working from dev/GitHub:

    ``pip install -e .``

Testing
-------

    ``python setup.py test``

Since common is so important to `Prosper`_ projects, testing and coverage are extremely important.  Please know PR's will require the following

- >90% coverage
- PEP8 compliance
- `Napoleon style`_ docstrings for all functions and classes
- Docs coverage for any new functionality

Docs
----

    ``pip install .[dev]``

    ``sphinx-apidoc -f -o docs/source prosper/common/`` Update autodocs
    
    ``sphinx-build -b html docs/ webpage/`` build docs

Documentation is important.  Please make sure to update docs before release

Release
-------

Release is handled by tagging + `Travis-CI`_.  Tagged versions are automatically pushed to `PyPI`_.  

Release message should include useful update notes, and versions should follow `Semantic Versioning`_ standard.

.. _Prosper: http://www.eveprosper.com
.. _Napoleon style: http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
.. _Travis-CI: https://travis-ci.org/EVEprosper/ProsperCommon
.. _PyPI: https://pypi.python.org/pypi/ProsperCommon
.. _Semantic Versioning: http://semver.org/