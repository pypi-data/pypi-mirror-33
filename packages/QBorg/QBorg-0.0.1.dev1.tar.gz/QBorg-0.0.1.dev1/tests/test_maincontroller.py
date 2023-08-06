import enum

from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, ANY

from qborg.adapters.backingstore.file import FileBackingStoreAdapter
from qborg.entities.backup import Backup
from qborg.entities.config import RepositorySet
from qborg.entities.location import Location
from qborg.entities.repository import Repository
from qborg.ui.pyqt4.controllers.maincontroller import MainController, RepositoryNode
from qborg.ui.pyqt4.guis.main import RepositoryTreeModel


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'

    @property
    def requires_password(self):
        return False


class MainControllerTest(TestCase):
    def setUp(self):
        self.repositories = RepositorySet([
            Repository('repo1',
                       Location(FileBackingStoreAdapter(), '/tmp/testrepo1'),
                       BorgMockEncryptionMode.NONE),
            Repository('repo2',
                       Location(FileBackingStoreAdapter(), '/tmp/testrepo2'),
                       BorgMockEncryptionMode.NONE)
        ])

        with patch('qborg.ui.pyqt4.guis.main.RepositoryNode.list_repo') as list_mock:
            self.selected_node = RepositoryNode(repo=self.repositories['repo1'])
            self.selected_node.list_repo = list_mock

        with patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui'):
            self.mc = MainController()
            self.mc.context_object = self.repositories['repo1']

    @patch('qborg.ui.pyqt4.controllers.maincontroller.InitRepoController', autospec=True)
    def test_start_init(self, init_mock):
        self.mc.start_process_init()
        init_mock.assert_called_once_with(callback=ANY, parent=self.mc.main)

    @patch('qborg.ui.pyqt4.controllers.maincontroller.CreateBackupController', autospec=True)
    def test_start_create(self, create_mock):
        self.mc.start_process_create_backup()
        selected_repository = self.mc.context_object
        create_mock.assert_called_once_with(selected_repository, callback=ANY, parent=self.mc.main)

    @patch('qborg.ui.pyqt4.controllers.maincontroller.DeleteBackupController', autospec=True)
    def test_start_delete(self, controller_mock):
        backup = Backup('testbackup', datetime(2018, 1, 1), self.repositories['repo1'])
        self.mc.context_object = backup
        self.mc.start_process_delete_backup()

        controller_mock.assert_called_once_with(backup, parent=self.mc.main,
                                                callback=self.mc.tree_remove_node_for_entity)

    @patch('qborg.ui.pyqt4.controllers.maincontroller.QMessageBox', autospec=True)
    def test_show_about(self, box_mock):
        self.mc.show_about_dialog()
        box_mock.about.assert_called_once_with(self.mc.main, 'About QBorg', ANY)

    @patch('qborg.ui.pyqt4.controllers.maincontroller.QModelIndex', autospec=True)
    @patch('qborg.ui.pyqt4.controllers.maincontroller.QModelIndex', autospec=True)
    def test_select(self, index_new_mock, index_old_mock):
        index_new_mock.internalPointer.return_value = self.selected_node

        self.mc.tree_navigator_current_row_changed(index_new_mock, index_old_mock)
        self.assertTrue(self.mc.main.btn_repository_create.hide.called)
        self.assertTrue(self.mc.main.btn_repository_delete.show.called)
        self.assertTrue(self.mc.main.btn_repository_rename.show.called)
        self.assertTrue(self.mc.main.btn_backup_create.show.called)
        self.assertTrue(self.mc.main.btn_backup_delete.hide.called)
        self.assertTrue(self.mc.main.btn_backup_restore.hide.called)
        self.assertTrue(self.mc.main.btn_job_create.show.called)
        self.assertTrue(self.mc.main.btn_job_delete.hide.called)
        self.assertTrue(self.mc.main.btn_job_run.hide.called)

    @patch('qborg.ui.pyqt4.controllers.maincontroller.QModelIndex', autospec=True)
    @patch('qborg.ui.pyqt4.guis.main.QBorgNode', autospec=True)
    @patch('qborg.ui.pyqt4.controllers.maincontroller.MainController.get_tree_model')
    def test_show(self, get_tree_model_mock, root_node_mock, index_mock):
        get_tree_model_mock.return_value = RepositoryTreeModel(self.repositories)
        self.mc.main.tree_navigator.model().index.return_value = index_mock

        self.mc.show()

        root_node_mock.assert_called_once_with(self.repositories)
        self.assertTrue(self.mc.main.show.called)
        self.assertTrue(self.mc.main.tree_navigator.expandAll.called)
        self.mc.main.tree_navigator.selectionModel().currentRowChanged.connect.assert_called_once_with(
            self.mc.tree_navigator_current_row_changed)

        self.assertTrue(index_mock.called)
        self.mc.main.tree_navigator.model().index.assert_called_once_with(0, 0, index_mock.return_value)
        self.mc.main.tree_navigator.setCurrentIndex.assert_called_once_with(index_mock)
