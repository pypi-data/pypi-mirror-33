import enum

from PyQt4.QtCore import Qt
from unittest.mock import MagicMock, ANY, patch

from qborg.ui.pyqt4.guis.initrepo import InitRepoGui


class BorgEncryptionMode(enum.Enum):
    NONE = 'none'
    REPOKEY = 'repokey'
    KEYFILE = 'keyfile'

    @property
    def requires_password(self):
        # all methods except for NONE require a password
        return (self != self.NONE)


backing_stores = ['file']


@patch('qborg.ui.pyqt4.controllers.initrepocontroller.InitRepoController', autospec=True)
def test_init_repo_accept_model(controller_mock, qtbot):
    controller_mock.check_valid_new_repo_name.return_value = (True, '')

    test_name = 'testrepo'
    test_path = '/tmp/repo'
    test_pwd = 'password'

    widget = InitRepoGui(backing_stores, BorgEncryptionMode, listener=controller_mock)
    widget.show()

    # Set index in combobox and get string value for later checks
    widget.cb_backing_store.setCurrentIndex(0)
    test_store = widget.cb_backing_store.currentText()
    widget.cb_encryption_mode.setCurrentIndex(1)
    test_crypto = widget.cb_encryption_mode.currentText()

    qtbot.addWidget(widget)

    qtbot.keyClicks(widget.txt_repo_name, test_name)
    qtbot.keyClicks(widget.txt_repo_path, test_path)
    qtbot.keyClicks(widget.txt_password, test_pwd)
    qtbot.keyClicks(widget.txt_password_check, test_pwd)
    ok_widget = widget.bb_cancel_ok.button(widget.bb_cancel_ok.Ok)
    qtbot.mouseClick(ok_widget, Qt.LeftButton)

    controller_mock.btn_accept_click.assert_called_once_with(ANY)
    assert controller_mock.btn_accept_click.call_args[0][0].name == test_name
    assert controller_mock.btn_accept_click.call_args[0][0].backing_store.protocol == test_store
    assert controller_mock.btn_accept_click.call_args[0][0].path == test_path
    assert controller_mock.btn_accept_click.call_args[0][0].name == test_name
    assert controller_mock.btn_accept_click.call_args[0][0].password == test_pwd
    assert controller_mock.btn_accept_click.call_args[0][0].encryption_mode == test_crypto


@patch('qborg.ui.pyqt4.controllers.initrepocontroller.InitRepoController', autospec=True)
def test_init_repo_no_name(controller_mock, qtbot):
    controller_mock.check_valid_new_repo_name.return_value = (False, 'Empty name')
    widget = InitRepoGui(backing_stores, BorgEncryptionMode, listener=controller_mock)
    widget.show_input_error_message_box = MagicMock()
    widget.show()

    # Set index in combobox and get string value for later checks
    widget.cb_encryption_mode.setCurrentIndex(1)

    qtbot.addWidget(widget)

    test_path = 'testpath'
    test_pwd = 'password'
    qtbot.keyClicks(widget.txt_repo_path, test_path)
    qtbot.keyClicks(widget.txt_password, test_pwd)
    qtbot.keyClicks(widget.txt_password_check, test_pwd)
    ok_widget = widget.bb_cancel_ok.button(widget.bb_cancel_ok.Ok)
    qtbot.mouseClick(ok_widget, Qt.LeftButton)

    assert not controller_mock.btn_accept_click.called
    widget.show_input_error_message_box.assert_called_once_with(
        message='Input error',
        message_detail='The repository name is invalid:\nEmpty name')


def test_init_repo_password_visible():
    widget = InitRepoGui(backing_stores, BorgEncryptionMode, None)
    widget.show()
    # Chose crypto method that needs password check
    widget.cb_encryption_mode.setCurrentIndex(1)

    assert widget.txt_password.isVisible()
    assert widget.txt_password_check.isVisible()


def test_init_repo_password_invisible():
    widget = InitRepoGui(backing_stores, BorgEncryptionMode, None)
    widget.show()
    # Chose crypto method that needs password check
    widget.cb_encryption_mode.setCurrentIndex(0)

    assert not widget.txt_password.isVisible()
    assert not widget.txt_password_check.isVisible()


@patch('qborg.ui.pyqt4.controllers.initrepocontroller.InitRepoController', autospec=True)
def test_init_repo_password_wrong(controller_mock, qtbot):
    controller_mock.check_valid_new_repo_name.return_value = (True, '')
    widget = InitRepoGui(backing_stores, BorgEncryptionMode, listener=controller_mock)
    widget.show_input_error_message_box = MagicMock()
    widget.show()

    # Chose crypto method that needs password check
    widget.cb_encryption_mode.setCurrentIndex(1)

    qtbot.addWidget(widget)

    test_pwd = 'password'
    qtbot.keyClicks(widget.txt_repo_path, 'testpath')
    qtbot.keyClicks(widget.txt_password, test_pwd)
    qtbot.keyClicks(widget.txt_password_check, 'wrong')
    ok_widget = widget.bb_cancel_ok.button(widget.bb_cancel_ok.Ok)
    qtbot.mouseClick(ok_widget, Qt.LeftButton)

    assert not controller_mock.btn_accept_click.called
    widget.show_input_error_message_box.assert_called_once_with(
        message='Input error',
        message_detail='Passwords do not match')
