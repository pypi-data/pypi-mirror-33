import platform

from PyQt4.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QModelIndex, Qt
from PyQt4.QtGui import QMessageBox, QHeaderView, QAbstractItemView

from qborg import __copyright__, __description__, __license__, __version__
from qborg.entities.backup import Backup
from qborg.entities.repository import Repository
from qborg.qborg import QBorgApp
from qborg.ui.pyqt4 import pyqtRunOnGuiThread
from qborg.ui.pyqt4.controllers.createbackupcontroller import CreateBackupController
from qborg.ui.pyqt4.controllers.deletebackupcontroller import DeleteBackupController
from qborg.ui.pyqt4.controllers.deleterepocontroller import DeleteRepoController
from qborg.ui.pyqt4.controllers.extractbackupcontroller import ExtractBackupController
from qborg.ui.pyqt4.controllers.initrepocontroller import InitRepoController
from qborg.ui.pyqt4.controllers.listrepocontroller import ListRepoController
from qborg.ui.pyqt4.controllers.listbackupcontroller import ListBackupController
from qborg.ui.pyqt4.controllers.renamebackupcontroller import RenameBackupController
from qborg.ui.pyqt4.controllers.renamerepocontroller import RenameRepoController
from qborg.ui.pyqt4.guis.main import (
    MainGui, MainEvent, RepositoryTreeModel, QBorgNode, RepositoryNode,
    JobCollectionNode, BackupCollectionNode, JobNode, BackupNode, TableModel)


