
import collections.abc
import logging
import typing as t

import slackclient

_LOG = logging.getLogger(__name__)


def default_handler(records: collections.abc.Sequence) -> t.Optional[bool]:
    """Print the records on screen and return True.

    Recipe to build a handler:

    Handle records, which should be a sequence.

    Return:
    - True if bot should awake
    - False if bot should continue sleeping
    - None if bot should stop

    If any exception is raised, it will be caught by the bot and bot will behave
    as if None was returned
    """
    print(records)
    return True


class SlackBot(slackclient.SlackClient):

    """Bot for Slack."""

    def __init__(self, username: str, *args, **kwargs):
        assert isinstance(username, str), type(username)
        assert username
        super().__init__(*args, **kwargs)
        self._username = username
        self._userid = self.query_userid(username)
        self._handler = default_handler

    @property
    def username(self) -> str:
        return self._username

    @property
    def userid(self) -> str:
        return self._userid

    @property
    def handler(self) -> t.Callable[[collections.abc.Sequence], t.Optional[bool]]:
        return self._handler

    @handler.setter
    def handler(self, handler: t.Callable[[collections.abc.Sequence], t.Optional[bool]]) -> None:
        assert isinstance(handler, collections.abc.Callable)
        self._handler = handler

    def query_userid(self, username: str) -> str:
        users = self.api_call('users.list')['members']
        _LOG.debug('users: %s', users)
        user_data = [_ for _ in users if _['name'] == username][0]
        _LOG.debug('user_data: %s', user_data)
        userid = user_data['id']
        return userid

    def query_user_channel_ids(self) -> t.List[str]:
        channels = self.api_call('channels.list')
        private_channels = self.api_call('groups.list')['groups']
        dm_channels = self.api_call('im.list')['ims']
        _LOG.info(
            '%i public + %i private + %i DM = %i', len(channels), len(private_channels),
            len(dm_channels), len(channels) + len(private_channels) + len(dm_channels))
        _LOG.debug('public: %s', channels)
        _LOG.debug('private: %s', private_channels)
        _LOG.debug('DM: %s', dm_channels)
        user_channels = [_ for _ in dm_channels if _['is_im'] is True]
        _LOG.debug('user channels: %s', user_channels)
        user_channels_ids = [_['id'] for _ in user_channels]
        return user_channels_ids
