import logging

from qborg.entities.location import Location
from qborg.entities.repository import Repository
from qborg.logic.factories import BackupAdapterFactory
from qborg.logic.wrapperdelegate import WrapperDelegate
from qborg.qborg import QBorgApp

_logger = logging.getLogger(__name__)


class InitRepoLogic():
    def __init__(self):
        self.adapter = BackupAdapterFactory.get_adapter()

    def get_supported_backing_stores(self):
        # FIXME
        return ['file']

    def get_supported_encryption_modes(self):
        return self.adapter.supported_encryption_modes

    def check_valid_new_repo_name(self, name):
        if not isinstance(name, str):
            raise TypeError('Name is not a string')
        if not name:
            raise ValueError('Name is empty')

        try:
            config_manager = QBorgApp.instance().config_manager
            repositories = config_manager.config.repositories
            if repositories[name]:
                raise ValueError('Name already taken')
        except KeyError:
            # No such repository exists at this point
            return True

    def init_repository(self, name, backing_store, path, encryption_mode,
                        password=None, delegate=None, callback=None):
        try:
            self.check_valid_new_repo_name(name)
        except Exception as e:
            _logger.error('Repository with name %s already exists', name)
            raise e

        class WrapperInitRepoDelegate(WrapperDelegate):
            def process_finished(self, rc):
                super().process_finished(rc)
                if 0 == rc:
                    _logger.info('Success! Adding repository %s to config' % repository.name)

                    # Persist repository
                    try:
                        config_manager = QBorgApp.instance().config_manager
                        config_manager.config.repositories.add(repository)
                        config_manager.save_config()
                    except Exception:
                        _logger.error('Adding repository %s to config failed!' % repository.name)

                    # Cache set passphrase in PassphraseManager so that the
                    # repository can be loaded without having to enter the
                    # passphrase again.
                    passphrase_manager = QBorgApp.instance().passphrase_manager
                    passphrase_manager.set(repository.name, password)

                    # Call back
                    if callable(callback):
                        callback(repository)
                else:
                    _logger.error(self.last_error if self.last_error else 'Unknown error!')

        location = Location(backing_store, path)
        encryption_mode = self.adapter.supported_encryption_modes(encryption_mode)

        # Passed into the wrapper delegate
        repository = Repository(name, location, encryption_mode)

        wrapper_delegate = WrapperInitRepoDelegate(self, delegate)

        command = self.adapter.init_repository(
            location, encryption_mode, password=password,
            delegate=wrapper_delegate)
        return command
