from qborg.logic.controllerdelegate import ControllerDelegate
from qborg.logic.initrepo import InitRepoLogic
from qborg.ui.pyqt4.guis.initrepo import InitRepoGui


class InitRepoDelegate(ControllerDelegate):
    last_error = None

    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent, title='Initialising repository...')

    def success(self):
        super().success()
        self.parent.close()


class InitRepoController():
    def __init__(self, callback=None, parent=None):
        self.logic = InitRepoLogic()
        self.backing_stores = self.logic.get_supported_backing_stores()
        self.encryption_modes = self.logic.get_supported_encryption_modes()
        self.parent = parent
        self.callback = callback
        self.widget = InitRepoGui(self.backing_stores, self.encryption_modes, self)

    def check_valid_new_repo_name(self, name):
        try:
            return self.logic.check_valid_new_repo_name(name), ''
        except Exception as e:
            return False, e

    def btn_accept_click(self, model):
        # Call the domain logic from here
        model_dict = vars(model)

        delegate = InitRepoDelegate(controller=self, parent=self.widget)
        self.logic.init_repository(delegate=delegate, callback=self.callback, **model_dict)
