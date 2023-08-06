from qborg.adapters.backup import TooManyAttemptsError
from qborg.adapters.backup.borg.borg11adapter import MAX_PASSWORD_ATTEMPTS
from qborg.entities.repository import Repository
from qborg.logic.factories import BackupAdapterFactory
from qborg.logic.wrapperdelegate import WrapperDelegate
from qborg.qborg import QBorgApp


class CreateBackupLogic():
    def __init__(self):
        config_manager = QBorgApp.instance().config_manager

        self.adapter = BackupAdapterFactory.get_adapter()
        self.compression_modes = self.adapter.supported_compression_modes
        self.repositories = config_manager.config.repositories

    def get_repositories(self):
        return self.repositories

    def get_supported_compression_modes(self):
        return self.compression_modes

    def create_backup(self, repository, archive_name, compression_mode,
                      include_paths, exclude_paths,
                      access_unknown_repo=False, delegate=None):
        attempt = 0

        if not isinstance(repository, Repository):
            raise TypeError('repository is not a Repository')
        if not archive_name:
            raise ValueError('No archive_name given')
        if not isinstance(compression_mode, self.compression_modes):
            raise TypeError('compression_mode is of an invalid type. %s required' % self.compression_modes)

        def _run_create():
            nonlocal attempt
            attempt += 1
            if attempt > MAX_PASSWORD_ATTEMPTS:
                raise TooManyAttemptsError(
                    'Reached maximum number of attempts to list repository %s', repository.name)

            self.adapter.create_backup(
                repository, archive_name, compression_mode, include_paths,
                repository.encryption_mode, exclude_paths,
                access_unknown_repo=access_unknown_repo, delegate=wrapper_delegate)

        class WrapperCreateBackupDelegate(WrapperDelegate):
            def run_logic(self):
                _run_create()

        wrapper_delegate = WrapperCreateBackupDelegate(self, delegate)

        _run_create()
