from qborg.logic.factories import BackupAdapterFactory


class ListBackupLogic():
    def __init__(self):
        self.adapter = BackupAdapterFactory.get_adapter()

    def list_backup(self, backup, password=None, delegate=None):
        return self.adapter.list_archive(
            repository=backup.repository, archive_name=backup.name,
            access_unknown_repo=False, delegate=delegate)
