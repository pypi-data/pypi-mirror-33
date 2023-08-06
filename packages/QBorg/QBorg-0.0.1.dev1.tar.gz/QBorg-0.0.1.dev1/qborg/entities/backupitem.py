class BackupItem():
    def __new__(cls, type, *args, **kwargs):
        if cls is BackupItem:
            if 'd' == type:
                _real_class = BackupDirectory
            elif '-' == type:
                _real_class = BackupFile
            return _real_class.__new__(_real_class, type, *args, **kwargs)
        return object.__new__(cls)

    def __init__(self, mode, path, user, group, size, mtime):
        if isinstance(self, BackupItem):
            raise RuntimeError('BackupItem cannot be initialised')

        self._attributes = dict()

        self._mode = mode
        self._path = path
        self._user = user
        self._group = group
        self._size = size
        self._mtime = mtime

    def __eq__(self, other):
        if type(self) == type(other):
            return vars(self) == vars(other)

        return NotImplemented

    def __hash__(self):
        return hash((self._healthy, self._mtime, self._path, self._size, self._type))

    def __str__(self):
        return "[%s]" % (self.path)

    @property
    def attributes(self):
        return self._attributes

    @property
    def type(self):
        return self._type

    @property
    def mode(self):
        return self._mode

    @property
    def path(self):
        return self._path

    @property
    def user(self):
        return self._user

    @property
    def mtime(self):
        return self._mtime

    @property
    def group(self):
        return self._group

    @property
    def size(self):
        return self._size


class BackupDirectory(BackupItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._children = dict()
        self._type = 'd'

    @property
    def children(self):
        return self._children

class BackupFile(BackupItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._type = '-'

    def to_table_row(self):
        return [self.path, self.size, self.mtime, self.healthy]
