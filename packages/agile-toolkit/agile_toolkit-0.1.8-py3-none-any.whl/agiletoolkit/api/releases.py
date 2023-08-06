import os
import stat
import mimetypes
import logging
from urllib.parse import urlsplit

from .components import RepoComponents, GithubException
from ..utils import semantic_version


logger = logging.getLogger(__file__)

ONEMB = 2**20


class Assets(RepoComponents):
    pass


class Releases(RepoComponents):
    """Github repository endpoints
    """
    @property
    def assets(self):
        return Assets(self)

    def latest(self):
        """Get the latest release of this repo
        """
        url = '%s/latest' % self
        response = self.http.get(url, auth=self.auth)
        if response.status_code == 200:
            return response.json()
        elif response.status_code != 404:
            response.raise_for_status()

    def tag(self, tag):
        """Get a release by tag
        """
        url = '%s/tags/%s' % (self, tag)
        response = self.http.get(url, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def delete(self, id=None, tag=None):
        if tag:
            assert not id, "provide either tag or id to delete"
            release = self.tag(tag)
            id = release['id']
        assert id, "id not given"
        return super().delete(id)

    def release_assets(self, release):
        """Assets for a given release
        """
        release = self.as_id(release)
        return self.get_list(url='%s/%s/assets' % (self, release))

    def upload(self, release, filename, content_type=None):
        """Upload a file to a release

        :param filename: filename to upload
        :param content_type: optional content type
        :return: json object from github
        """
        release = self.as_id(release)
        name = os.path.basename(filename)
        if not content_type:
            content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            raise ValueError('content_type not known')
        inputs = {'name': name}
        url = '%s%s/%s/assets' % (self.uploads_url,
                                  urlsplit(self.api_url).path,
                                  release)
        info = os.stat(filename)
        size = info[stat.ST_SIZE]
        response = self.http.post(
            url, data=stream_upload(filename), auth=self.auth,
            params=inputs,
            headers={'content-type': content_type,
                     'content-length': str(size)})
        response.raise_for_status()
        return response.json()

    def validate_tag(self, tag_name, prefix=None):
        """Validate ``tag_name`` with the latest tag from github

        If ``tag_name`` is a valid candidate, return the latest tag from github
        """
        new_version = semantic_version(tag_name)
        current = self.latest()
        if current:
            tag_name = current['tag_name']
            if prefix:
                tag_name = tag_name[len(prefix):]
            tag_name = semantic_version(tag_name)
            if tag_name >= new_version:
                what = 'equal to' if tag_name == new_version else 'older than'
                raise GithubException(
                    'Your local version "%s" is %s '
                    'the current github version "%s".\n'
                    'Bump the local version to '
                    'continue.' %
                    (
                        str(new_version),
                        what,
                        str(tag_name)
                    )
                )
        return current


def stream_upload(filename):
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(ONEMB)
            if not chunk:
                break
            yield chunk
