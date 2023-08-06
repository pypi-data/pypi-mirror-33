import logging
from qborg.qborg import QBorgApp
import qborg.ui.pyqt4.controllers.maincontroller

_logger = logging.getLogger(__name__)


class RenameRepoController():
    def __init__(self, repository=None, parent=None):
        self.parent = parent
        self.old_name = repository.name
        self.repository = repository

    def change_name(self):
        new_name, ok = self.parent.get_input_dialog("Rename Repository", "New repository name", self.repository.name)
        if ok and self.old_name != new_name:

            if not new_name:
                self.parent.show_error_message_box("Input error", "Name is empty", lambda: self.change_name())
            else:
                config_manager = QBorgApp.instance().config_manager
                repositories = config_manager.config.repositories
                try:
                    if repositories[new_name]:
                        self.parent.show_error_message_box("Input error", "Name already exists",
                                                           lambda: self.change_name())
                except KeyError:
                    self.do_update(new_name, config_manager)

    def do_update(self, new_name, config_manager):
        config_manager.config.repositories[self.old_name].name = new_name
        config_manager.save_config()

        tree_model = self.parent.listener.get_tree_model()
        node = tree_model.find_node_by_entity(
            qborg.ui.pyqt4.controllers.maincontroller.RepositoryNode, self.repository)
        self.repository.name = new_name

        tree_model.layoutAboutToBeChanged.emit()
        node.updateData(0, new_name)
        tree_model.layoutChanged.emit()
