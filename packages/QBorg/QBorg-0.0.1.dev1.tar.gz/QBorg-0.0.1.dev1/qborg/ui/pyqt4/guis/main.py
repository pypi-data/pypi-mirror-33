import collections

from PyQt4 import QtGui
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, QAbstractTableModel
from PyQt4.QtGui import QStandardItem

from qborg.ui.pyqt4.guis.qborggui import QBorgGui


class MainGui(QtGui.QMainWindow, QBorgGui):
    def __init__(self, parent=None, listener=None):
        super(MainGui, self).__init__(parent)
        self.show_ui('main.ui')

        self.controller = listener
        self.listener = listener

        # Connect slots
        self.a_repository_create.triggered.connect(self.create_repository)
        self.a_repository_rename.triggered.connect(self.rename_repository)
        self.a_about.triggered.connect(self.show_about_dialog)
        self.a_backup_create.triggered.connect(self.create_backup)
        self.btn_backup_delete.clicked.connect(self.delete_backup)
        self.btn_rename_backup.clicked.connect(self.rename_backup)
        # Connect buttons
        self.btn_backup_restore.clicked.connect(self.extract_backup)
        self.btn_repository_delete.clicked.connect(self.delete_repository)

    def create_repository(self):
        if self.listener is not None:
            self.listener.start_process_init()

    def rename_repository(self):
        if self.listener is not None:
            self.listener.start_process_rename_repository()

    def create_backup(self):
        if self.listener is not None:
            self.listener.start_process_create_backup()

    def rename_backup(self):
        if self.listener is not None:
            self.listener.start_process_rename_backup()

    def delete_backup(self):
        if self.listener is not None:
            self.listener.start_process_delete_backup()

    def list_repo(self, repository):
        if self.listener is not None:
            self.listener.start_process_repository_list(repository=repository)

    def show_about_dialog(self):
        if self.listener is not None:
            self.listener.show_about_dialog()

    def extract_backup(self):
        if self.listener is not None:
            self.listener.start_process_extract_backup()

    def delete_repository(self):
        if self.listener is not None:
            self.listener.start_process_repository_delete()

    def show_delete_repository_success(self, detail=None):
        self.show_success_message_box(self.tr("Successfully deleted repository"), detail)

    def show_delete_repository_error(self, detail=None):
        self.show_error_message_box(self.tr("Error deleting repository"), detail)

    def show_rename_backup_success(self, detail=None):
        self.show_success_message_box(self.tr("Successfully renamed backup"), detail)

    def show_rename_backup_error(self, detail=None):
        self.show_error_message_box(self.tr("Error renaming backup"), detail)


class MainEvent:
    def start_process_init(self):
        raise NotImplementedError

    def start_process_create_backup(self):
        raise NotImplementedError

    def start_process_rename_backup(self):
        raise NotImplementedError

    def start_process_extract_backup(self):
        raise NotImplementedError

    def start_process_delete_backup(self):
        raise NotImplementedError

    def start_process_repository_list(self, repository):
        raise NotImplementedError

    def start_delete_repository(self):
        raise NotImplementedError


class TableModel(QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def insertRows(self, position, rows, idx):
        self.beginInsertRows(QModelIndex(), position, position+rows-1)

        for i in range(rows):
            empty_row = [''] * self.columnCount(self.parent)
            self.mylist.insert(position, empty_row)

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, idx):
        self.beginRemoveRows(QModelIndex(), position, position+rows-1)

        for i in range(rows):
            del self.mylist[position]

        self.endRemoveRows()
        return True

    def setData(self, idx, val, role):
        row = idx.row()
        new_row = self.mylist[row]

        new_row[idx.column()] = str(val)

        self.mylist[row] = new_row
        self.dataChanged.emit(idx, idx)


