import logging

from qborg.adapters.backup import TooManyAttemptsError
from qborg.adapters.backup.borg.borg11adapter import MAX_PASSWORD_ATTEMPTS
from qborg.logic.factories import BackupAdapterFactory
from qborg.logic.wrapperdelegate import WrapperDelegate
from qborg.qborg import QBorgApp

_logger = logging.getLogger(__name__)


class DeleteRepoLogic():
    def __init__(self):
        self.adapter = BackupAdapterFactory.get_adapter()
        self.config_manager = QBorgApp.instance().config_manager

    def delete_repository(self, repository, delegate=None):
        def _delete_from_config(repository):
            try:
                config_manager = QBorgApp.instance().config_manager
                config_manager.config.repositories.discard(repository)
                config_manager.save_config()
            except Exception:
                _logger.error('Deleting repository %s from config failed!' % repository.name)

        attempt = 0

        def _run_delete():
            nonlocal attempt
            attempt += 1
            if attempt > MAX_PASSWORD_ATTEMPTS:
                raise TooManyAttemptsError(
                    'Reached maximum number of attempts to list repository %s', repository.name)

            self.adapter.delete_repository(repository, delegate=wrapper_delegate)

        class WrapperDeleteRepoDelegate(WrapperDelegate):
            def process_finished(self, rc):
                super().process_finished(rc)
                if 0 == rc:
                    _logger.info('Success! Deleting repository %s from config' % repository.name)

                    # Delete repository from config
                    _delete_from_config(repository)

            def run_logic(self):
                _run_delete()

        if repository.location.backingstore.exists(repository.location.path):
            wrapper_delegate = WrapperDeleteRepoDelegate(self, delegate)

            _run_delete()
        else:
            _logger.warning('Repository %s does not exist at URL %s! '
                            'Just removing entry from config.',
                            repository.name, repository.location.borg_url)
            _delete_from_config(repository)

            # Pretend the Borg process has finished
            delegate.process_finished(rc=0)
