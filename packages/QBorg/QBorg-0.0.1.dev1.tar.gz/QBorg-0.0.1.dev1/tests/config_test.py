import enum
import unittest

from unittest.mock import patch

from qborg.adapters.backingstore.file import FileBackingStoreAdapter
from qborg.adapters.backup.borg import BorgAdapter
from qborg.entities.config import Config
from qborg.entities.location import Location
from qborg.entities.repository import Repository


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'


class BorgMockAdapter(BorgAdapter):
    supported_encryption_modes = BorgMockEncryptionMode


class ConfigTest(unittest.TestCase):
    def test_repository(self):
        config = Config()

        repo_name = 'TestRepo'
        location = Location(FileBackingStoreAdapter(), '/tmp/repo')
        repository = Repository(repo_name, location, BorgMockEncryptionMode.NONE)

        config.repositories.add(repository)

        assert config.repositories == {repository}
        assert config.repositories[repo_name] == repository

        with self.assertRaises(KeyError):
            config.repositories['nonexisting_repository']

        with self.assertRaises(ValueError):
            config.repositories.add(repository)

        for invalid_repo in (None, 'not a repo'):
            with self.assertRaises(TypeError):
                config.repositories.add(invalid_repo)

        assert repository in config.repositories
        config.repositories.remove(repository)
        assert repository not in config.repositories

        with self.assertRaises(KeyError):
            config.repositories.remove('nonexisting_repository')
        # discard does not raise an exception
        config.repositories.discard('nonexisting_repository')

    def test_dump(self):
        config = Config()

        repo_name = 'TestRepo'
        enryption_str = 'none'
        location = Location(FileBackingStoreAdapter(), '/tmp/repo')
        repository = Repository(repo_name, location, BorgMockEncryptionMode(enryption_str))

        config.repositories.add(repository)
        assert config.dump() == {
            'repositories': {
                repo_name: {
                    'location': location.dump(),
                    'encryption_mode': enryption_str,
                    'jobs': {}
                }
            }
        }

    def test_load(self):
        config = Config()
        config.repositories.add(Repository(
            'TestRepo A', Location(FileBackingStoreAdapter(), '/tmp/repoA'), BorgMockEncryptionMode('none')))
        config.repositories.add(Repository(
            'TestRepo B', Location(FileBackingStoreAdapter(), '/tmp/repoB'), BorgMockEncryptionMode('none')))

        # HACK: Mocking the adapter should not be needed because the Repository
        # loader should not call the adapter
        with patch('qborg.logic.factories.BackupAdapterFactory.get_adapter') as factory_mock:
            factory_mock.return_value = BorgMockAdapter
            config_thawed = Config.load({
                'repositories': {
                    'TestRepo A': {
                        'location': {'backingstore': 'file', 'path': '/tmp/repoA'},
                        'encryption_mode': 'none',
                        'jobs': {}
                    },
                    'TestRepo B': {
                        'location': {'backingstore': 'file', 'path': '/tmp/repoB'},
                        'encryption_mode': 'none',
                        'jobs': {}
                    }
                }
                })

        # FIXME: Fix equality check without dump
        assert config.dump() == config_thawed.dump()
