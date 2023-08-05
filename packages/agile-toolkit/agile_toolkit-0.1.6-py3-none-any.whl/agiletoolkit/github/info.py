import json

import click

from ..utils import gitrepo


@click.command()
def info():
    """Display information about repository
    """
    info = gitrepo()
    click.echo(json.dumps(info, indent=4))
