import os
from unittest.mock import patch

os.environ['SLACK_TOKEN'] = 'test'


patch('slackclient.SlackClient.api_call')
