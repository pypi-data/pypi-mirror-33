from mara_cli.cli import cli
import re

def test_without_argument(cli_runner):

    result = cli_runner.invoke(cli)
    assert result.exit_code == 0
    # here we get the name as 'cli' instead of 'mara'
    assert 'Usage: cli [OPTIONS] COMMAND [ARGS]' in result.output
    assert re.search(r'--debug\s+Show debug output',result.output) is not None
    assert re.search(r'print_config\s+Prints the current config', result.output) is not None

