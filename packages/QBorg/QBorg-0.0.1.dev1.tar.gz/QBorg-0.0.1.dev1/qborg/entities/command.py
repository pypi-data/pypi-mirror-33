class Command():
    def __init__(self, thread):
        if thread is None:
            raise ValueError('thread must not be None')
        self._thread = thread

    def __eq__(self, other):
        if type(self) == type(other):
            return self._thread == other._thread

        return NotImplemented

    def __hash__(self):
        return hash((self._thread,))

    def start(self):
        self._thread.start()

    @property
    def is_running(self):
        return self._thread.is_alive()

    def join(self, timeout):
        self._thread.join(timeout)

        if self._thread.is_alive():
            raise TimeoutError
