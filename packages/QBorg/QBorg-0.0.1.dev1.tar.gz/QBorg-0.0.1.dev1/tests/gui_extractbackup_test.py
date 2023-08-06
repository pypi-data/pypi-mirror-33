from unittest.mock import patch, ANY

from PyQt4.QtCore import Qt

from qborg.ui.pyqt4.guis.extractbackup import ExtractBackupGui


@patch('qborg.ui.pyqt4.controllers.extractbackupcontroller.ExtractBackupController', autospec=True)
def test_init_repo_accept_model(controller_mock, qtbot):
    widget = ExtractBackupGui(listener=controller_mock)
    widget.show()

    qtbot.addWidget(widget)

    test_path = 'testpath'

    qtbot.keyClicks(widget.txt_extract_path, test_path)
    ok_widget = widget.bb_cancel_ok.button(widget.bb_cancel_ok.Ok)
    qtbot.mouseClick(ok_widget, Qt.LeftButton)

    controller_mock.btn_accept_click.assert_called_once_with(ANY)
    assert controller_mock.btn_accept_click.call_args[0][0].path == test_path
