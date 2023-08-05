import click

from ..utils import niceJson
from ..repo import RepoManager


@click.command()
@click.pass_context
@click.option(
    '--yes', is_flag=True,
    help='Commit changes to github', default=False)
@click.option(
    '--latest', is_flag=True,
    help='Show latest release in github', default=False)
def release(ctx, yes, latest):
    """Create a new release in github
    """
    m = RepoManager(ctx.obj['agile'])
    api = m.github_repo()
    if latest:
        latest = api.releases.latest()
        if latest:
            click.echo(latest['tag_name'])
    elif m.can_release('stage'):
        branch = m.info['branch']
        version = m.validate_version()
        name = 'v%s' % version
        body = ['Release %s from agiletoolkit' % name]
        data = dict(
            tag_name=name,
            target_commitish=branch,
            name=name,
            body='\n\n'.join(body),
            draft=False,
            prerelease=False
        )
        if yes:
            data = api.releases.create(data=data)
            m.message('Successfully created a new Github release')
        click.echo(niceJson(data))
    else:
        click.echo('skipped')
