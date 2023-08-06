import os
import re
import json
import subprocess
from asyncio import get_event_loop
from contextlib import contextmanager

import click


PR_RE = re.compile('pr-*')
FORMAT = '%n'.join(['%H', '%aN', '%ae', '%cN', '%ce', '%s'])


class CommandError(click.ClickException):
    pass


def wait(awaitable):
    get_event_loop().run_until_complete(awaitable)


def deep_merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        else:
            destination[key] = value
    return destination


def sh(command, cwd=None, echo=None, env=None):
    if echo:
        echo(command)
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=cwd,
        env=env,
        universal_newlines=True
    )
    p.wait()
    out, err = p.communicate()
    if p.returncode and err:
        raise CommandError(err)
    elif err:
        print(err)
    return out


def shi(command, cwd=None, echo=None, env=None):
    env = env or {}
    if echo:
        echo(command)
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=cwd,
        env=dict(os.environ, **env),
        universal_newlines=True
    )
    while True:
        line = p.stdout.readline()
        if not line:
            break
        print(line.rstrip())
    p.wait()
    err = p.stderr.read()
    if p.returncode and err:
        raise CommandError(err)
    elif err:
        print(err)


@contextmanager
def command():
    try:
        yield
    except CommandError as exc:
        raise


def error(exc):
    click.secho('ERROR: %s' % exc, err=True, fg='red', bold=True)


def niceJson(data):
    if isinstance(data, str):
        data = json.loads(data)
    return json.dumps(data, indent=4)


def semantic_version(tag):
    """Get a valid semantic version for tag
    """
    try:
        version = list(map(int, tag.split('.')))
        assert len(version) == 3
        return tuple(version)
    except Exception as exc:
        raise CommandError(
            'Could not parse "%s", please use '
            'MAJOR.MINOR.PATCH' % tag
        ) from exc


def gitrepo(root=None):
    if not root:
        cwd = root = os.getcwd()
    else:
        cwd = os.getcwd()
        if cwd != root:
            os.chdir(root)
    gitlog = sh('git --no-pager log -1 --pretty="format:%s"' % FORMAT,
                cwd=root).split('\n', 5)
    branch = sh('git symbolic-ref HEAD --short 2>/dev/null', cwd=root).strip()
    if not branch:
        branch = sh(
            "git branch -a --contains HEAD | sed -n 2p | awk '{ printf $1 }'"
        )
    if branch.startswith('remotes/origin/'):
        branch = branch[15:]
    try:
        current_tag = sh('git tag --points-at HEAD')
    except CommandError:
        current_tag = ''
    try:
        tag = sh('git describe --tags --abbrev=0')
    except CommandError:
        tag = ''
    tag = tag.strip()
    current_tag = current_tag.strip()
    remotes = [x.split() for x in
               filter(lambda x: x.endswith('(fetch)'),
                      sh('git remote -v', cwd=root).strip().splitlines())]
    if cwd != root:
        os.chdir(cwd)
    return {
        "head": {
            "id": gitlog[0],
            "author_name": gitlog[1],
            "author_email": gitlog[2],
            "committer_name": gitlog[3],
            "committer_email": gitlog[4],
            "message": gitlog[5].strip(),
        },
        "branch": branch,
        "current_tag": current_tag,
        "tag": tag,
        "pr": bool(PR_RE.match(branch)),
        "remotes": [{'name': remote[0], 'url': remote[1]}
                    for remote in remotes]
    }


def version():
    return sh('make version').strip().split()[-1]
