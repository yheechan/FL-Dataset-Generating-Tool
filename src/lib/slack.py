import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Slack:
    """
    Slack class to send messages to a Slack channel
    """
    def __init__(self, channel_name=None, bot_name="Un-Named Bot"):
        self.client = WebClient(token=os.environ["SLACK_TOKEN"])
        self.channel_name = channel_name
        self.deactivated = False
        if channel_name is None:
            self.deactivated = True
        self.bot_name = bot_name

    def send_message(self, msg):
        if self.deactivated:
            return
        try:
            self.client.chat_postMessage(
                channel=self.channel_name,
                text=msg,
                username=self.bot_name
            )
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
