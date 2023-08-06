from PyQt4.QtGui import QMessageBox

from qborg.adapters.backup import NoPassphraseError
from qborg.logic.controllerdelegate import ControllerDelegate
from qborg.logic.deleterepo import DeleteRepoLogic


class DeleteRepoDelegate(ControllerDelegate):
    last_error = None

    def __init__(self, controller=None, parent=None, callback=None):
        super().__init__(controller, parent, title=parent.tr("Deleting repository..."))
        self.callback = callback

    def success(self):
        super().success()
        if callable(self.callback):
            self.callback(self.controller.repository)

    def show_success_message(self):
        self.controller.parent.show_delete_repository_success()

    def show_error_message(self, error_message):
        self.parent.show_delete_repository_error(detail=self.last_error)


class DeleteRepoController():
    def __init__(self, repository, parent):
        self.logic = DeleteRepoLogic()
        self.repository = repository
        self.parent = parent

    def delete_repository(self, callback=None):
        btntype = self.parent.show_prompt_message_box(
            self.parent.tr("Delete Repository"),
            self.parent.tr(
                "You requested to completely DELETE the repository "
                "*including* all archives it contain. Do you want to "
                "continue?"))

        if btntype == QMessageBox.Yes:
            delegate = DeleteRepoDelegate(controller=self, callback=callback, parent=self.parent)
            try:
                self.logic.delete_repository(self.repository, delegate=delegate)
            except NoPassphraseError:
                delegate.close_dialog()
                self.parent.show_error_message_box(
                    message='Password required',
                    message_detail='Repository cannot be deleted without repository password')
