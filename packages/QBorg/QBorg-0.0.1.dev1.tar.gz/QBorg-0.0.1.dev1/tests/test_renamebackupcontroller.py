import enum
from unittest import TestCase
from unittest.mock import patch

from qborg.entities.backup import Backup
from qborg.entities.repository import Repository
from qborg.ui.pyqt4.controllers.renamebackupcontroller import RenameBackupController, RenameBackupDelegate


class ThreadProxyHelper:
    def __init__(self, _self, _func, *args, **kwargs):
        self._self = _self
        self._func = _func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._func(self._self, *self._args, **self._kwargs)


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'


class RenameBackupControllerTest(TestCase):
    def setUp(self):
        self.repository = Repository("test", "/test", BorgMockEncryptionMode.NONE)
        self.backup = Backup("name", "1234", self.repository)

        with patch('qborg.ui.pyqt4.controllers.renamebackupcontroller.RenameBackupLogic'), \
                patch('qborg.ui.pyqt4.controllers.renamebackupcontroller.RenameBackupDelegate'), \
                patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui') as parent_mock:
            parent_mock.get_input_dialog.return_value = ("Test", True)
            self.ic = RenameBackupController(self.backup, parent=parent_mock)

    @patch('qborg.ui.pyqt4.controllers.renamebackupcontroller.RenameBackupDelegate')
    @patch('qborg.ui.pyqt4.controllers.renamebackupcontroller.RenameBackupLogic')
    @patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui')
    def test_constructor(self, maingui_mock, logic_mock, delegate_mock):
        maingui_mock.get_input_dialog.return_value = ("Test", True)
        backup = Backup("name", "1234", self.repository)
        c = RenameBackupController(backup, parent=maingui_mock)
        logic_mock.assert_called_once_with()
        assert c.parent == maingui_mock
        maingui_mock.get_input_dialog.assert_called_once_with("Rename Backup", "New Backup name", backup.name)


class RenameBackupDelegateTest(TestCase):

    @patch('qborg.ui.pyqt4.controllers.renamebackupcontroller.ControllerDelegate.__init__')
    def test_constructor(self, init_mock):
        RenameBackupDelegate("controller", "parent")
        init_mock.assert_called_once_with("controller", "parent", title='Renaming Backup...')
