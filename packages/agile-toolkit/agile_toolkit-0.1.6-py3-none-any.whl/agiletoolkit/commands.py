import os
import json

from dotenv import load_dotenv

load_dotenv()   # noqa

import click

from . import __version__
from .github import git
from .kong import kong

AGILE_CONFIG = os.environ.get('AGILE_CONFIG', 'agile.json')


@click.group(invoke_without_command=True)
@click.option(
    '--debug/--no-debug',
    is_flag=True,
    default=False,
    help='Run in debug mode'
)
@click.option(
    '--version',
    is_flag=True,
    default=False,
    help='Display version and exit'
)
@click.option(
    '--config', default=AGILE_CONFIG,
    type=click.Path(),
    help=f'Agile configuration json file location ({AGILE_CONFIG})'
)
@click.pass_context
def start(ctx, debug, version, config):
    """Commands for devops operations"""
    ctx.obj = {}
    ctx.DEBUG = debug
    if os.path.isfile(config):
        with open(config) as fp:
            agile = json.load(fp)
    else:
        agile = {}
    ctx.obj['agile'] = agile
    if version:
        click.echo(__version__)
        ctx.exit(0)
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())


start.add_command(git)
start.add_command(kong)
