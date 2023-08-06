from unittest import TestCase
from unittest.mock import patch

from qborg.entities.repository import Repository
from qborg.ui.pyqt4.controllers.initrepocontroller import InitRepoController, InitRepoDelegate


class ThreadProxyHelper:
    def __init__(self, _self, _func, *args, **kwargs):
        self._self = _self
        self._func = _func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._func(self._self, *self._args, **self._kwargs)


class InitRepoTest(TestCase):

    def setUp(self):
        with patch('qborg.ui.pyqt4.controllers.initrepocontroller.InitRepoLogic'), \
             patch('qborg.ui.pyqt4.controllers.initrepocontroller.InitRepoGui'), \
             patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui') as parent_mock:
            self.ic = InitRepoController(parent=parent_mock)

    @patch('qborg.ui.pyqt4.controllers.initrepocontroller.InitRepoLogic')
    @patch('qborg.ui.pyqt4.controllers.initrepocontroller.InitRepoGui')
    @patch('qborg.ui.pyqt4.controllers.maincontroller.MainGui')
    def test_constructor(self, maingui_mock, repogui_mock, logic_mock):
        c = InitRepoController(parent=maingui_mock)

        logic_mock.assert_called_once_with()
        logic_mock.return_value.get_supported_encryption_modes.assert_called_once_with()
        self.assertEqual(maingui_mock, c.parent)
        repogui_mock.assert_called_once_with(c.backing_stores, c.encryption_modes, c)

    @patch('qborg.ui.pyqt4.controllers.initrepocontroller.InitRepoDelegate')
    def test_btn_accept(self, delegate_mock):
        model = Repository("name", "location", "none")
        model_dict = vars(model)

        self.ic.btn_accept_click(model)
        delegate_mock.assert_called_once_with(controller=self.ic, parent=self.ic.widget)

        self.ic.logic.init_repository.assert_called_once_with(
            delegate=delegate_mock.return_value, callback=None, **model_dict)


class InitRepoDelegateTest(TestCase):

    @patch('qborg.ui.pyqt4.controllers.initrepocontroller.ControllerDelegate.__init__')
    def test_constructor(self, init_mock):
        InitRepoDelegate("controller", "parent")
        init_mock.assert_called_once_with("controller", "parent", title="Initialising repository...")
