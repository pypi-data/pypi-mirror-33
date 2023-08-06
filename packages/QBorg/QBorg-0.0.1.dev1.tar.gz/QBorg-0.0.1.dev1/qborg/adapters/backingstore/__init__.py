class IBackingStoreAdapter():
    @property
    def protocol(self):
        return self._protocol_name

    @property
    def is_mounted(self):
        return self._is_mounted

    def borg_url(self, path):
        raise NotImplementedError('borg_url is not implemented')

    def posix_path(self, path):
        raise NotImplementedError('posix_path is not implemented')

    def mount(self):
        raise NotImplementedError('mount is not implemented')

    def unmount(self):
        raise NotImplementedError('unmount is not implemented')

    def exists(self, path):
        raise NotImplementedError('exists is not implemented')
