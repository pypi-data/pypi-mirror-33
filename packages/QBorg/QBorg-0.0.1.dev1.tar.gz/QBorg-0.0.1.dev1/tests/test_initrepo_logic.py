import enum

from unittest import TestCase
from unittest.mock import patch

from qborg.adapters.backingstore.file import FileBackingStoreAdapter
from qborg.entities.config import Config
from qborg.entities.location import Location
from qborg.entities.repository import Repository
from qborg.logic.initrepo import InitRepoLogic


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'


class InitRepoLogicTest(TestCase):

    def setUp(self):
        with patch('qborg.adapters.backup.borg.BorgAdapter._find_borg_executable') as find_borg_mock:
            find_borg_mock.return_value = '/usr/fake/bin/borg'
            self.logic = InitRepoLogic()

    @patch('qborg.logic.initrepo.QBorgApp')
    @patch('qborg.logic.config_file_manager.ConfigFileManager', autospec=True)
    def test_check_valid_new_repo_name(self, config_manager_mock, app_mock):
        config_manager_mock.config = Config()
        for repo_name in ['TestRepo', 'RepoA', 'AnotherRepo']:
            location = Location(FileBackingStoreAdapter(), '/tmp/repos/%s' % repo_name)
            repository = Repository(repo_name, location, BorgMockEncryptionMode.NONE)
            config_manager_mock.config.repositories.add(repository)
        app_mock.instance.return_value.config_manager = config_manager_mock

        with self.assertRaises(TypeError):
            self.logic.check_valid_new_repo_name(None)

        with self.assertRaises(ValueError):
            self.logic.check_valid_new_repo_name('')

        with self.assertRaises(ValueError):
            self.logic.check_valid_new_repo_name('RepoA')

        assert self.logic.check_valid_new_repo_name('non_exist') is True
