==========
ProsperCLI
==========

Help create uniform templates and reduce boilerplate, PropsperCLI gives a common jumping off point for any scraper/utility.  Based off `Plumbum`_ framework.

Using prosper_cli
=================

**Generic CLI**

.. code-block:: python

    """my_app.py"""
    from os import path
    import prosper.common.prosper_cli as p_cli
    from _version import __version__

    class MyApplication(p_cli.ProsperApplication):
        PROGNAME = 'my_app_name'  # REQUIRED
        VERSION = __version__

        config_path = path.join(
            path.abspath(path.dirname(__file__)),
            'my_config_file.cfg'
        )

        def main(self):
            """actual logic goes here"""
            self.logger.info('Hello world!')
            ...

    if __name__ == '__main__':
        MyApplication.run()

-----

**Flask Launcher**

.. code-block:: python

    """my_app.py"""
    from os import path
    import prosper.common.prosper_cli as p_cli
    from _version import __version__
    from endpoints import APP

    class MyFlaskApplication(p_cli.FlaskLauncher):
        PROGNAME = 'my_app_name'  # REQUIRED
        VERSION = __version__

        config_path = path.join(
            path.abspath(path.dirname(__file__)),
            'my_config_file.cfg'
        )

        def main(self):
            """actual logic goes here"""
            self.notify_launch()
            
            APP.run(
                host=self.get_host(),
                port=self.port,
                debug=self.debug,
                threaded=self.threaded,
                process=self.workers,
            )

    if __name__ == '__main__':
        MyFlaskApplication.run()
     
Meant to be used with `ProsperCookiecutters`_ for debug launching Flask apps.  

CLI Features
------------

By using the Prosper framework, the following is handled automatically:

- Help/version info handled by `Plumbum`_
- ``-d``/``--debug`` bool for avoiding production mode
- ``-v``/``--verbose`` bool for enabling STDOUT logging
- ``--config`` for loading a custom config file
- ``--dump-config`` for dumping default config to STDOUT
- ``--secret-cfg`` for using a jinja2 template secret-keeping style
- ``self.logger`` and ``self.config`` loaded automagically
- Full ``ProsperLogging`` support
    - Slack and Discord support if webhooks are provided by config
    - Standardized log formatting
    - Platform and version information for webhook loggers

Secret Config
~~~~~~~~~~~~~

Sometimes having a secrets file is preferrable to using environment variables.  This allows secrets to be more easily passed as keys.

.. code-block:: cfg

# credentials.ini
[key]
    value_1 = secret
    value_2 = secret


.. _Plumbum: http://plumbum.readthedocs.io/en/latest/cli.html
.. _ProsperCookiecutters: https://github.com/EVEprosper/ProsperCookiecutters
