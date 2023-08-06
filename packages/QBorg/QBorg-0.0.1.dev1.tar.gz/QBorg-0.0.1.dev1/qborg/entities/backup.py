class Backup():
    def __init__(self, name, time, repository):
        self._name = name
        self._time = time
        self._repository = repository
        self._files = []

    def __eq__(self, other):
        if type(self) == type(other):
            return vars(self) == vars(other)

        return NotImplemented

    def __hash__(self):
        return hash((self._time, self._repository))

    def __str__(self):
        return "[%s]: %s" % (self.time, self.name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def repository(self):
        return self._repository

    @property
    def time(self):
        return self._time

    @property
    def files(self):
        return self._files

    # used for the table for its files
    def table_row_header(self):
        return ['Path', 'Size', 'Time', 'Health Status']

    def to_table_row(self):
        return [self.name, self.time]


class BackupFile():
    def __init__(self, healthy, mtime, path, size, qtype):
        self._healthy = healthy
        self._mtime = mtime
        self._path = path
        self._size = size
        self._qtype = qtype

    def __eq__(self, other):
        if type(self) == type(other):
            return vars(self) == vars(other)

        return NotImplemented

    def __hash__(self):
        return hash((self._healthy, self._mtime, self._path, self._size, self._qtype))

    def __str__(self):
        return "[%s]" % (self.path)

    @property
    def healthy(self):
        return self._healthy

    @property
    def mtime(self):
        return self._mtime

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def size(self):
        return self._size

    # renamed to avoid confusion with python type
    @property
    def qtype(self):
        return self._qtype

    def to_table_row(self):
        return [self.path, self.size, self.mtime, self.healthy]
