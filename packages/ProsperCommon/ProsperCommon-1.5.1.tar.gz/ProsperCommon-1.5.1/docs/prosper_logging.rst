=============
ProsperLogger
=============

All `Prosper <https://github.com/EVEprosper>`_ scripts use a unified logger.  ``ProsperLogger`` is the easy way to build/extend any logger.  Death to ``print()`` long live ``logger``

ProsperLogger()
===============

Building a logger is easy.

.. code-block:: python

    import prosper.common.prosper_logging as p_loging

    LogBuilder = p_loging.ProsperLogger(
        'log_name',
        'desired/log/path',
        configuration_object,
        bool:debug_mode [optional]
    )
    LogBuilder.configure_discord_logger() # log ERROR/CRITICAL to Discord

    if DEBUG:
        LogBuilder.configure_debug_logger() # log debug messages to STDOUT

    logger = LogBuilder.get_logger()

the ``LogBuilder`` can be extended with some other handlers if required.  Also, defaults can be rerun if desired.

Built-In Handlers
=================

`configure_default_logger()`_
-----------------------------

.. code-block:: python
   :linenos:

    def configure_default_logger(
        log_freq:str,
        log_total:int,
        log_level:log_level_str,
        log_format:log_format_str,
        debug_mode:bool
    ):

* **log_freq**: `TimedRotatingFileHandler definition <https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler>`_
* **log_total**: how many log-periods to retain
* **log_level**: `Desired minimum log level <https://docs.python.org/3.5/library/logging.html#levels>`_
* **log_format**: `Python log formatter string <https://docs.python.org/3.5/library/logging.html#logrecord-attributes>`_
* **debug_mode**: unused at this time

This handler is loaded by default.  It can be reset by calling ``ProsperLogger().configure_default_logger(...)`` again.  **THIS SHOULD BE DONE AS EARLY AS POSSIBLE** can wipe out all other attached handlers.

`configure_debug_logger()`_
---------------------------

.. code-block:: python
   :linenos:

    def configure_debug_logger(
        log_level:log_level_str,
        log_format:log_format_str,
        debug_mode:bool
    ):

* **log_level**: default = 'DEBUG' (print everything)
* **log_format**: default = ``ReportingFormats.STDOUT``
* **debug_mode**: unused

For live debugging, report logging messages to standard out.  This can be attached by a `Plumbum.cli <http://plumbum.readthedocs.io/en/latest/cli.html>`_ for easy toggling between debug/production logging

`configure_discord_logger()`_
-----------------------------

.. code-block:: python
   :linenos:

    def configure_discord_logger(
        discord_webhook:url_str,
        discord_recipient:'<@int>'_discord_id_str,
        log_level:log_level_str,
        log_format:log_format_str,
        debug_mode:bool
    ):

* **discord_webhook**: `discord webhook url <https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks)>`_
* **discord_recipients**: ``<@int>`` for alerting `users <https://discordapp.com/developers/docs/resources/user#user-object>`_/groups (see app developer console)
* **log_level**: default 'ERROR'
* **log_format**: default ``ReportingFormats.PRETTY_PRINT``
* **debug_mode**: unused

Live alerting is a useful tool.  ProsperCommon is loaded with a REST handler for pushing logging alerts to `discord webhooks <https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks>`_.  Any alerts above a given level will be pushed out to a discord channel along the webhook pipeline

`configure_slack_logger()`_
---------------------------

.. code-block:: python
   :linenos:

    def configure_slack_logger(
        slack_webhook:url_str,
        log_level:log_level_str,
        log_format:log_format_str
        debug_mode:bool
    ):

* **slack_webhook**: `Slack webhook url <https://api.slack.com/apps>`_
* **log_level**: default 'ERROR'
* **log_format**: default ``ReportingFormats.PRETTY_PRINT``
* **debug_mode**: unused

Similar to the Discord handler, the Slack handler works very similarly.  Just get a `webhook for slack <https://api.slack.com/apps>`_ and assign the appropriate channel scope.  

**NOTE**: does not have alerting built in by default.  Best-practice for alerting humans may be to configure multiple slack_logger handles with direct message webhooks.

Logging Configuration
=====================

ProsperLogger is designed with the following priority order for finding configurations:

1. arguments in ``configure_handler`` calls
2. ``__init__`` called ``configuration_object`` loaded by the script that needs the logger
3. prosper.common/common_config.cfg as global defaults

## configuration_object

.. code-block:: none

    [LOGGING]
        log_level = INFO
        log_path = .
        log_freq = midnight
        log_total = 30
        discord_webhook = #SECRET
        discord_level = ERROR
        discord_alert_recipient = <@236681427817725954>
        slack_webhook = #SECRET

This section is valid in any loaded configuration object loaded by ``prosper.common.prosper_config.ProsperConfig()``.  Any commented/blank keys are loaded as ``None`` but should have error handling in place.

ReportingFormats
================

`Python Log Formats <https://docs.python.org/3.5/library/logging.html#logrecord-attributes>`_ are obnoxious to write, and leaving them in config-levels could lead to version upgrading issues later.

Instead we include some helpful baked-in formats for easy setup:

* ``ReportingFormats.DEFAULT`` (for file logging)

.. code-block:: none

    [2016-10-14 16:11:38,805;DEBUG;prosper_logging.py;<module>;185] my debug message

* ``ReportingFormats.PRETTY_PRINT`` (for Discord logging)

.. code-block:: none

    [DEBUG:prosper_logging.py--<module>:185]
    my debug message

* ``ReportingFormats.STDOUT`` (for STDOUT/console logging)

.. code-block:: none

    [DEBUG:prosper_logging.py--<module>:185] my debug message

.. _configure_default_logger(): source/common.html#common.prosper_logging.ProsperLogger.configure_default_logger
.. _configure_debug_logger(): source/common.html#common.prosper_logging.ProsperLogger.configure_debug_logger
.. _configure_discord_logger(): source/common.html#common.prosper_logging.ProsperLogger.configure_discord_logger
.. _configure_slack_logger(): common.html#common.prosper_logging.ProsperLogger.configure_slack_logger