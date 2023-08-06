from qborg.logic.controllerdelegate import ControllerDelegate
from qborg.logic.extractbackup import ExtractBackupLogic
from qborg.ui.pyqt4.guis.extractbackup import ExtractBackupGui


class ExtractBackupDelegate(ControllerDelegate):
    last_error = None

    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent, title="Extracting backup...")


class ExtractBackupController():
    def __init__(self, backup, parent=None):
        self.parent = parent
        self.backup = backup
        self.widget = ExtractBackupGui(self)
        self.logic = ExtractBackupLogic()

    def btn_accept_click(self, model):
        delegate = ExtractBackupDelegate(controller=self, parent=self.widget)
        self.logic.extract_local_backup(self.backup, model.path, delegate=delegate)
