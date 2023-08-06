from mara_cli.cli import cli, setup_commandline_commands
import re

import mara_config


def test_print_config(cli_runner):
    # needed to get the debug into the config ouput
    mara_config.register_functionality(mara_config)
    result = cli_runner.invoke(cli , ['print_config'])
    assert result.exit_code == 0
    assert 'Config:' in result.output
    assert re.search(r'debug.+-D-.+->.+False',result.output) is not None

def test_print_config_debug(cli_runner):
    mara_config.register_functionality(mara_config)
    # unfortunately, you cannot simply specify ['--debug', 'print_config'] because '--debug is handled outside of click
    mara_config.set_config('debug', function=lambda: True)
    result = cli_runner.invoke(cli , ['print_config'])
    assert result.exit_code == 0
    assert 'Config:' in result.output
    assert re.search(r'debug.+SD-.+->.+True',result.output) is not None
