import enum

from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from qborg.entities.backup import Backup
from qborg.entities.repository import Repository
from qborg.ui.pyqt4.controllers.extractbackupcontroller import ExtractBackupController
from qborg.ui.pyqt4.guis.extractbackup import ExtractBackupViewModel


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'
    REPOKEY = 'repokey'

    @property
    def requires_password(self):
        return (self != self.NONE)


class ExtractBackupTest(TestCase):

    def setUp(self):
        self.repository = Repository("test", "/test", BorgMockEncryptionMode.NONE)
        self.backup = Backup("name", datetime(2018, 1, 1), self.repository)

        with patch('qborg.ui.pyqt4.controllers.extractbackupcontroller.ExtractBackupLogic'), \
                patch('qborg.ui.pyqt4.controllers.extractbackupcontroller.ExtractBackupGui') as gui_mock, \
                patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui') as parent_mock:
            self.controller = ExtractBackupController(self.backup, parent=parent_mock)
            self.gui = gui_mock

    @patch('qborg.ui.pyqt4.controllers.extractbackupcontroller.ExtractBackupLogic')
    @patch('qborg.ui.pyqt4.controllers.extractbackupcontroller.ExtractBackupGui')
    @patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui')
    def test_constructor(self, maingui_mock, repogui_mock, logic_mock):
        c = ExtractBackupController(self.backup, parent=maingui_mock)

        logic_mock.assert_called_once_with()
        assert repogui_mock.called
        self.assertEqual(maingui_mock, c.parent)

    @patch('qborg.ui.pyqt4.controllers.extractbackupcontroller.ExtractBackupDelegate')
    def test_btn_accept(self, delegate_mock):
        model = ExtractBackupViewModel()
        model.path = "/tmp/extract"

        self.controller.btn_accept_click(model)
        delegate_mock.assert_called_once_with(
            controller=self.controller, parent=self.controller.widget)
        self.controller.logic.extract_local_backup.assert_called_once_with(
            self.controller.backup, model.path, delegate=delegate_mock())
