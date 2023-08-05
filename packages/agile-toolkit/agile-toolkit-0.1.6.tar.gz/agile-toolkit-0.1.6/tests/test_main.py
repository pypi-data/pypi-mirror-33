import yaml

from click.testing import CliRunner

from agiletoolkit import __version__
from agiletoolkit.commands import start
from agiletoolkit.repo import RepoManager
from agiletoolkit.test import gitrepo
from agiletoolkit.api import GithubException


def mocked(*a, **kw):
    print('mocked')


def test_main():
    runner = CliRunner()
    result = runner.invoke(start)
    assert result.exit_code == 0
    assert result.output.startswith('Usage:')
    #
    result = runner.invoke(start, ['--config', 'tests/cfg1.json'])
    assert result.exit_code == 0
    assert result.output.startswith('Usage:')


def test_version():
    runner = CliRunner()
    result = runner.invoke(start, ['--version'])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_repo(mocker):
    with gitrepo('deploy'):
        m = RepoManager()
        m.validate_version = mocker.Mock(return_value=True)
        assert m.can_release()

    with gitrepo('deploy'):
        m = RepoManager()
        m.validate_version = mocker.Mock(side_effect=GithubException('test'))
        assert m.can_release() is False


def test_docker_tag():
    with gitrepo('feature/ABC-123/bla-bla', head_id='1234567890'):
        m = RepoManager()
        assert m.version() == 'feature-abc-123-bla-bla-12345678'


def test_load_data(mocker):
    with gitrepo('deploy'):
        m = RepoManager(namespace='dev')
        with open('./deploy/values.yaml', 'w') as f:
            f.write(yaml.dump({
                'foo': '1',
                'bar': '2',
                'dev': {
                    'bar': '3',
                },
                'production': {
                    'bar': '4',
                },
            }))
        data = m.load_data('values.yaml')
        expected = {
            'foo': '1',
            'bar': '3',
            'namespace': 'dev',
        }
        assert data == expected
