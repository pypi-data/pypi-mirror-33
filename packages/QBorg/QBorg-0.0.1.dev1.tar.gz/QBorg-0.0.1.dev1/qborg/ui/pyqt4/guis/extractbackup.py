import os

from PyQt4 import QtGui

from qborg.ui.pyqt4.guis.qborggui import QBorgGui


class ExtractBackupGui(QtGui.QWidget, QBorgGui):
    def __init__(self, listener=None):
        super(ExtractBackupGui, self).__init__()
        self.show_ui('extract_backup.ui')

        self.listener = listener

        self.btn_file_explorer.clicked.connect(self.btn_open_browser)
        self.bb_cancel_ok.accepted.connect(self.accept)
        self.bb_cancel_ok.rejected.connect(self.close)

    def btn_open_browser(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
        path = dialog.getExistingDirectory(self, self.tr('Choose Repository'),
                                           os.path.expanduser('~'))
        self.txt_extract_path.setText(path)

    def accept(self):
        if self.check_input():
            model = ExtractBackupViewModel()
            model.path = self.txt_extract_path.text()

            if self.listener:
                self.listener.btn_accept_click(model)

    def check_input(self):
        message = None

        if not self.txt_extract_path.text():
            message = self.tr("Please choose a path to restore the backup")

        if message:
            self.show_input_error_message_box(message=self.tr("Input error"), message_detail=message)
            return False

        return True

    def show_success(self, detail=None):
        self.show_success_message_box(self.tr("Successfully restored backup"), detail, function=self.close)

    def show_error(self, detail=None):
        self.show_error_message_box(self.tr("Error restoring backup"), detail)


class ExtractBackupViewModel:
    def __init__(self):
        self.path = None
