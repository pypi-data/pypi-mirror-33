==============
ProsperVersion
==============

Getting version information reliably vs `GitHub`_, `PyPI`_, `Travis-CI`_, and `source`_ is difficult.  Taking a page out of `ccpgames/setuphelpers`_ to standardize work.

Using prosper_version
=====================

.. code-block:: python
    
    _version.py 
    """_version.py: a place to report package version info"""
    from os import path
    import warnings

    INSTALLED = True
    try:
        import prosper.common.prosper_version as p_version
        #requires helper, but setup.py install can't reference itself on first pass
    except ImportError:
        INSTALLED = False

    HERE = path.abspath(path.dirname(__file__))

    def get_version():
        """find current version

        Returns:
            (str): current version

        """
        if not INSTALLED:
            warnings.warn('Unable to resolve package version until installed', UserWarning)
            return '0.0.0'

        return p_version.get_version(HERE)

    __version__ = get_version() #required for setup.py to find via `importlib`

This code helps both users of Prosper projects and devs get the version information reliably, without worrying about all the background confilcts.

Version Priorities
==================

Below is the rank/order prosper_version will try to resolve version information

1. ``TRAVIS_TAG``: if test is running on `Travis-CI`_, default to its version (release)
2. ``git tag``: Look for latest version in git (dev)
3. ``version.txt``: Look for latest version in ``version.txt`` file.  (PyPI released)
4. ``default_version``: If all else fails, default to 0.0.0


.. _GitHub: https://github.com/EVEprosper/ProsperCommon
.. _PyPI: https://pypi.python.org/pypi/ProsperCommon
.. _Travis-CI: https://travis-ci.org/EVEprosper/ProsperCommon
.. _source: https://github.com/EVEprosper/ProsperCommon
.. _ccpgames/setuphelpers: https://github.com/ccpgames/setuphelpers