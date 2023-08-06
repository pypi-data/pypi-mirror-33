from PyQt4.QtGui import QMessageBox

from qborg.adapters.backup import NoPassphraseError
from qborg.logic.controllerdelegate import ControllerDelegate
from qborg.logic.deletebackup import DeleteBackupLogic


class DeleteBackupDelegate(ControllerDelegate):
    last_error = None

    def __init__(self, controller=None, parent=None, callback=None):
        super().__init__(controller, parent, title="Deleting backup...")
        self.callback = callback

    def success(self):
        super().success()
        if callable(self.callback):
            self.callback(self.controller.backup)

    def show_success_message(self):
        print('successfully deleted archive')


class DeleteBackupController():
    def __init__(self, backup, parent=None, callback=None):
        self.logic = DeleteBackupLogic()
        self.parent = parent
        self.backup = backup

        # Check with the user
        dialog = self.parent.get_message_box(
            icon=QMessageBox.Critical, title=self.parent.tr("Delete Backup"),
            message=self.parent.tr("Do you really want to delete this archive?"),
            message_detail=self.backup.name, standard_buttons=(QMessageBox.Ok | QMessageBox.Cancel))

        result = dialog.exec_()

        if result == QMessageBox.Ok:
            self.delete_backup(callback)

    def delete_backup(self, callback):
        delegate = DeleteBackupDelegate(controller=self, parent=self.parent, callback=callback)
        try:
            self.logic.delete_local_backup(backup=self.backup, delegate=delegate)
        except NoPassphraseError:
            delegate.close_dialog()
            self.parent.show_error_message_box(
                message='Password required',
                message_detail='Backup cannot be deleted without repository password')
