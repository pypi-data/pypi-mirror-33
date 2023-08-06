from qborg.logic.factories import BackingStoreAdapterFactory


class Location():
    def __init__(self, backingstore, path):
        self._backingstore = backingstore
        self._path = path

    def __eq__(self, other):
        if type(self) == type(other):
            return self._backingstore == self._backingstore and self._path == other._path

        return NotImplemented

    def __hash__(self):
        return hash((self._backingstore, self._path))

    @property
    def backingstore(self):
        return self._backingstore

    @property
    def path(self):
        return self._path

    @property
    def borg_url(self):
        return self._backingstore.borg_url(self._path)

    @property
    def posix_path(self):
        return self._backingstore.posix_path(self._path)

    def dump(self):
        return {
            'backingstore': self._backingstore.protocol,
            'path': self._path
        }

    @classmethod
    def load(cls, obj):
        if not isinstance(obj, dict):
            raise TypeError('obj must be a serialized location dict')

        try:
            backingstore_url = obj['backingstore']
            path = obj['path']
        except KeyError as e:
            raise ValueError('Serialized Location object does not contain %s' % e.args[0])

        backingstore = BackingStoreAdapterFactory.adapter_for_url(backingstore_url)
        return Location(backingstore, path)
