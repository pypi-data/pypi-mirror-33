import click

from ..utils import command
from ..repo import RepoManager


@click.command()
@click.pass_context
def remote(ctx):
    """Display repo github path
    """
    with command():
        m = RepoManager(ctx.obj['agile'])
        click.echo(m.github_repo().repo_path)
