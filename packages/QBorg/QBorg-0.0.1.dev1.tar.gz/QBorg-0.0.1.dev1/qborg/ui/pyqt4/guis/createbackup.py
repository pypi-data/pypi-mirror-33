from PyQt4 import QtGui

from qborg.ui.pyqt4.guis.qborggui import QBorgGui


class CreateBackupGui(QtGui.QWidget, QBorgGui):
    def __init__(self, selected_repository_entity, repositories, compression_modes,
                 controller=None):
        super().__init__()
        self.show_ui('create_backup.ui')

        self.controller = controller
        self.compression_modes = compression_modes
        self.repositories = repositories

        self.btn_add_dir.clicked.connect(self.add_directory)
        self.btn_add_file.clicked.connect(self.add_files)
        self.btn_remove_dir_or_file.clicked.connect(self.remove_dir_or_file)
        self.bb_cancel_ok.accepted.connect(self.accept)
        self.bb_cancel_ok.rejected.connect(self.close)

        self.initialize_compression_modes()
        self.initialize_repository_overview(selected_repository_entity)
        self.initialize_job_overview()

    def enable_multi_selection(self, dialog):
        # Make it possible to select multiple directories
        f_tree_view = dialog.findChild(QtGui.QTreeView)
        if f_tree_view:
            f_tree_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        file_view = dialog.findChild(QtGui.QListView, 'listView')
        if file_view:
            file_view.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        if dialog.exec():
            self.selected_files = dialog.selectedFiles()
            return self.selected_files

    def add_item_to_list_widget(self, selected_files):
        for path in selected_files:
            path_exists = False
            for i in range(self.listWidget_dirs_and_files.count()):
                if path == self.listWidget_dirs_and_files.item(i).text():
                    path_exists = True
                    break
            if not path_exists:
                self.listWidget_dirs_and_files.addItem(path)

    def add_directory(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        if self.enable_multi_selection(dialog):
            self.add_item_to_list_widget(self.selected_files)

    def add_files(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)
        if self.enable_multi_selection(dialog):
            self.add_item_to_list_widget(self.selected_files)

    def remove_dir_or_file(self):
        for selected_item in self.listWidget_dirs_and_files.selectedItems():
            q_index = self.listWidget_dirs_and_files.indexFromItem(selected_item)
            self.listWidget_dirs_and_files.takeItem(q_index.row())

    def initialize_repository_overview(self, select_repository_entity):
        self.cb_repository.addItems([m.name for m in self.repositories])
        index = self.cb_repository.findText(select_repository_entity.name)
        self.cb_repository.setCurrentIndex(index)

    def initialize_job_overview(self):
        jobs = self.get_selected_repository().jobs
        self.cb_jobs.addItems(jobs)

    def get_selected_repository(self):
        repo_name = self.cb_repository.currentText()
        return self.repositories[repo_name]

    def initialize_compression_modes(self):
        self.cb_compression_mode.addItems([m.value for m in self.compression_modes])
        self.cb_repository.setCurrentIndex(0)

    def accept(self):
        supported_compression_modes = self.controller.get_supported_compression_modes()
        model = CreateBackupGuiModel()
        model.archive_name = self.txt_archive_name.text()
        model.repository = self.get_selected_repository()
        model.compression_mode = supported_compression_modes(self.cb_compression_mode.currentText())
        model.include_paths = [str(self.listWidget_dirs_and_files.item(i).text())
                               for i in range(self.listWidget_dirs_and_files.count())]
        model.exclude_paths = []  # TODO: Not supported yet.

        if self.check_input(model) and hasattr(self.controller, 'btn_accept_click'):
            self.controller.btn_accept_click(model)

    def check_input(self, model):
        input_valid, error = self.controller.check_model(model)

        if not input_valid:
            self.show_input_error_message_box(
                message=self.tr('Input error'), message_detail=self.tr(error))
            return False

        return True

    def show_success(self, detail=None):
        self.show_success_message_box(self.tr('Successfully created backup'),
                                      detail, function=self.close)

    def show_error(self, detail=None):
        self.show_error_message_box(self.tr('Error creating backup'), detail)


class CreateBackupGuiModel:
    repository = None
    archive_name = None
    compression_mode = None
    include_paths = None
    exclude_paths = None
