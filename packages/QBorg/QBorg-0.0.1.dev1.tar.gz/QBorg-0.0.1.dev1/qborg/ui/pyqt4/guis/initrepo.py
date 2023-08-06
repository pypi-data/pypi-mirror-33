import os

from PyQt4 import QtGui

from qborg.logic.factories import BackingStoreAdapterFactory
from qborg.ui.pyqt4.guis.qborggui import QBorgGui


class InitRepoGui(QtGui.QWidget, QBorgGui):
    def __init__(self, backing_stores, encryption_modes, listener=None):
        super().__init__()
        self.show_ui('initrepo.ui')

        self.listener = listener
        self.backing_stores = backing_stores
        self.encryption_modes = encryption_modes

        self.btn_repo_path_browse.clicked.connect(self.btn_open_browser)
        self.bb_cancel_ok.accepted.connect(self.accept)
        self.bb_cancel_ok.rejected.connect(self.close)
        self.init_backing_stores_combobox()
        self.init_encryption_modes_combobox()

    def init_backing_stores_combobox(self):
        cb = self.cb_backing_store
        cb.addItems(self.backing_stores)
        cb.currentIndexChanged.connect(self.backing_store_combobox_index_changed)
        self.backing_store_combobox_index_changed()

    def init_encryption_modes_combobox(self):
        cb = self.cb_encryption_mode
        cb.addItems([m.value for m in self.encryption_modes])
        cb.currentIndexChanged.connect(self.encryption_mode_combobox_index_changed)
        self.encryption_mode_combobox_index_changed()

    def backing_store_combobox_index_changed(self):
        idx_value = self.cb_backing_store.currentText()
        if 'file' == idx_value:
            self.lbl_repo_path.show()
            self.txt_repo_path.show()
            self.btn_repo_path_browse.show()
        else:
            # TODO: Fix for more backing stores
            self.lbl_repo_path.hide()
            self.txt_repo_path.hide()
            self.btn_repo_path_browse.hide()

    def encryption_mode_combobox_index_changed(self):
        idx_value = self.cb_encryption_mode.currentText()
        method = self.encryption_modes(idx_value)
        if method.requires_password:
            self.txt_password.show()
            self.txt_password_check.show()
            self.lbl_password.show()
            self.lbl_password_check.show()
        else:
            self.txt_password.hide()
            self.txt_password.setText(None)
            self.txt_password_check.hide()
            self.txt_password_check.setText(None)
            self.lbl_password.hide()
            self.lbl_password_check.hide()

    def btn_open_browser(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
        path = dialog.getExistingDirectory(self, self.tr('Choose Repository'),
                                           os.path.expanduser('~'))
        self.txt_repo_path.setText(path)

    def accept(self):
        if self.check_input():
            model = InitRepoViewModel()
            model.name = self.txt_repo_name.text()
            if self.cb_backing_store.currentIndex() >= 0:
                backing_store_str = self.cb_backing_store.currentText()
                model.backing_store = BackingStoreAdapterFactory.adapter_for_protocol(backing_store_str)
            model.path = self.txt_repo_path.text()

            if self.cb_encryption_mode.currentIndex() >= 0:
                model.encryption_mode = self.cb_encryption_mode.currentText()
            model.password = self.txt_password.text()

            if self.listener:
                self.listener.btn_accept_click(model)

    def check_input(self):
        message = None

        repo_name_valid, repo_name_error = self.listener.check_valid_new_repo_name(self.txt_repo_name.text())
        if not repo_name_valid:
            message = self.tr("The repository name is invalid:\n%s" % str(repo_name_error))
        elif not self.txt_repo_path.text():
            message = self.tr("Please choose a path for the repository")
        else:
            idx_value = self.cb_encryption_mode.currentText()
            method = self.encryption_modes(idx_value)
            if method.requires_password:
                if not self.txt_password.text():
                    message = self.tr("Please enter a password")
                elif not self.txt_password_check.text():
                    message = self.tr("Please repeat the password")
                elif not self.txt_password.text() == self.txt_password_check.text():
                    message = self.tr("Passwords do not match")

        if message:
            self.show_input_error_message_box(message=self.tr("Input error"), message_detail=message)
            return False

        return True

    def show_success(self, detail=None):
        self.show_success_message_box(self.tr("Successfully created repository"), detail, function=self.close)

    def show_error(self, detail=None):
        self.show_error_message_box(self.tr("Error creating repository"), detail)


class InitRepoViewModel:
    def __init__(self):
        self.name = None
        self.backing_store = None
        self.path = None
        self.encryption_mode = None
        self.password = None
        self.name = None
