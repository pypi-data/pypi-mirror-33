from .components import Commits, Pulls, Issues, Component, Milestones, Hooks
from .releases import Releases


class GitRepo(Component):
    """Github repository endpoints
    """
    def __init__(self, client, repo_path):
        super().__init__(client)
        self.repo_path = repo_path
        self.releases = Releases(self)
        self.commits = Commits(self)
        self.issues = Issues(self)
        self.pulls = Pulls(self)
        self.milestones = Milestones(self)
        self.hooks = Hooks(self)
        self.headers = dict(
            accept='application/vnd.github.symmetra-preview+json'
        )

    @property
    def api_url(self):
        return '%s/repos/%s' % (self.client, self.repo_path)

    def label(self, name, color, update=True):
        """Create or update a label
        """
        url = '%s/labels' % self
        data = dict(name=name, color=color)
        response = self.http.post(
            url, json=data, auth=self.auth, headers=self.headers
        )
        if response.status_code == 201:
            return True
        elif response.status_code == 422 and update:
            url = '%s/%s' % (url, name)
            response = self.http.patch(
                url, json=data, auth=self.auth, headers=self.headers
            )
        response.raise_for_status()
        return False
