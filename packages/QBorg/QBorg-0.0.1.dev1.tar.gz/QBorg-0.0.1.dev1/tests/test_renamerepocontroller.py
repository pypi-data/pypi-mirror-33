from unittest import TestCase
from unittest.mock import patch
from qborg.entities.repository import Repository
from qborg.entities.config import RepositorySet
import qborg.ui.pyqt4.controllers.renamerepocontroller


class RenameRepoControllerTest(TestCase):

    def setUp(self):
        self.repository = Repository('oldname', 'location', 'none')
        with patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui') as parent_mock:
            self.cut = qborg.ui.pyqt4.controllers.renamerepocontroller.RenameRepoController(self.repository,
                                                                                            parent=parent_mock)

    @patch('qborg.ui.pyqt4.controllers.renamerepocontroller.RenameRepoController.do_update')
    def test_cancel(self, update_mock):
        self.cut.parent.get_input_dialog.return_value = ('', False)
        self.cut.change_name()
        self.assertFalse(update_mock.called)

    @patch('qborg.ui.pyqt4.controllers.renamerepocontroller.RenameRepoController.do_update', autospec=True)
    def test_same_name(self, update_mock):
        self.cut.parent.get_input_dialog.return_value = ('oldname', True)
        self.cut.change_name()
        self.assertFalse(update_mock.called)

    @patch('qborg.ui.pyqt4.controllers.renamerepocontroller.RenameRepoController.do_update', autospec=True)
    def test_name_empty(self, update_mock):
        self.cut.parent.get_input_dialog.return_value = ('', True)
        self.cut.change_name()
        self.assertFalse(update_mock.called)
        self.assertTrue(self.cut.parent.show_error_message_box.called)

    @patch('qborg.ui.pyqt4.controllers.renamerepocontroller.RenameRepoController.do_update', autospec=True)
    @patch('qborg.ui.pyqt4.controllers.renamerepocontroller.QBorgApp', autospec=True)
    def test_name_exists(self, app_mock, update_mock):
        self.cut.parent.get_input_dialog.return_value = ('newname', True)
        app_mock.instance.return_value.config_manager.config.repositories = RepositorySet(
            [Repository('newname', 'loc', 'none')])
        self.cut.change_name()
        self.assertFalse(update_mock.called)
        self.assertTrue(self.cut.parent.show_error_message_box.called)

    @patch('qborg.ui.pyqt4.controllers.renamerepocontroller.RenameRepoController.do_update', autospec=True)
    @patch('qborg.ui.pyqt4.controllers.renamerepocontroller.QBorgApp', autospec=True)
    def test_name_okay(self, app_mock, update_mock):
        self.cut.parent.get_input_dialog.return_value = ('newname', True)
        app_mock.instance.return_value.config_manager.config.repositories = RepositorySet(
            [Repository('somename', 'loc', 'none')])
        self.cut.change_name()
        update_mock.assert_called_once_with(self.cut, 'newname', app_mock.instance.return_value.config_manager)
        self.assertFalse(self.cut.parent.show_error_message_box.called)

    @patch('qborg.ui.pyqt4.guis.main.RepositoryTreeModel')
    @patch('qborg.ui.pyqt4.controllers.maincontroller.RepositoryNode', autospec=True)
    @patch('qborg.logic.config_file_manager.ConfigFileManager', autospec=True)
    def test_do_update(self, configmanagermock, nodemock, treemock):

        configmanagermock.config.repositories = RepositorySet([Repository('oldname', 'loc', 'none')])
        self.cut.parent.listener.get_tree_model.return_value = treemock
        treemock.find_node_by_entity.return_value = nodemock

        self.cut.do_update('newname', configmanagermock)

        try:
            if configmanagermock.config.repositories['oldname']:
                self.fail('oldname should not exist anymore')
        except KeyError:
            pass  # OK
        self.assertTrue(configmanagermock.config.repositories['newname'])
        self.assertTrue(configmanagermock.save_config.called)
        self.assertEqual('newname', self.cut.repository.name)

        self.cut.parent.listener.get_tree_model.assert_called_once_with()
        treemock.find_node_by_entity.assert_called_once_with(qborg.ui.pyqt4.controllers.maincontroller.RepositoryNode,
                                                             self.repository)
        treemock.layoutAboutToBeChanged.emit.assert_called_once_with()
        nodemock.updateData.assert_called_once_with(0, 'newname')
        treemock.layoutChanged.emit.assert_called_once_with()
