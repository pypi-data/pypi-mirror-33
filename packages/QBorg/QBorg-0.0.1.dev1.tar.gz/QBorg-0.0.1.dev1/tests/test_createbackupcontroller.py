import enum
import imp
from unittest import TestCase
from unittest.mock import patch, ANY

import qborg.ui.pyqt4.controllers.createbackupcontroller
from qborg.adapters.backingstore.file import FileBackingStoreAdapter
from qborg.entities.location import Location
from qborg.entities.repository import Repository
from qborg.ui.pyqt4.controllers.createbackupcontroller import CreateBackupController, CreateBackupDelegate
from qborg.ui.pyqt4.guis.createbackup import CreateBackupGuiModel


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'


class BorgMockCompressionMode(enum.Enum):
    NONE = 'none'


class CreateBackupControllerTest(TestCase):
    def setUp(self):
        self.encryption_modes = BorgMockEncryptionMode
        self.compression_modes = BorgMockCompressionMode

        def kill_patches():
            patch.stopall()
            imp.reload(qborg.ui.pyqt4.controllers.createbackupcontroller)

        self.addCleanup(kill_patches)

        # Patch the pyqtRunOnGuiThread decorator (with a pass-through)
        patch('qborg.ui.pyqt4.pyqtRunOnGuiThread', lambda x: x).start()
        # Reload the module-to-test which applies the patched decorator
        imp.reload(qborg.ui.pyqt4.controllers.createbackupcontroller)

        with patch('qborg.ui.pyqt4.controllers.createbackupcontroller.CreateBackupLogic'), \
                patch('qborg.ui.pyqt4.controllers.createbackupcontroller.CreateBackupGui'), \
                patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui') as parent_mock:
            self.ic = CreateBackupController("selected_test_Repository", parent=parent_mock)

    @patch('qborg.ui.pyqt4.controllers.createbackupcontroller.CreateBackupLogic')
    @patch('qborg.ui.pyqt4.controllers.createbackupcontroller.CreateBackupGui')
    @patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui')
    def test_constructor(self, maingui_mock, backupgui_mock, logic_mock):
        selected_repository_name = "selected_test_repository"
        c = CreateBackupController(selected_repository_name, parent=maingui_mock)
        logic_mock.return_value.get_supported_compression_modes.assert_called_once_with()
        logic_mock.return_value.get_repositories.assert_called_once_with()
        assert c.parent == maingui_mock
        backupgui_mock.assert_called_once_with(
            selected_repository_name, c.repositories, c.compression_modes,
            controller=c)

    @patch('qborg.ui.pyqt4.controllers.createbackupcontroller.CreateBackupDelegate')
    def test_btn_accept(self, delegate_mock):
        repo_name = 'testrepo'
        location = Location(FileBackingStoreAdapter(), '/tmp/repos/%s' % repo_name)
        model = CreateBackupGuiModel()

        model.repository = Repository(repo_name, location, self.encryption_modes.NONE)
        model.compression_method = self.compression_modes.NONE
        model.archive_name = 'testbackup'
        model.include_paths = ['/tmp']

        self.ic.btn_accept_click(model)
        delegate_mock.assert_called_once_with(self.ic, self.ic.widget, callback=ANY)
        self.ic.logic.create_backup.assert_called_once_with(
            delegate=delegate_mock.return_value, **vars(model))


class CreateBackupDelegateTest(TestCase):

    @patch('qborg.ui.pyqt4.guis.main.MainGui')
    @patch('qborg.ui.pyqt4.controllers.createbackupcontroller.CreateBackupController')
    def test_constructor(self, controller_mock, maingui_mock):
        parent = maingui_mock()
        controller = controller_mock()

        with patch('qborg.ui.pyqt4.controllers.createbackupcontroller.ControllerDelegate.__init__') \
                as controller_delegate_mock:
            CreateBackupDelegate(controller=controller, parent=parent)

            controller_delegate_mock.assert_called_once_with(controller, parent, title="Creating Backup...")
