import enum
import io
import os
import unittest
import tempfile

from unittest.mock import patch

from qborg.adapters.backingstore.file import FileBackingStoreAdapter
from qborg.adapters.backup.borg import BorgAdapter
from qborg.logic.config_file_manager import ConfigFileManager
from qborg.entities.config import Config
from qborg.entities.job import Job
from qborg.entities.location import Location
from qborg.entities.repository import Repository


class BorgMockEncryptionMode(enum.Enum):
    NONE = 'none'


class BorgMockAdapter(BorgAdapter):
    supported_encryption_modes = BorgMockEncryptionMode


class TestConfigFileManager(unittest.TestCase):
    def setUp(self):
        repository_name = 'TestRepo'
        job_name = 'TestJob'
        location = Location(FileBackingStoreAdapter(), os.path.join(
            tempfile.gettempdir(), 'qborg',
            repository_name.replace(' ', '_').lower()))
        precommands = ['a_script.sh']
        postcommands = ['another_script.sh']
        includes = ['/tmp']
        excludes = ['/tmp/tmp*']
        keep_daily = 0
        keep_weekly = 5
        keep_monthly = 1

        self.yaml_valid = """
            repositories:
                '%(name)s':
                    location: {backingstore: 'file', path: '%(path)s'}
                    encryption_mode: 'none'
                    jobs:
                        '%(job_name)s':
                            excludes: %(excludes)s
                            includes: %(includes)s
                            postcommands: %(postcommands)s
                            precommands: %(precommands)s
                    prune:
                        keep_daily: %(keep_daily)d
                        keep_weekly: %(keep_weekly)d
                        keep_monthly: %(keep_monthly)d
        """ % dict(name=repository_name, path=location.path, job_name=job_name,
                   excludes=excludes, includes=includes, postcommands=postcommands,
                   precommands=precommands, keep_daily=keep_daily,
                   keep_weekly=keep_weekly, keep_monthly=keep_monthly)

        self.job = Job(job_name)
        self.job.precommands.extend(precommands)
        self.job.postcommands.extend(postcommands)
        self.job.includes.extend(includes)
        self.job.excludes.extend(excludes)

        self.repository = Repository(repository_name, location,
                                     BorgMockEncryptionMode('none'))
        self.repository.prune['keep_daily'] = keep_daily
        self.repository.prune['keep_weekly'] = keep_weekly
        self.repository.prune['keep_monthly'] = keep_monthly
        self.repository.jobs.add(self.job)

        self.config = Config()
        self.config.repositories.add(self.repository)

    def _patched_config_manager(self, file_handle=None):
        with patch('qborg.logic.config_file_manager.ConfigFileManager._find_config') as find_mock,\
                patch('qborg.logic.config_file_manager.fcntl.flock'):
            # Pass a non-existing path into ConfigFileManager.__init__ so that
            # it does not get loaded automatically
            find_mock.return_value = '/non_exist'
            config_file_manager = ConfigFileManager()
            if file_handle:
                # Inject test config handle
                config_file_manager._config_file = file_handle
        return config_file_manager

    def test_load_valid_config(self):
        test_conf = tempfile.TemporaryFile()
        test_conf.write(self.yaml_valid.encode())

        config_file_manager = self._patched_config_manager(test_conf)
        # HACK: Mocking the adapter should not be needed because the Repository
        # loader should not call the adapter
        with patch('qborg.logic.factories.BackupAdapterFactory.get_adapter') as factory_mock:
            factory_mock.return_value = BorgMockAdapter
            config_file_manager.load_config()

        assert config_file_manager.config.dump() == self.config.dump()

    def test_save_load_no_modifications(self):
        # Note: encoding is needed for YAML emitter
        test_conf = tempfile.TemporaryFile(mode='w+', encoding='utf-8')
        config_file_manager = self._patched_config_manager(test_conf)
        config_file_manager._config = self.config

        config_file_manager.save_config()

        assert test_conf.tell() > 0  # assert something was written
        test_conf.seek(0, io.SEEK_SET)

        config_file_manager._config = None
        # HACK: Mocking the adapter should not be needed because the Repository
        # loader should not call the adapter
        with patch('qborg.logic.factories.BackupAdapterFactory.get_adapter') as factory_mock:
            factory_mock.return_value = BorgMockAdapter
            config_file_manager.load_config()

        assert config_file_manager.config.dump() == self.config.dump()
