
import collections.abc
import logging
import time
import typing as t
import websocket

# import slackclient

from .slack_bot import SlackBot

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.DEBUG)


class SlackRtmBot(SlackBot):

    """RTM bot for Slack."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rtm_reconnected_count: int = 0
        # Number of reconnection attempts since last successful connection ended.
        self._rtm_reconnect_limit: int = 7
        self._sleep_min: float = 0.1
        self._sleep_max: float = self._sleep_min * (2 ** self._rtm_reconnect_limit)
        self._sleep_time: float = self._sleep_min

    @property
    def within_rtm_reconnect_limit(self) -> bool:
        return self._rtm_reconnect_limit is None \
            or self._rtm_reconnected_count < self._rtm_reconnect_limit

    @property
    def sleep_bounds(self) -> t.Tuple[float, float]:
        return self._sleep_min, self._sleep_max

    @sleep_bounds.setter
    def sleep_bounds(self, sleep_min: float, sleep_max: float) -> None:
        assert isinstance(sleep_min, float)
        assert isinstance(sleep_max, float)
        self._sleep_min = sleep_min
        self._sleep_max = sleep_max

    def rtm_reconnect(self) -> t.Optional[bool]:
        """Attempt to reconnect with Slack once unless over reconnection limit.

        Return a bool iff reconnection attempt was made.
        """
        if not self.within_rtm_reconnect_limit:
            _LOG.error(
                'too many consecutive unsuccessful reconnection attempts (limit is %i),'
                ' connection attempt aborted.', self._rtm_reconnect_limit)
            return None
        self._rtm_reconnected_count += 1
        if self.rtm_connect():
            self._rtm_reconnected_count = 0
            _LOG.info('connected.')
            return True
        _LOG.debug('cannot connect.')
        return False

    def rtm_reconnect_persistent(self) -> bool:
        """Attempt to reconnect with Slack many times until reaching reconnection limits."""
        while True:
            result = self.rtm_reconnect()
            if result is True:
                return True
            if result is None:
                return False

    def rtm_read_handled(self) -> t.Optional[collections.abc.Sequence]:
        """Perform a read while doing best not to throw any exception."""
        data = None
        try:
            data = self.rtm_read()
        except TimeoutError:
            _LOG.debug('rtm_read() failed', exc_info=True)
        except BrokenPipeError:
            _LOG.debug('rtm_read() failed', exc_info=True)
        except websocket.WebSocketConnectionClosedException:
            _LOG.debug('rtm_read() failed', exc_info=True)
        return data

    def rtm_read_persistent(self) -> t.Optional[collections.abc.Sequence]:
        """Try to read until success or prefedined number of retries."""
        data = None
        while True:
            try:
                data = self.rtm_read_handled()
            except AttributeError:
                _LOG.info('connecting for the 1st time...')
                if self.rtm_reconnect_persistent():
                    continue
            if data is None and self.within_rtm_reconnect_limit:
                _LOG.info('reconnecting...')
                if self.rtm_reconnect_persistent():
                    continue
            break
        return data

    def rtm_read_loop_iteration(self) -> bool:
        """Run single iteration of a bot life cycle."""
        # read data
        data = self.rtm_read_persistent()
        # handle result
        handler_result = False
        if data:
            try:
                handler_result = self._handler(data)
            except Exception:
                _LOG.exception('handler error when processing: %s', data)
                handler_result = None
        elif not self.within_rtm_reconnect_limit:
            handler_result = None
        # interpret handler's feedback
        if handler_result is None:
            _LOG.info('stopped.')
            return False
        elif handler_result is True:
            if self._sleep_time > self._sleep_min:
                self._sleep_time = self._sleep_min
                _LOG.info('reactivated.')
        elif handler_result is False:
            _LOG.debug('waiting for %fs...', self._sleep_time)
            time.sleep(self._sleep_time)
            if self._sleep_time < self._sleep_max:
                self._sleep_time *= 2
                if self._sleep_time > self._sleep_max:
                    self._sleep_time = self._sleep_max
        else:
            raise RuntimeError('handler result must be True, False or None, but it was: {}'
                               .format(handler_result))
        return True

    def rtm_read_loop(self) -> None:
        """Start bot lifecycle."""
        while self.rtm_read_loop_iteration():
            pass
