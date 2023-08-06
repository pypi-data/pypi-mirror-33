from qborg.logic.controllerdelegate import ControllerDelegate
from qborg.logic.renamebackup import RenameBackupLogic


class RenameBackupDelegate(ControllerDelegate):

    def __init__(self, controller=None, parent=None, callback=None):
        super().__init__(controller, parent, title='Renaming Backup...')
        self.callback = callback

    def success(self):
        super().success()
        if callable(self.callback):
            self.callback()

    def show_success_message(self):
        self.controller.parent.show_rename_backup_success()

    def show_error_message(self, error_message):
        self.controller.parent.show_rename_backup_error(detail=error_message)


class RenameBackupController():
    def __init__(self, backup_entity, callback=None, parent=None):
        self.logic = RenameBackupLogic()
        self.backup_entity = backup_entity
        self.parent = parent
        self.callback = callback
        old_name = backup_entity.name

        archive_name, ok = self.parent.get_input_dialog("Rename Backup", "New Backup name", backup_entity.name)
        if ok and not old_name == archive_name:
            def callback():
                if callable(self.callback):
                    self.backup_entity.name = archive_name
                    self.callback(self.backup_entity)

            delegate = RenameBackupDelegate(self, self.parent, callback=callback)

            try:
                self.logic.rename_local_backup(backup_entity, archive_name, delegate=delegate)
            except Exception as e:
                delegate.close_dialog()
                self.parent.show_error_message_box(
                    message='An error occurred when renaming archive %s' % backup_entity.name,
                    message_detail='%s' % e)
