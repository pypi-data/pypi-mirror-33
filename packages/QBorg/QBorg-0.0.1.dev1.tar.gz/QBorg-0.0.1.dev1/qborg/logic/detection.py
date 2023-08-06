from qborg.adapters.backup.borg import BorgAdapter


class ToolDetection():
    _borg_version = None

    @classmethod
    def get_borg_version(cls, borg_bin="borg"):
        if cls._borg_version is None:
            cls._borg_version = BorgAdapter.get_detected_version(borg_bin)

        return cls._borg_version
