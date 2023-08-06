import click

from kong.client import Kong, KongError

from .repo import RepoManager
from .import utils


@click.command()
@click.pass_context
@click.option('--namespace', default='dev', help='target namespace')
@click.option(
    '--yes', is_flag=True,
    help='commit changes to kong', default=False)
def kong(ctx, namespace, yes):
    """Update the kong configuration
    """
    m = KongManager(ctx.obj['agile'], namespace=namespace)
    click.echo(utils.niceJson(m.create_kong(yes)))


class KongManager(RepoManager):

    def create_kong(self, yes):
        data = self.load_data('values.yaml')
        values = data.copy()
        manifest = self.manifest(values, 'kong.yaml')
        if yes:
            return self.wait(self.apply_kong(manifest))
        else:
            return manifest

    async def apply_kong(self, manifest):
        async with Kong() as cli:
            try:
                result = await cli.apply_json(manifest)
            except KongError as exc:
                raise utils.CommandError(f'Kong Error: {exc}') from None
            return result
