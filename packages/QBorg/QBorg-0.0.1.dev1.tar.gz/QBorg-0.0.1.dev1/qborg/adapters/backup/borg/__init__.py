import os
import shutil
import subprocess
from distutils.version import StrictVersion
from re import search

from qborg.adapters.backup import IBackupAdapter


class BorgAdapter(IBackupAdapter):
    @classmethod
    def _find_borg_executable(cls, borg_bin='borg'):
        if os.path.isabs(borg_bin):
            _borg_realpath = os.path.abspath(borg_bin)
            if not os.path.isfile(_borg_realpath):
                raise ValueError(
                    'no borg executable found at %s' % _borg_realpath)
            return _borg_realpath
        else:
            _borg_realpath = shutil.which(borg_bin)
            if _borg_realpath is None:
                raise ValueError('borg executable could not be found')
            return _borg_realpath

    def __init__(self, borg_bin='borg'):
        # Find borg executable
        self.borg_bin = BorgAdapter._find_borg_executable(borg_bin)

    def get_borg_version(self):
        raise NotImplementedError('get_borg_version is not implemented')

    def is_min_version(self, versionstr):
        return self.get_borg_version() >= StrictVersion(versionstr)

    @classmethod
    def get_detected_version(cls, borg_bin='borg'):
        try:
            output = subprocess.check_output([borg_bin, "--version"], stderr=subprocess.STDOUT)
            if output:
                output_line = output.decode("utf-8")
                res = search("(\d+\.)*\d+", output_line).group(0)
                return StrictVersion(res)
        except FileNotFoundError:
            pass

        return None
