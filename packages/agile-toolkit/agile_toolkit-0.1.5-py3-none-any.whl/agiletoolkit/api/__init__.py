import os
import logging
import configparser

import requests

from .repo import GitRepo
from .components import GithubException


LOGGER = logging.getLogger('github')


class GithubApi:

    def __init__(self, auth=None, http=None):
        self.http = requests.Session()
        try:
            self.auth = auth or get_auth()
        except GithubException as exc:
            LOGGER.warning(str(exc))
            self.auth = None

    @property
    def api_url(self):
        return 'https://api.github.com'

    @property
    def uploads_url(self):
        return 'https://uploads.github.com'

    def __repr__(self):
        return self.api_url
    __str__ = __repr__

    def repo(self, repo_path):
        return GitRepo(self, repo_path)


def get_auth():
    """Return a tuple for authenticating a user

    If not successful raise ``AgileError``.
    """
    auth = get_auth_from_env()
    if auth[0] and auth[1]:
        return auth

    home = os.path.expanduser("~")
    config = os.path.join(home, '.gitconfig')
    if not os.path.isfile(config):
        raise GithubException('No .gitconfig available')

    parser = configparser.ConfigParser()
    parser.read(config)
    if 'user' in parser:
        user = parser['user']
        if 'username' not in user:
            raise GithubException('Specify username in %s user '
                                  'section' % config)
        if 'token' not in user:
            raise GithubException('Specify token in %s user section'
                                  % config)
        return user['username'], user['token']
    else:
        raise GithubException('No user section in %s' % config)


def get_auth_from_env():
    return (
        os.environ.get('GITHUB_USERNAME', ''),
        os.environ.get('GITHUB_TOKEN', '')
    )
