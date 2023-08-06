from datetime import datetime

from qborg.adapters.backup import NoPassphraseError
from qborg.entities.backup import Backup
from qborg.entities.repository import Repository
from qborg.logic.controllerdelegate import ControllerDelegate
from qborg.logic.createbackup import CreateBackupLogic
from qborg.ui.pyqt4.guis.createbackup import CreateBackupGui


class CreateBackupDelegate(ControllerDelegate):
    last_error = None

    def __init__(self, controller, parent, callback=None):
        super().__init__(controller, parent, title='Creating Backup...')
        self.callback = callback

    def success(self):
        super().success()
        if callable(self.callback):
            self.callback()
        self.parent.close()


class CreateBackupController():
    def __init__(self, selected_repository_entity, parent=None, callback=None):
        self.logic = CreateBackupLogic()
        self.compression_modes = self.logic.get_supported_compression_modes()
        self.repositories = self.logic.get_repositories()
        self.parent = parent
        self.callback = callback

        self.widget = CreateBackupGui(
            selected_repository_entity, self.repositories, self.compression_modes,
            controller=self)

    def get_supported_compression_modes(self):
        return self.logic.get_supported_compression_modes()

    def check_model(self, model):
        message = None

        if not isinstance(model.repository, Repository):
            message = 'Please choose a repository'
        elif not model.archive_name:
            message = 'Please enter a name for your backup'
        elif not isinstance(model.compression_mode, self.compression_modes):
            message = 'Please select a compression mode'
        elif 0 >= len(model.include_paths):
            message = 'Please choose some directories and files for your backup'

        return (False if message else True), message

    def btn_accept_click(self, model):
        model_dict = vars(model)
        _start_time = datetime.now()

        def callback():
            if callable(self.callback):
                self.callback(Backup(
                    name=model_dict['archive_name'],
                    time=_start_time,
                    repository=model_dict['repository']))

        # Run process
        delegate = CreateBackupDelegate(self, self.widget, callback=callback)
        try:
            self.logic.create_backup(delegate=delegate, **model_dict)
        except NoPassphraseError:
            delegate.close_dialog()
            self.widget.show_error_message_box(
                message='Password required',
                message_detail='Backup cannot be created without repository password')
