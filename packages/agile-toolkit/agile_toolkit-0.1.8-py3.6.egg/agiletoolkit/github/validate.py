import click

from ..repo import RepoManager


@click.command()
@click.option(
    '--stage', is_flag=True,
    help='Validate only on stage/deploy branch', default=False)
@click.pass_context
def validate(ctx, stage):
    """Check if version of repository is semantic
    """
    m = RepoManager(ctx.obj['agile'])
    if not stage or m.can_release('stage'):
        click.echo(m.validate_version())
