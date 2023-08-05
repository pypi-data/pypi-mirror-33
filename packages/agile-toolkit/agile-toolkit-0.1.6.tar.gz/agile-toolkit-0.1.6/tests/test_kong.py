from click.testing import CliRunner

from agiletoolkit.commands import start


def test_git():
    runner = CliRunner()
    result = runner.invoke(start, ['kong', '--help'])
    assert result.exit_code == 0
    assert result.output.startswith('Usage:')
