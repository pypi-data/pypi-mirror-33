"""prosper_config.py

Unified config parsing and option picking against config objects

"""

from os import path, getenv
import configparser
from configparser import ExtendedInterpolation
import logging

import anyconfig
import anytemplate


def render_secrets(
        config_path,
        secret_path,
):
    """combine a jinja template with a secret .ini file

    Args:
        config_path (str): path to .cfg file with jinja templating
        secret_path (str): path to .ini-like secrets file

    Returns:
        ProsperConfig: rendered configuration object

    """
    with open(secret_path, 'r') as s_fh:
        secret_ini = anyconfig.load(s_fh, ac_parser='ini')

    with open(config_path, 'r') as c_fh:
        raw_cfg = c_fh.read()

    rendered_cfg = anytemplate.renders(raw_cfg, secret_ini, at_engine='jinja2')

    p_config = ProsperConfig(config_path)
    local_config = configparser.ConfigParser()
    local_config.optionxform = str
    local_config.read_string(rendered_cfg)

    p_config.local_config = local_config

    return p_config


class ProsperConfig(object):
    """configuration handler for all prosper projects

    Helps maintain global, local, and args values to pick according to priority

    1. args given at runtile
    2. <config_file>_local.cfg -- untracked config with #SECRETS
    3. <config_file>.cfg -- tracked 'master' config without #SECRETS
    4. environment varabile
    5. args_default -- function default w/o global config

    Args:
        config_filename (str): path to config file
        local_filepath_override (str): path modifier for private config file

    Attributes:
        global_config (:obj:`configparser.ConfigParser`)
        local_config (:obj:`configparser.ConfigParser`)
        config_filename (str): filename of global/tracked/default .cfg file
        local_config_filename (str): filename for local/custom .cfg file

    """
    logger = logging.getLogger('ProsperCommon')
    def __init__(
            self,
            config_filename,
            local_filepath_override='',
    ):
        """get the config filename for initializing data structures

        Args:
            config_filename (str): path to config
            local_filepath_override (str, optional): path to alternate private config file
            logger (:obj:`logging.Logger`, optional): capture messages to logger
            debug_mode (bool, optional): enable debug modes for config helper

        """
        self.config_filename = config_filename
        self.local_config_filename = get_local_config_filepath(config_filename)
        if local_filepath_override:
            self.local_config_filename = local_filepath_override
            #TODO: force filepaths to abspaths?
        self.global_config, self.local_config = get_configs(
            config_filename,
            self.local_config_filename,
        )

    def get(
            self,
            section_name,
            key_name,
    ):
        """Replicate configparser.get() functionality

        Args:
            section_name (str): section name in config
            key_name (str): key name in config.section_name

        Returns:
            (str): do not check defaults, only return local value

        """
        value = None
        try:
            value = self.local_config.get(section_name, key_name)
        except Exception as error_msg:
            self.logger.warning(
                '%s.%s not found in local config', section_name, key_name
            )
            try:
                value = self.global_config.get(section_name, key_name)
            except Exception as error_msg:
                self.logger.error(
                    '%s.%s not found in global config', section_name, key_name
                )
                raise KeyError('Could not find option in local/global config')

        return value

    def get_option(
            self,
            section_name,
            key_name,
            args_option=None,
            args_default=None,
    ):
        """evaluates the requested option and returns the correct value

        Notes:
            Priority order
            1. args given at runtile
            2. <config_file>_local.cfg -- untracked config with #SECRETS
            3. <config_file>.cfg -- tracked 'master' config without #SECRETS
            4. environment varabile
            5. args_default -- function default w/o global config

        Args:
            section_name (str): section level name in config
            key_name (str): key name for option in config
            args_option (any): arg option given by a function
            args_default (any): arg default given by a function

        Returns:
            (str) appropriate response as per priority order

        """
        if args_option != args_default and\
           args_option is not None:
            self.logger.debug('-- using function args')
            return args_option

        section_info = section_name + '.' + key_name

        option = None
        try:
            option = self.local_config[section_name][key_name]
            self.logger.debug('-- using local config')
            if option:
                return option
        except (KeyError, configparser.NoOptionError, configparser.NoSectionError):
            self.logger.debug('`%s` not found in local config', section_info)

        try:
            option = self.global_config[section_name][key_name]
            self.logger.debug('-- using global config')
            if option:
                return option
        except (KeyError, configparser.NoOptionError, configparser.NoSectionError):
            self.logger.warning('`%s` not found in global config', section_info)

        env_option = get_value_from_environment(section_name, key_name, logger=self.logger)
        if env_option:
            self.logger.debug('-- using environment value')
            return env_option

        self.logger.debug('-- using default argument')
        return args_default #If all esle fails return the given default

    def attach_logger(self, logger):
        """because load orders might be weird, add logger later"""
        self.logger = logger

ENVNAME_PAD = 'PROSPER'
def get_value_from_environment(
        section_name,
        key_name,
        envname_pad=ENVNAME_PAD,
        logger=logging.getLogger('ProsperCommon'),
):
    """check environment for key/value pair

    Args:
        section_name (str): section name
        key_name (str): key to look up
        envname_pad (str): namespace padding
        logger (:obj:`logging.logger`): logging handle

    Returns:
        str: value in environment

    """
    var_name = '{pad}_{section}__{key}'.format(
        pad=envname_pad,
        section=section_name,
        key=key_name
    )

    logger.debug('var_name=%s', var_name)
    value = getenv(var_name)
    logger.debug('env value=%s', value)

    return value

def get_configs(
        config_filepath,
        local_filepath_override='',
):
    """go and fetch the global/local configs from file and load them with configparser

    Args:
        config_filepath (str): path to config
        local_filepath_override (str): secondary place to locate config file

    Returns:
        ConfigParser: global_config
        ConfigParser: local_config

    """
    global_config = read_config(config_filepath)

    local_filepath = get_local_config_filepath(config_filepath, True)
    if local_filepath_override:
        local_filepath = local_filepath_override
    local_config = read_config(local_filepath)

    return global_config, local_config

def read_config(
        config_filepath,
        logger=logging.getLogger('ProsperCommon'),
):
    """fetch and parse config file

    Args:
        config_filepath (str): path to config file.  abspath > relpath
        logger (:obj:`logging.Logger`): logger to catch error msgs

    Raises:
        FileNotFound: file access issues

    """
    config_parser = configparser.ConfigParser(
        interpolation=ExtendedInterpolation(),
        allow_no_value=True,
        delimiters=('='),
        inline_comment_prefixes=('#')
    )
    logger.debug('config_filepath=%s', config_filepath)
    try:
        with open(config_filepath, 'r') as filehandle:
            config_parser.read_file(filehandle)
    except Exception as error_msg:
        logger.error(
            'Unable to parse config file: %s', config_filepath, exc_info=True
        )
        raise error_msg

    return config_parser

def get_local_config_filepath(
        config_filepath,
        force_local=False,
):
    """helper for finding local filepath for config

    Args:
        config_filepath (str): path to local config abspath > relpath
        force_local (bool): force return of _local.cfg version

    Returns:
        str: Path to local config, or global if path DNE

    """
    local_config_name = path.basename(config_filepath).split('.')[0] + '_local.cfg'
    local_config_filepath = path.join(path.split(config_filepath)[0], local_config_name)

    real_config_filepath = ''
    if path.isfile(local_config_filepath) or force_local:
        #if _local.cfg version exists, use it instead
        real_config_filepath = local_config_filepath
    else:
        #else use tracked default
        real_config_filepath = config_filepath

    return real_config_filepath
