=============
ProsperConfig
=============
Parsing global/local configs can be obnoxious.  We provide a way to use/override configs.  Especially for libraries, a way to control globals or override them.

All `Prosper <https://github.com/EVEprosper>`_ use the ``ProsperConfig`` parser.  Powered by py3's ``configparser``.

ProsperConfig()
===============

.. code-block:: python

    import prosper.common.prosper_config as p_config

    ConfigObj = ProsperConfig(
        'path/to/config.cfg'
        local_filepath_override='path/to/custom_config.cfg' #optional
    )

    option_value = ConfigObj.get_option('SECTION_NAME', 'KEY_NAME', override_value, default_value)

This should give the following priority for ``option_value``

1. ``if override_value != default_value: override value``: A value given at arg time
2. ``local_config['SECTION_NAME']['KEY_NAME']``: Untracked local config file (secrets safe)
3. ``global_config['SECTION_NAME']['KEY_NAME']``: Git tracked config file
4. ``os.environ.get('PROSPER_{SECTION_NAME}__{KEY_NAME}')``: Check the environment for values (secrets safe-ish)
5. ``default_value`` as a final result to avoid returning ``None`` where it wouldn't be supported
