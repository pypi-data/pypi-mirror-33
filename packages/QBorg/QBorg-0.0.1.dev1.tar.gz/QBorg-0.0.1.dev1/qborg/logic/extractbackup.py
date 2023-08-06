from qborg.adapters.backup import TooManyAttemptsError
from qborg.adapters.backup.borg.borg11adapter import MAX_PASSWORD_ATTEMPTS
from qborg.logic.factories import BackupAdapterFactory
from qborg.logic.wrapperdelegate import WrapperDelegate


class ExtractBackupLogic():
    def __init__(self):
        self.adapter = BackupAdapterFactory.get_adapter()

    def extract_local_backup(self, backup, target_path, delegate=None):
        attempt = 0

        def _run_extract():
            nonlocal attempt
            attempt += 1
            if attempt > MAX_PASSWORD_ATTEMPTS:
                raise TooManyAttemptsError(
                    'Reached maximum number of attempts to list repository %s',
                    backup.repository.name)

            self.adapter.extract_backup(backup.repository, backup.name, target_path, delegate=wrapper_delegate)

        class WrapperExtractBackupDelegate(WrapperDelegate):
            def run_logic(self):
                _run_extract()

        wrapper_delegate = WrapperExtractBackupDelegate(self, delegate)

        _run_extract()
