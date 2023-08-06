import os

from pathlib import Path

from qborg.adapters.backingstore import IBackingStoreAdapter


_root_path = os.path.abspath(os.path.sep)
_slashdot = _root_path + os.path.curdir


class FileBackingStoreAdapter(IBackingStoreAdapter):
    _protocol_name = 'file'

    def __init__(self, mountpoint=_root_path):
        if mountpoint != _root_path:
            raise NotImplementedError('As of now only the root mountpoint is supported')

        self.mountpoint = os.path.realpath(mountpoint)

        # The local root filesystem is always mounted
        self._is_mounted = True

    def _is_subpath(self, path):
        mntpath = Path(self.mountpoint)
        realpath = Path(os.path.realpath(path))  # eliminate symlinks
        return mntpath == realpath or mntpath in realpath.parents

    def borg_url(self, path):
        return ('file://' + self.posix_path(path))

    def posix_path(self, path):
        # We prepend a slashdot here because os.path.abspath does not strip multiple leading slashes
        abspath = os.path.abspath(os.path.sep.join([_slashdot, self.mountpoint, path]))

        if not self._is_subpath(abspath):
            raise PermissionError('The path %s is not within mountpoint %s' % (path, self.mountpoint))

        return abspath

    def mount(self):
        pass

    def unmount(self):
        pass

    def exists(self, path):
        return os.path.exists(self.posix_path(path))
