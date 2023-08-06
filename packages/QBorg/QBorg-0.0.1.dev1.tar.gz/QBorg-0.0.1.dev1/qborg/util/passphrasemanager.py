import datetime
import functools
import logging
import time
import threading

from collections import namedtuple


_logger = logging.getLogger(__name__)


def static(**assignments):
    def wrap(func):
        statics = namedtuple('Static', assignments.keys())
        for k, v in assignments.items():
            setattr(statics, k, v)
        return lambda *args, **kwargs: func(*args, static=statics, **kwargs)
    return wrap


class PassphraseEntry:
    def __init__(self, value=None, atime=datetime.datetime.now()):
        self.value = value
        self.atime = atime


class PassphraseManager():
    @static(store=dict())
    def __init__(self, static, keep_time=datetime.timedelta(minutes=3)):
        self._keep_time = keep_time
        self._cleanup_thread = None
        self.get = functools.partial(self.__get, static=static)
        self.set = functools.partial(self.__set, static=static)
        self.unset = functools.partial(self.__unset, static=static)

    def __cleanup(self, store):
        def __run():
            while 0 < len(store):
                # Sleep until next cleanup run
                oldest_atime = min([v.atime for v in store.values()])
                next_run = oldest_atime + self._keep_time
                time.sleep((next_run - datetime.datetime.now()).seconds + 1)

                def expired(v): return now > (v.atime + self._keep_time)
                now = datetime.datetime.now()
                for k in [k for k, v in store.items() if expired(v)]:
                    _logger.debug('Deleting passphrase %s' % k)
                    del store[k]

        if not (self._cleanup_thread and self._cleanup_thread.is_alive()):
            # Start on own thread if not running there
            self._cleanup_thread = threading.Thread(target=__run)
            self._cleanup_thread.start()

    def __get(self, name, static, update_atime=True):
        _logger.debug('Looking up passphrase for repository %s', name)
        try:
            el = None
            el = static.store[name]
            if update_atime:
                el.atime = datetime.datetime.now()
            return el.value
        finally:
            del el
            self.__cleanup(static.store)

    def __set(self, name, value, static):
        if 0 < self._keep_time.seconds:
            static.store[name] = PassphraseEntry(value=value, atime=datetime.datetime.now())
            self.__cleanup(static.store)

    def __unset(self, name, static):
        try:
            del static.store[name]
            _logger.debug('Passphrase was unset for repository %s', name)
        except KeyError:
            pass
