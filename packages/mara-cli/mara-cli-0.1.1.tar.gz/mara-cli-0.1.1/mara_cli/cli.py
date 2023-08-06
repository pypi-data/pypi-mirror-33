"""Mara command line interface"""

import logging
import os
import sys

import click

log = logging.getLogger(__name__)


def _add_syslog_handler():
    """Adds a handler that the log produced by the CLI commands also go to syslog/systemd journal"""
    if os.name == 'posix':
        import logging.handlers
        # /dev/log is linux only (would need a different path on Mac, but these are dev machines...)
        handler = logging.handlers.SysLogHandler(address='/dev/log')
        # root logger to send every log message
        logging.root.addHandler(handler)


@click.group(help="""\
Runs contributed commandline commands

Contributed functionality (flask, downloader,...) is available as subcommands.

To run the webapp, use 'flask run'.

""")
@click.option('--debug', default=False, is_flag=True, help="Show debug output")
@click.option('--log-to-syslog', default=False, is_flag=True, help="Log to syslog")
def cli(debug: bool, log_to_syslog):
    # --debug is consumed by the setup_commandline_commands but it's here to let it show up in help
    # and not cause parse errors
    if log_to_syslog:
        # we want any log show up in the system log /systemd journal to see it there too...
        # Having it here menas we cannot log the startup to the syslog, but if something
        # goes wrong we anyway have to debug it manually
        _add_syslog_handler()


def setup_commandline_commands():
    """Needs to be run before click itself is run so the config which contributes click commands is available"""
    commandline_debug = '--debug' in sys.argv
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s, %(name)s: %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        # makefiles expect all log in stdout
                        stream=sys.stdout)

    if commandline_debug:
        logging.root.setLevel(logging.DEBUG)
        log.debug("Enabled debug output via commandline")

    # Initialize the config system
    from mara_config import init_mara_config_once
    init_mara_config_once()

    # The order basically means that the we only get information about the config system startup
    # when --debug is given on the commandline, but not when mara_config.config.debug() is configured
    # in the config system itself.
    # I think we can live with that...
    from mara_config.config import debug as configured_debug
    if configured_debug():
        logging.root.setLevel(logging.DEBUG)
        log.debug("Enabled debug output via config")

    # overwrite any config system with commandline debug switch
    if commandline_debug and not configured_debug():
        from mara_config.config_system import set_config
        set_config('debug', function=lambda: True)


    from mara_config import get_contributed_functionality
    for module, command in get_contributed_functionality('MARA_CLICK_COMMANDS'):
        if command and 'callback' in command.__dict__ and command.__dict__['callback']:
            package = command.__dict__['callback'].__module__.rpartition('.')[0]
            if package != 'flask':
                command.name = package + '.' + command.name
                cli.add_command(command)


def main():
    """'mara' console_scripts entry point"""
    setup_commandline_commands()
    args = sys.argv[1:]
    cli.main(args=args, prog_name='mara')


# This is here (instead of in mara-config) to have somethign to test the click functionality and
# to not add another import without setup requirements
@cli.command()
def print_config():
    """Prints the current config"""
    from mara_config.config_system.config_display import print_config
    print_config()


if __name__ == '__main__':
    main()
