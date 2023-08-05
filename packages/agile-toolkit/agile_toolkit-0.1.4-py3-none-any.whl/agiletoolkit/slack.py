import os
from slackclient import SlackClient


class SlackIntegration:
    token = os.environ.get('SLACK_TOKEN')

    def __init__(self, manager):
        self.manager = manager
        self.channel = manager.config.get('slack_channel', 'agile')
        self.cli = SlackClient(self.token)

    @classmethod
    def add(cls, manager):
        if cls.token:
            manager.message_brokers.append(cls(manager))

    def __call__(self, message):
        info = self.manager.info
        repo = self.manager.github_repo().repo_path
        sha = info['head']['id']
        commit = 'https://github.com/%s/commit/%s' % (repo, sha)
        message = '*%s* - %s\nby %s <%s>\n%s' % (
            repo,
            info['branch'],
            info['head']['committer_name'],
            info['head']['committer_email'],
            message
        )
        attachments = [
            dict(
                fallback="Git commit %s" % commit,
                actions=[
                    dict(
                        type="button",
                        text="Git commit",
                        url=commit
                    )
                ]
            )
        ]

        self.cli.api_call(
            'chat.postMessage',
            channel=self.channel,
            text=message,
            attachments=attachments
        )
