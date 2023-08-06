import enum

from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, ANY

from PyQt4.QtGui import QMessageBox

from qborg.entities.backup import Backup
from qborg.entities.repository import Repository
from qborg.ui.pyqt4.controllers.deletebackupcontroller import DeleteBackupController


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'


class DeleteBackupTest(TestCase):
    def setUp(self):
        self.repository = Repository("test", "/test", BorgMockEncryptionMode.NONE)
        self.backup = Backup("name", datetime(2018, 1, 1), self.repository)

    @patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui')
    def test_constructor(self, parent_mock):
        with patch('qborg.ui.pyqt4.controllers.deletebackupcontroller.DeleteBackupLogic'), \
                patch.object(parent_mock, 'tr', lambda x: x):
            c = DeleteBackupController(self.backup, parent=parent_mock)

        assert c.parent == parent_mock

        parent_mock.get_message_box.assert_called_once_with(
            icon=QMessageBox.Critical, title=ANY, message=ANY,
            message_detail=self.backup.name, standard_buttons=ANY)

    @patch('qborg.ui.pyqt4.controllers.deletebackupcontroller.DeleteBackupDelegate')
    def test_delete_backup(self, delegate_mock):
        with patch('qborg.ui.pyqt4.controllers.deletebackupcontroller.DeleteBackupLogic'), \
             patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui') as parent_mock:
            controller = DeleteBackupController(self.backup, parent=parent_mock)

        # Confirm dialog
        controller.delete_backup(callback=None)

        # Assert that the delegate has been instantiated
        delegate_mock.assert_called_once_with(controller=controller, parent=controller.parent, callback=None)

        # Assert that the logic has been called
        controller.logic.delete_local_backup.assert_called_once_with(backup=self.backup, delegate=ANY)
