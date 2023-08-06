import click


def get_repos(labels):
    if not labels:
        click.echo(
            'You need to specify the "labels" object in the config file',
            error=True
        )
        click.exit()
    repos = labels.get('repositories')
    if not isinstance(repos, list):
        click.echo(
            'You need to specify the "repos" list in the config '
            'labels object file',
            error=True
        )
        click.exit()
    return repos