class RepositoryTreeModel(QAbstractItemModel):
    def __init__(self, repositories):
        super().__init__()
        self._root = TreeNode()
        self._root.add_child(QBorgNode(repositories))

    def rowCount(self, idx):
        ''' Returns number of rows required for the passed index

        Does only need to return number of direct children because
        method is called for every item.
        '''
        if idx.isValid():
            return idx.internalPointer().child_count
        return self._root.child_count

    def columnCount(self, idx):
        ''' Returns number of columns required for the passed index

        Needs to return the maximum number of required columns for the
        whole tree.
        '''
        if idx.isValid():
            return idx.internalPointer().column_count
        return self._root.column_count

    def root(self):
        return self._root

    def add_child(self, node, parent):
        if not parent or not parent.isValid():
            parent = self._root
        else:
            parent = parent.internalPointer()
        parent.add_child(node)

    def parent(self, idx):
        if idx.isValid():
            p = idx.internalPointer().parent
            if p:
                return super().createIndex(p.row, 0, p)
        return QModelIndex()

    def index(self, row, column, parent_idx=None):
        if not parent_idx or not parent_idx.isValid():
            parent = self._root
        else:
            parent = parent_idx.internalPointer()

        if not super().hasIndex(row, column, parent_idx):
            return QModelIndex()

        child = parent.child(row)
        if child:
            return super().createIndex(row, column, child)
        else:
            return QModelIndex()

    def data(self, idx, role):
        if not idx.isValid():
            return None
        node = idx.internalPointer()
        if role == Qt.DisplayRole:
            return node.data(idx.column())
        return None

    def find_node_by_entity(self, node_type, entity):
        return self._find_node_by_entity(self._root.child(0), node_type, entity)

    def _find_node_by_entity(self, node, node_type, entity):
        if isinstance(node, node_type) and node.entity == entity:
            return node

        for i in range(node.child_count):
            sub_node = node.child(i)
            result = self._find_node_by_entity(sub_node, node_type, entity)
            if result is not None:
                return result

        return None


class TreeNode(QStandardItem):
    def __init__(self, data=None, entity=None):
        if isinstance(data, str):
            self._data = [data]
        elif isinstance(data, collections.Sequence):
            self._data = data
        else:
            self._data = []

        self._children = []
        self._parent = None
        self._entity = entity

        super().__init__()

    @property
    def column_count(self):
        return max([len(self._data)] + [c.column_count for c in self._children])

    @property
    def child_count(self):
        return len(self._children)

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, value):
        self._entity = value

    @property
    def parent(self):
        return self._parent

    @property
    def row(self):
        return self.parent.index_of(self) if self.parent else 0

    def data(self, column):
        if 0 <= column < len(self._data):
            return self._data[column]

    def updateData(self, column, new_data):
        if 0 <= column < len(self._data):
            self._data[column] = new_data

    def child(self, row):
        if 0 <= row < self.child_count:
            return self._children[row]

    def index_of(self, child):
        return self._children.index(child)

    def model_index(self, model, column=0):  # FIXME: shouldn't column attribute be tracked by object?
        row = self.row
        return model.createIndex(row, column, self)

    def add_child(self, child):
        child._parent = self
        self._children.append(child)

    def remove_child(self, child):
        child._parent = None
        self._children.remove(child)


class QBorgNode(TreeNode):
    def __init__(self, repositories):
        super().__init__('QBorg')

        for repo in repositories:
            self.add_child(RepositoryNode(repo))


class RepositoryNode(TreeNode):
    def __init__(self, repo=None):
        super().__init__(repo.name, repo)

        # Only load the backup nodes when the repo node
        # gets triggered for the first time
        self._loaded = False

        self._backup_collection_node = BackupCollectionNode(repository=self.entity)
        self._job_collection_node = JobCollectionNode(repository=self.entity, jobs=self.entity.jobs)

    def list_repo(self, controller=None):
        # TODO: translate header labels
        controller.table_view_init(self.entity.table_row_header())

        if not self._loaded:
            controller.start_process_repository_list(self.entity)
        else:
            # populate table view with sbackups
            for i in range(self.backup_collection_node().child_count):
                bkp = self.backup_collection_node().child(i).entity
                controller.table_view_add_item(bkp)

    def backup_collection_node(self):
        return self._backup_collection_node

    def job_collection_node(self):
        return self._job_collection_node

    def load_nodes(self, tree_model):
        if not self._loaded:
            # Add backup and jobs nodes
            tree_model.layoutAboutToBeChanged.emit()
            self.add_child(self._backup_collection_node)
            self.add_child(self._job_collection_node)
            tree_model.layoutChanged.emit()

            self._loaded = True


class JobCollectionNode(TreeNode):
    def __init__(self, repository, jobs):
        super().__init__('Jobs', repository)

        for job in jobs:
            self.add_child(JobNode(job))


class JobNode(TreeNode):
    def __init__(self, job):
        super().__init__(job.name, job)


class BackupCollectionNode(TreeNode):
    def __init__(self, repository):
        super().__init__('Backups', repository)


class BackupNode(TreeNode):
    def __init__(self, backup):
        super().__init__(backup.name, backup)
        self._loaded = False

    def list_backup(self, controller=None):
        # TODO: Translate header labels
        controller.table_view_init(self.entity.table_row_header())

        if not self._loaded:
            # Execute borg list command to load backups
            controller.start_process_backup_list(self.entity)

            self._loaded = True
        else:
            # Populate table view with files
            for i in range(len(self.entity.files)):
                bkp_file = self.entity.files[i]
                controller.table_view_add_item(bkp_file)
