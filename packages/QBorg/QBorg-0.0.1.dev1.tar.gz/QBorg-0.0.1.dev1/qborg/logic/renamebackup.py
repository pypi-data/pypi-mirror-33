from qborg.adapters.backup import TooManyAttemptsError
from qborg.adapters.backup.borg.borg11adapter import MAX_PASSWORD_ATTEMPTS
from qborg.entities.repository import Repository
from qborg.logic.factories import BackupAdapterFactory
from qborg.logic.wrapperdelegate import WrapperDelegate
from qborg.qborg import QBorgApp


class RenameBackupLogic():
    def __init__(self):
        self.adapter = BackupAdapterFactory.get_adapter()
        self.config_manager = QBorgApp.instance().config_manager

    def rename_local_backup(self, backup_entity, archive_name, access_unknown_repo=False, delegate=None):
        if not isinstance(backup_entity.repository, Repository):
            raise TypeError('repository is not a Repository')
        if not archive_name:
            raise ValueError('No archive_name given')

        attempt = 0

        def _run_rename():
            nonlocal attempt
            attempt += 1
            if attempt > MAX_PASSWORD_ATTEMPTS:
                raise TooManyAttemptsError(
                    'Reached maximum number of attempts to list repository %s', backup_entity.repository.name)

            self.adapter.rename_archive(backup_entity, archive_name,
                                        access_unknown_repo=access_unknown_repo, delegate=wrapper_delegate)

        class WrapperRenameBackupDelegate(WrapperDelegate):
            def run_logic(self):
                _run_rename()

        wrapper_delegate = WrapperRenameBackupDelegate(self, delegate)

        _run_rename()
