import os
import asyncio
from typing import Dict

import yaml

from jinja2 import Template

from . import utils


NAMESPACES = {
    'local', 'development', 'dev', 'stage', 'prod', 'sandbox', 'production'
}


class Manager:

    def __init__(self, config=None, path=None, yes=False, namespace=None):
        self.config = config or {}
        self.path = path or os.getcwd()
        self.deploy_path = os.path.join(self.path, 'deploy')
        self.yes = yes
        self.message_brokers = []
        self.namespace = namespace
        self.init()

    def init(self):
        pass

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
