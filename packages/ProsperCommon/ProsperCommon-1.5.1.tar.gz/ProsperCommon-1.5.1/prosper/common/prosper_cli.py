"""Plumbum CLI wrapper for easier/common application writing"""
import logging
import os
import platform

from plumbum import cli

import prosper.common.prosper_logging as p_logging
import prosper.common.prosper_config as p_config


class ProsperApplication(cli.Application):
    """parent-wrapper for CLI applications"""

    debug = cli.Flag(
        ['d', '--debug'],
        help='DEBUG MODE: do not write to prod'
    )

    verbose = cli.Flag(
        ['v', '--verbose'],
        help='enable verbose messaging'
    )

    def __new__(cls, *args, **kwargs):
        """wrapper for ensuring expected variables"""
        if not hasattr(cls, 'config_path'):
            raise NotImplementedError(
                '`config_path` required path to default .cfg file'
            )
        return super(cli.Application, cls).__new__(cls)  # don't break cli.Application

    @cli.switch(
        ['--config'],
        str,
        help='Override default config')
    def override_config(self, config_path):  # pragma: no cover
        """override config object with local version"""
        self.config_path = config_path

    @cli.switch(
        ['--dump-config'],
        help='Dump default config to stdout')
    def dump_config(self):  # pragma: no cover
        """dumps configfile to stdout so users can edit/implement their own"""
        with open(self.config_path, 'r') as cfg_fh:
            base_config = cfg_fh.read()

        print(base_config)
        exit(2)

    @cli.switch(
        ['--secret-cfg'],
        cli.ExistingFile,
        help='Secrets .ini file for jinja2 template'
    )
    def load_secrets(self, secret_path):
        """render secrets into config object"""
        self._config = p_config.render_secrets(self.config_path, secret_path)

    _logger = None
    @property
    def logger(self):
        """uses "global logger" for logging"""
        if self._logger:
            return self._logger
        else:
            log_builder = p_logging.ProsperLogger(
                self.PROGNAME,
                self.config.get_option('LOGGING', 'log_path'),
                config_obj=self.config
            )

            if self.verbose:
                log_builder.configure_debug_logger()
            else:
                id_string = '({platform}--{version})'.format(
                    platform=platform.node(),
                    version=self.VERSION
                )
                if self.config.get_option('LOGGING', 'discord_webhook'):
                    log_builder.configure_discord_logger(
                        custom_args=id_string
                    )
                if self.config.get_option('LOGGING', 'slack_webhook'):
                    log_builder.configure_slack_logger(
                        custom_args=id_string
                    )
                if self.config.get_option('LOGGING', 'hipchat_webhook'):
                    log_builder.configure_hipchat_logger(
                        custom_args=id_string
                    )

            self._logger = log_builder.get_logger()
            return self._logger

    _config = None
    @property
    def config(self):
        """uses "global config" for cfg"""
        if self._config:
            return self._config
        else:
            self._config = p_config.ProsperConfig(self.config_path)
            return self._config


OPTION_ARGS = (
    'debug', 'port', 'threaded', 'workers'
)
class FlaskLauncher(ProsperApplication):
    """wrapper for launching (DEBUG) Flask apps"""

    port = cli.SwitchAttr(
        ['p', '--port'],
        int,
        help='port to launch Flask app on',
        default=int(os.environ.get('PROSPER_FLASK__port', 8000)),
    )
    threaded = cli.SwitchAttr(
        ['t', '--threaded'],
        bool,
        help='Launch Werkzeug in threaded mode',
        default=os.environ.get('PROSPER_FLASK__threadded', False),
    )
    workers = cli.SwitchAttr(
        ['w', '--workers'],
        int,
        help='Launch Werkzeug with multiple worker threads',
        default=int(os.environ.get('PROSPER_FLASK__workers', 1)),
    )


    def get_host(self):
        """returns appropriate host configuration

        Returns:
            str: host IP (127.0.0.1 or 0.0.0.0)

        """
        if self.debug:
            return '127.0.0.1'
        else:
            return '0.0.0.0'

    def notify_launch(self, log_level='ERROR'):
        """logs launcher message before startup

        Args:
            log_level (str): level to notify at

        """
        if not self.debug:
            self.logger.log(
                logging.getLevelName(log_level),
                'LAUNCHING %s -- %s', self.PROGNAME, platform.node()
            )
        flask_options = {
            key: getattr(self, key) for key in OPTION_ARGS
        }
        flask_options['host'] = self.get_host()

        self.logger.info('OPTIONS: %s', flask_options)


class ProsperTESTApplication(ProsperApplication):  # pragma: no cover
    """test wrapper for CLI tests"""
    PROGNAME = 'CLITEST'
    VERSION = '0.0.0'

    HERE = os.path.abspath(os.path.dirname(__file__))

    config_path = os.path.join(HERE, 'common_config.cfg')

    def main(self):
        """do stuff"""
        self.logger.info('HELLO WORLD')


if __name__ == '__main__':  # pragma: no cover
    ProsperTESTApplication.run()  # test hook
