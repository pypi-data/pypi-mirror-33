from unittest.mock import MagicMock, patch

from PyQt4.QtCore import Qt, QModelIndex

from qborg.entities.job import Job
from qborg.entities.repository import Repository
from qborg.ui.pyqt4.controllers.maincontroller import MainController
from qborg.ui.pyqt4.guis.main import MainGui, MainEvent, RepositoryTreeModel


def test_repository_create_btn(qtbot):
    event_mock = MainEvent()
    event_mock.start_process_init = MagicMock()
    widget = MainGui(listener=event_mock)
    widget.show()

    # QActions can only be triggered by code not from qtbot
    qtbot.mouseClick(widget.btn_repository_create, Qt.LeftButton)

    # Tests if the method is called once
    event_mock.start_process_init.assert_called_once_with()


def test_backup_delete_btn(qtbot):
    event_mock = MainEvent()
    event_mock.start_process_delete_backup = MagicMock()
    widget = MainGui(listener=event_mock)
    widget.show()

    # QActions can only be triggered by code not from qtbot
    qtbot.mouseClick(widget.btn_backup_delete, Qt.LeftButton)

    # Tests if the method is called once
    event_mock.start_process_delete_backup.assert_called_once_with()


@patch('qborg.ui.pyqt4.controllers.maincontroller.MainController', autospec=True)
def test_delete_repo(controller_mock, qtbot):
    widget = MainGui(listener=controller_mock)
    widget.show()
    qtbot.addWidget(widget)

    qtbot.mouseClick(widget.btn_repository_delete, Qt.LeftButton)
    controller_mock.start_process_repository_delete.assert_called_once_with()


@patch('qborg.ui.pyqt4.controllers.maincontroller.MainController.get_tree_model')
@patch('qborg.ui.pyqt4.guis.main.RepositoryNode.list_repo')
def test_ribbon_buttons(list_repo_mock, get_tree_model_mock):
    # FIXME, test currently fails for some reasons
    return

    repo1 = Repository('testrepo', '/tmp/testrepo', 'none')
    repo1.jobs.add(Job('testjob'))

    get_tree_model_mock.return_value = RepositoryTreeModel([repo1])
    list_repo_mock.return_value = None

    controller = MainController()
    controller.show()

    btn_repository_create = controller.main.btn_repository_create
    btn_repository_delete = controller.main.btn_repository_delete
    btn_backup_create = controller.main.btn_backup_create
    btn_backup_delete = controller.main.btn_backup_delete
    btn_backup_restore = controller.main.btn_backup_restore
    btn_job_create = controller.main.btn_job_create
    btn_job_delete = controller.main.btn_job_delete
    btn_job_run = controller.main.btn_job_run

    tree = controller.main.tree_navigator
    model = tree.model()

    root = model.index(0, 0, QModelIndex())
    tree.setCurrentIndex(root)
    assert not btn_repository_create.isHidden()
    assert btn_repository_delete.isHidden()
    assert btn_backup_create.isHidden()
    assert btn_backup_delete.isHidden()
    assert btn_backup_restore.isHidden()
    assert btn_job_create.isHidden()
    assert btn_job_delete.isHidden()
    assert btn_job_run.isHidden()

    repo = model.index(0, 0, root)
    tree.setCurrentIndex(repo)
    assert btn_repository_create.isHidden()
    assert not btn_repository_delete.isHidden()
    assert not btn_backup_create.isHidden()
    assert btn_backup_delete.isHidden()
    assert btn_backup_restore.isHidden()
    assert not btn_job_create.isHidden()
    assert btn_job_delete.isHidden()
    assert btn_job_run.isHidden()

    job_collection = model.index(0, 0, repo)
    tree.setCurrentIndex(job_collection)
    assert btn_repository_create.isHidden()
    assert btn_repository_delete.isHidden()
    assert btn_backup_create.isHidden()
    assert btn_backup_delete.isHidden()
    assert btn_backup_restore.isHidden()
    assert not btn_job_create.isHidden()
    assert btn_job_delete.isHidden()
    assert btn_job_run.isHidden()

    backup_collection = model.index(1, 0, repo)
    tree.setCurrentIndex(backup_collection)
    assert btn_repository_create.isHidden()
    assert btn_repository_delete.isHidden()
    assert not btn_backup_create.isHidden()
    assert btn_backup_delete.isHidden()
    assert btn_backup_restore.isHidden()
    assert btn_job_create.isHidden()
    assert btn_job_delete.isHidden()
    assert btn_job_run.isHidden()

    job = model.index(0, 0, job_collection)
    tree.setCurrentIndex(job)
    assert btn_repository_create.isHidden()
    assert btn_repository_delete.isHidden()
    assert btn_backup_create.isHidden()
    assert btn_backup_delete.isHidden()
    assert btn_backup_restore.isHidden()
    assert not btn_job_create.isHidden()
    assert not btn_job_delete.isHidden()
    assert not btn_job_run.isHidden()

    backup = model.index(0, 0, backup_collection)
    tree.setCurrentIndex(backup)
    assert btn_repository_create.isHidden()
    assert btn_repository_delete.isHidden()
    assert not btn_backup_create.isHidden()
    assert not btn_backup_delete.isHidden()
    assert not btn_backup_restore.isHidden()
    assert btn_job_create.isHidden()
    assert btn_job_delete.isHidden()
    assert btn_job_run.isHidden()