class MainController(MainEvent):
    def __init__(self):
        self.main = MainGui(listener=self)
        self.context_object = None
        self.tree_model = None
        self.table_model = None

    def get_tree_model(self):
        if not self.tree_model:
            repositories = QBorgApp.instance().config_manager.config.repositories
            self.tree_model = RepositoryTreeModel(repositories)
        return self.tree_model

    def show(self):
        self.main.show()
        self.main.tree_navigator.setModel(self.get_tree_model())
        self.main.tree_navigator.expandAll()
        self.main.tree_navigator.selectionModel().currentRowChanged.connect(self.tree_navigator_current_row_changed)

        # Expand repo tree and select root (qborg) node
        root_idx = self.main.tree_navigator.model().index(0, 0, QModelIndex())
        self.main.tree_navigator.setCurrentIndex(root_idx)

    def show_about_dialog(self):
        QMessageBox.about(
            self.main, "About QBorg",
            """<b>QBorg</b> version %(version)s
            <p>%(description)s
            <p>%(copyright)s<br>
            This application is licensed under %(license)s.
            <p>Python %(py_version)s on %(py_system)s - Qt %(qt_version)s - PyQt %(pyqt_version)s""" % {
                'copyright': __copyright__,
                'description': __description__,
                'license': __license__,
                'version': __version__,

                'py_version': platform.python_version(),
                'qt_version': QT_VERSION_STR,
                'pyqt_version': PYQT_VERSION_STR,
                'py_system': platform.system()
            })

    def start_process_init(self):
        @pyqtRunOnGuiThread
        def callback(repository):
            node = self.tree_append_repository_node(repository)
            node.list_repo(controller=self)

        InitRepoController(callback=callback, parent=self.main)

    def start_process_rename_repository(self):
        if isinstance(self.context_object, Repository):
            RenameRepoController(self.context_object, parent=self.main).change_name()

    def start_process_create_backup(self):
        repository = None
        if isinstance(self.context_object, Backup):
            repository = self.context_object.repository
        if isinstance(self.context_object, Repository):
            repository = self.context_object

        if isinstance(repository, Repository):
            CreateBackupController(repository, callback=self.tree_append_backup_node,
                                   parent=self.main)

    def start_process_rename_backup(self):
        if isinstance(self.context_object, Backup):
            RenameBackupController(self.context_object, callback=self.tree_rename_backup_node, parent=self.main)

    def start_process_delete_backup(self):
        if isinstance(self.context_object, Backup):
            DeleteBackupController(parent=self.main, backup=self.context_object,
                                   callback=self.tree_remove_node_for_entity)

    def start_process_extract_backup(self):
        if isinstance(self.context_object, Backup):
            ExtractBackupController(backup=self.context_object, parent=self.main)

    def start_process_repository_list(self, repository):
        ListRepoController(parent=self.main, repository=repository,
                           callback=self.list_repository_success,
                           backup_callback=self.tree_append_backup_node)

    def start_process_backup_list(self, backup):
        def _callback(item):
            backup.files.append(item)
            self.table_view_add_item(item)

        ListBackupController(backup=backup, parent=self.main,
                             callback=_callback)

    def start_process_repository_delete(self):
        if isinstance(self.context_object, Repository):
            controller = DeleteRepoController(self.context_object, self.main)
            controller.delete_repository(callback=self.tree_remove_node_for_entity)

    def list_repository_success(self, repository):
        tree_model = self.get_tree_model()
        found_node = tree_model.find_node_by_entity(node_type=RepositoryNode,
                                                    entity=repository)
        found_node.load_nodes(tree_model)

    def tree_navigator_current_row_changed(self, new_idx, old_idx):
        VIEW__OBJECTS = {
            self.main.btn_repository_create,
            self.main.btn_repository_rename,
            self.main.btn_repository_delete,
            self.main.btn_backup_create,
            self.main.btn_backup_delete,
            self.main.btn_backup_restore,
            self.main.btn_job_create,
            self.main.btn_job_delete,
            self.main.btn_rename_backup,
            self.main.btn_job_run,
            self.main.widget_repository_detail,
        }

        VIEW_OBJECTS_BY_NODE = {
            QBorgNode: {
                self.main.btn_repository_create,
            },
            RepositoryNode: {
                self.main.btn_repository_rename,
                self.main.btn_repository_delete,
                self.main.btn_backup_create,
                self.main.btn_job_create,
                self.main.widget_repository_detail,
            },
            JobCollectionNode: {
                self.main.btn_job_create,
                self.main.widget_repository_detail,
            },
            JobNode: {
                self.main.btn_job_create,
                self.main.btn_job_delete,
                self.main.btn_job_run,
            },
            BackupCollectionNode: {
                self.main.btn_backup_create,
                self.main.widget_repository_detail,
            },
            BackupNode: {
                self.main.btn_rename_backup,
                self.main.btn_backup_create,
                self.main.btn_backup_delete,
                self.main.btn_backup_restore,
                self.main.widget_repository_detail,
            }
        }

        selected_node = new_idx.internalPointer()
        self.context_object = selected_node.entity

        self._handle_node_checks(selected_node)
        self._handle_context_object_checks()

        active_view_objects = VIEW_OBJECTS_BY_NODE.get(type(selected_node), set())

        for o in active_view_objects:
            o.show()

        for o in VIEW__OBJECTS - active_view_objects:
            o.hide()

    def _handle_node_checks(self, node):
        self.table_view_reset()

        if isinstance(node, RepositoryNode):
            # load The Backup and job nodes for the selected repository
            node.list_repo(self)

        elif isinstance(node, BackupCollectionNode):
            node.parent.list_repo(self)

        elif isinstance(node, BackupNode):
            node.list_backup(self)

    def _handle_context_object_checks(self):
        context_object = self.context_object
        if isinstance(context_object, Repository):
            self.main.repository_title.setText(self.context_object.name)
        elif isinstance(context_object, Backup):
            self.main.repository_title.setText(
                "%s::%s" % (context_object.repository.name, context_object.name))

    def tree_append_repository_node(self, repository):
        tree_model = self.get_tree_model()
        tree_model.layoutAboutToBeChanged.emit()
        node = RepositoryNode(repository)
        tree_model.root().child(0).add_child(node)
        tree_model.layoutChanged.emit()

        return node

    def tree_append_backup_node(self, backup):
        # add backup to backup table
        self.table_view_add_item(backup)

        # Add the Backup as a BackupNode of the Repository and
        # update the tree view
        tree_model = self.get_tree_model()
        found_node = tree_model.find_node_by_entity(node_type=RepositoryNode,
                                                    entity=backup.repository)

        if found_node is not None:
            tree_model.layoutAboutToBeChanged.emit()
            found_node.backup_collection_node().add_child(BackupNode(backup))
            tree_model.layoutChanged.emit()
        else:
            raise NotImplemented

    def tree_rename_backup_node(self, entity):
        tree_model = self.get_tree_model()
        node_type = BackupNode
        found_node = tree_model.find_node_by_entity(node_type=node_type, entity=entity)
        if found_node:
            tree_model.layoutAboutToBeChanged.emit()
            found_node.updateData(0, entity.name)
            tree_model.layoutChanged.emit()

    def tree_remove_node_for_entity(self, entity):
        # Update the tree view
        tree_model = self.get_tree_model()
        if isinstance(entity, Backup):
            node_type = BackupNode
        elif isinstance(entity, Repository):
            node_type = RepositoryNode
        else:
            raise TypeError('Entities of type %s are not supported for removal in the tree' % type(entity))

        found_node = tree_model.find_node_by_entity(node_type=node_type, entity=entity)

        found_node_row = found_node.row
        if found_node:
            parent_index = found_node.parent.model_index(tree_model)
            node_idx = found_node.row

            tree_model.beginRemoveRows(parent_index, node_idx, node_idx)
            found_node.parent.remove_child(found_node)
            tree_model.endRemoveRows()

            if isinstance(found_node, BackupNode):
                # remove backup from table
                self.table_view_remove_row(found_node_row)
        else:
            raise ValueError('Could not find node for entity %s in tree' % entity)

    def table_view_reset(self):
        if self.table_model is not None:
            table_model = self.table_model
            table_model.removeRows(position=0, rows=table_model.rowCount(table_model.parent), idx=None)
            self.main.table_view.horizontalHeader().hide()

    def table_view_init(self, header, list=[]):
        self.table_model = TableModel(self.main.table_view, list, header)
        self.main.table_view.setModel(self.table_model)
        self.main.table_view.horizontalHeader().show()
        self.main.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.main.table_view.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.main.table_view.setSortingEnabled(False)
        self.main.table_view.setFocusPolicy(Qt.NoFocus)
        self.main.table_view.setSelectionMode(QAbstractItemView.NoSelection)
        self.main.table_view.setAlternatingRowColors(True)

    def table_view_add_item(self, item):
        row = item.to_table_row()
        table_model = self.table_model

        position = table_model.rowCount(table_model.parent)

        table_model.layoutAboutToBeChanged.emit()
        table_model.insertRows(position=position, rows=1, idx=None)

        for i in range(len(row)):
            idx = table_model.index(position, i)
            table_model.setData(idx=idx, val=row[i], role=None)
            table_model.layoutChanged.emit()

    def table_view_remove_row(self, position):
        table_model = self.table_model

        if table_model.rowCount(table_model.parent) <= position:
            return False

        table_model.removeRows(position=position, rows=1, idx=None)
        return True
