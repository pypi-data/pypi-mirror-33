import enum

from PyQt4.QtCore import Qt
from unittest.mock import patch

from qborg.entities.config import RepositorySet
from qborg.entities.repository import Repository
from qborg.ui.pyqt4.guis.createbackup import CreateBackupGui


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'


class BorgMockCompressionMode(enum.Enum):
    NONE = 'none'


repositories = RepositorySet([
    Repository("repo1", "/tmp/repo1", BorgMockEncryptionMode.NONE),
    Repository("repo2", "/tmp/repo2", BorgMockEncryptionMode.NONE)
])


@patch('qborg.ui.pyqt4.controllers.createbackupcontroller.CreateBackupController', autospec=True)
def test_create_backup_accept_model(controller_mock, qtbot):
    controller_mock.get_supported_compression_modes.return_value = BorgMockCompressionMode
    controller_mock.check_model.return_value = (True, '')

    test_files_and_dirs = ["Test_files_and_dir"]
    widget = CreateBackupGui(repositories["repo1"], repositories,
                             BorgMockCompressionMode, controller=controller_mock)
    widget.show()

    # Set index in combobox and get string value for later checks
    widget.cb_repository.setCurrentIndex(0)
    widget.cb_jobs.setCurrentIndex(0)
    widget.cb_compression_mode.setCurrentIndex(0)

    test_backup_name = 'testbackupname'
    test_repository = repositories[widget.cb_repository.itemText(0)]
    test_compression = BorgMockCompressionMode(widget.cb_compression_mode.currentText())

    # Add includes to GUI
    for item in test_files_and_dirs:
        widget.listWidget_dirs_and_files.addItem(item)
    assert widget.listWidget_dirs_and_files.count() == len(test_files_and_dirs)
    # test_exclude_files_and_dirs = ['*.swp', '*~']

    qtbot.addWidget(widget)
    qtbot.keyClicks(widget.txt_archive_name, test_backup_name)

    # Click "OK" and check values passed to btn_accept_click
    ok_widget = widget.bb_cancel_ok.button(widget.bb_cancel_ok.Ok)
    qtbot.mouseClick(ok_widget, Qt.LeftButton)

    # Check the call to the CreateBackupController
    btn_accept_click_args = controller_mock.btn_accept_click.call_args[0][0]
    assert btn_accept_click_args.repository == test_repository
    assert btn_accept_click_args.archive_name == test_backup_name
    assert btn_accept_click_args.compression_mode == test_compression
    assert btn_accept_click_args.include_paths == test_files_and_dirs
    # FIXME: Add excludes support
    # assert btn_accept_click_args.exclude_paths == test_exclude_files_and_dirs
