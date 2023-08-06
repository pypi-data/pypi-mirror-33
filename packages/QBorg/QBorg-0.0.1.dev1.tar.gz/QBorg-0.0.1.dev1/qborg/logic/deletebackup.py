from qborg.adapters.backup import TooManyAttemptsError
from qborg.adapters.backup.borg.borg11adapter import MAX_PASSWORD_ATTEMPTS
from qborg.logic.factories import BackupAdapterFactory
from qborg.logic.wrapperdelegate import WrapperDelegate


class DeleteBackupLogic:
    def __init__(self):
        self.adapter = BackupAdapterFactory.get_adapter()

    def delete_local_backup(self, backup, delegate=None):
        attempt = 0

        def _run_delete():
            nonlocal attempt
            attempt += 1
            if attempt > MAX_PASSWORD_ATTEMPTS:
                raise TooManyAttemptsError(
                    'Reached maximum number of attempts to list repository %s',
                    backup.repository.name)

            self.adapter.delete_archive(backup.repository, backup.name, delegate=wrapper_delegate)

        class WrapperDeleteBackupDelegate(WrapperDelegate):
            def run_logic(self):
                _run_delete()

        wrapper_delegate = WrapperDeleteBackupDelegate(self, delegate)

        _run_delete()
