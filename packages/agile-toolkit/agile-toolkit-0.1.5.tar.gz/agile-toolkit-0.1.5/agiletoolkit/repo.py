import os
import re
import asyncio
from typing import Dict
from dataclasses import dataclass
from urllib.parse import urlparse

import yaml

from jinja2 import Template

from .api import GithubApi, GithubException
from .slack import SlackIntegration
from . import utils


NAMESPACES = {'local', 'dev', 'stage', 'sandbox', 'production'}


@dataclass
class Branches:
    dev: str = 'master'
    stage: str = 'deploy'


class RepoManager:

    def __init__(self, config=None, path=None, yes=False, namespace=None):
        self.config = config or {}
        self.path = path or os.getcwd()
        self.deploy_path = os.path.join(self.path, 'deploy')
        self.yes = yes
        self.message_brokers = []
        self.namespace = namespace
        self.info = utils.gitrepo(self.path)
        SlackIntegration.add(self)
        self.init()

    def init(self):
        pass

    def software_version(self):
        """Software version

        Requires the Makefile entry

        version:
            ....
        """
        return utils.version()

    def version(self):
        """Software version of the current repository
        """
        branches = self.branches()
        if self.info['branch'] == branches.stage:
            try:
                return self.software_version()
            except Exception as exc:
                raise utils.CommandError(
                    'Could not obtain repo version, do you have a makefile '
                    'with version entry?\n%s' % exc
                )
        else:
            branch = self.info['branch'].lower()
            branch = re.sub('[^a-z0-9_-]+', '-', branch)
            return f"{branch}-{self.info['head']['id'][:8]}"

    def validate_version(self, prefix='v'):
        """Validate version by checking if it is a valid semantic version
        and its value is higher than latest github tag
        """
        version = self.software_version()
        repo = self.github_repo()
        repo.releases.validate_tag(version, prefix)
        return version

    def skip_build(self):
        """Check if build should be skipped
        """
        skip_msg = self.config.get('skip', '[ci skip]')
        return (
            os.environ.get('CODEBUILD_BUILD_SUCCEEDING') == '0' or
            self.info['current_tag'] or
            skip_msg in self.info['head']['message']
        )

    def can_release(self, target=None):
        if self.skip_build() or self.info["pr"]:
            return False

        branch = self.info['branch']
        branches = self.branches()

        if branch not in (branches.dev, branches.stage):
            return False

        if target and branch != getattr(branches, target):
            return False

        if not target:
            target = 'stage' if branch == branches.stage else 'dev'

        if target == 'stage':
            try:
                self.validate_version()
            except GithubException:
                return False

        return True

    def message(self, msg):
        """Send a message to third party applications
        """
        for broker in self.message_brokers:
            try:
                broker(msg)
            except Exception as exc:
                utils.error(exc)

    def github(self):
        return GithubApi()

    def branches(self):
        return self.get('branches', Branches)

    def target_from_branch(self):
        branches = self.branches()
        return 'dev' if self.info['branch'] == branches.dev else 'stage'

    def github_repo(self) -> str:
        url = self.info['remotes'][0]['url']
        if url.startswith('git@'):
            url = url.split(':')
            assert url[0] == 'git@github.com'
            path = url[1]
        else:
            path = urlparse(url).path[1:]
        bits = path.split('.')
        bits.pop()
        return self.github().repo('.'.join(bits))

    def get(self, name: str, DataClass: type) -> object:
        cfg = self.config.get(name) or {}
        return DataClass(**cfg)

    def load_data(self, *paths: str) -> Dict:
        filename = self.filename(*paths)
        if not os.path.isfile(filename):
            raise utils.CommandError('%s file missing' % filename)
        with open(filename, 'r') as fp:
            data = yaml.load(fp) or {}
        data_namespace = data.pop(self.namespace, None)
        for namespace in NAMESPACES:
            data.pop(namespace, None)
        if data_namespace:
            data.update(data_namespace)
        data['namespace'] = self.namespace
        return data

    def manifest(self, values, *paths, filename=None):
        """Load a manifest file and apply template values
        """
        filename = filename or self.filename(*paths)
        with open(filename, 'r') as fp:
            template = Template(fp.read())
        return yaml.load(template.render(values))

    def filename(self, *paths):
        if not os.path.isdir(self.deploy_path):
            raise utils.CommandError(
                "Path '%s' not available" % self.deploy_path
            )
        return os.path.join(self.deploy_path, *paths)

    def copy_env(self, *args, **kw):
        env = os.environ.copy()
        env.update(*args, **kw)
        return env

    def wait(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)
