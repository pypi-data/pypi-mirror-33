
import logging

import slackclient
import slackeventsapi

from .slack_bot import SlackBot

_LOG = logging.getLogger(__name__)


class SlackEventBot(SlackBot):

    """Event-based bot for Slack."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
