import copy
import os
import tempfile
from unittest import mock
from contextlib import contextmanager

from .api import GithubException

GIT_OUTPUT = {
    'branch': 'add_namespace',
    'current_tag': '',
    'head': {
        'author_email': 'konrad@example.com',
        'author_name': 'Konrad Rotkiewicz',
        'committer_email': 'konrad@example.com',
        'committer_name': 'Konrad Rotkiewicz',
        'id': '22f17e5c69dcda3b6695ac07b9f32e3c4964848a',
        'message': 'add namespace when loading data',
    },
    'pr': False,
    'remotes': [
        {
            'name': 'origin',
            'url': 'git@github.com:lendingblock/agile-toolkit.git',
        },
    ],
    'tag': 'v0.1.3'
}


MAKEFILE = """\
version:
<tab>@echo "1.2.3"
"""


CODEBUILD = """\
name: test
description: test
source:
  location: https://github.com/example/example.git
"""


@contextmanager
def gitrepo(branch, pr=False, tag=None, head_id=None):
    """
    prepare artifical git repo
    1. create temp dir
    2. add basic project structure
    3. cd to that dir
    4. mock utils.gtirepo
    5. cd back and removes the dir
    """

    def mocker(root=None):
        data = copy.deepcopy(GIT_OUTPUT)
        data['branch'] = branch
        data['pr'] = pr
        data['tag'] = tag
        if head_id:
            data['head']['id'] = head_id
        return data

    with tempfile.TemporaryDirectory() as temp_dir:
        curr_dir = os.getcwd()
        os.chdir(temp_dir)
        os.makedirs('deploy')
        with open('Makefile', 'w') as f:
            f.write(MAKEFILE.replace('<tab>', '\t'))
        with open('deploy/codebuild.yaml', 'w') as f:
            f.write(CODEBUILD)
        with mock.patch('agiletoolkit.utils.gitrepo', side_effect=mocker) as m:
            try:
                yield m
            finally:
                os.chdir(curr_dir)


def github_error(*args, **kwargs):
    raise GithubException
