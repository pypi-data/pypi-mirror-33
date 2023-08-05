from unittest import mock
from contextlib import contextmanager

from . import utils
from .api import GithubException


@contextmanager
def gitrepo(branch, pr=False, tag=None, head_id=None):

    original_gitrepo = utils.gitrepo

    def mocker(root=None):
        data = original_gitrepo(root)
        data['branch'] = branch
        data['pr'] = pr
        data['tag'] = tag
        if head_id:
            data['head']['id'] = head_id
        return data

    with mock.patch('agiletoolkit.utils.gitrepo', side_effect=mocker) as m:
        yield m


def github_error(*args, **kwargs):
    raise GithubException
