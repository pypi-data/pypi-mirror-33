import os
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from .manager import Manager
from .api import GithubApi, GithubException
from .slack import SlackIntegration
from . import utils


@dataclass
class Branches:
    dev: str = 'master'
    stage: str = 'deploy'


class RepoManager(Manager):

    def init(self):
        self.info = utils.gitrepo(self.path)
        SlackIntegration.add(self)

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
