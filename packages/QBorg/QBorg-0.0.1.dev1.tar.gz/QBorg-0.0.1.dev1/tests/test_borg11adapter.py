import os

from unittest import TestCase
from unittest.mock import patch, ANY
from distutils.version import StrictVersion

from qborg.adapters.backingstore.file import FileBackingStoreAdapter
from qborg.adapters.backup import NoPassphraseError
from qborg.adapters.backup.borg.borg11adapter import Borg11Adapter, Borg11EncryptionMode
from qborg.entities.location import Location
from qborg.entities.repository import Repository


class Borg11AdapterTest(TestCase):
    def setUp(self):
        with patch('qborg.adapters.backup.borg.BorgAdapter._find_borg_executable') as find_borg_mock:
            find_borg_mock.return_value = '/usr/fake/bin/borg'
            self.adapter = Borg11Adapter()

        self.borg_bin = self.adapter.borg_bin
        self.location = Location(FileBackingStoreAdapter(), '/tmp/borgrepo')
        self.repository = Repository("borgrepo", self.location, Borg11EncryptionMode.NONE)
        self.archive_name = "borgbackup"

    def test_supported_encryption_modes(self):
        assert self.adapter.supported_encryption_modes is Borg11EncryptionMode

    def test_borg_version(self):
        assert self.adapter.get_borg_version() == StrictVersion('1.1')

    def test_handle_encryption(self):
        enc_none = Borg11EncryptionMode.NONE
        enc_pwd = Borg11EncryptionMode.REPOKEY

        # Test if environment variable is set
        with patch.dict(os.environ, {}):
            self.adapter._handle_encryption(enc_pwd, passphrase='s3cret')
            assert os.environ['BORG_PASSPHRASE'] == 's3cret'

        # Test that no password is set if encryption_mode is none
        with patch.dict(os.environ, {}):
            self.adapter._handle_encryption(enc_none, passphrase='s3cret')
            assert 'BORG_PASSPHRASE' not in os.environ

        # Test that an exception is raised if no password is passed even though
        # it should have
        with patch.dict(os.environ, {}):
            with self.assertRaises(NoPassphraseError):
                self.adapter._handle_encryption(enc_pwd)
            assert 'BORG_PASSPHRASE' not in os.environ

    def test_init_local_repository(self):
        encryption_mode = Borg11EncryptionMode.NONE

        # Test valid parameters
        with patch('qborg.adapters.backup.borg.borg11adapter.Borg11Adapter._run_command') as run_mock:
            self.adapter.init_repository(self.location, encryption_mode)

            run_mock.assert_called_once_with(
                [self.borg_bin, 'init', '--progress', '--log-json', '--show-version',
                 '--show-rc', '--encryption', encryption_mode.value,
                 self.location.borg_url], delegate=ANY)

        # Test invalid location
        with patch('qborg.adapters.backup.borg.borg11adapter.Borg11Adapter._run_command') as run_mock:
            with self.assertRaises(TypeError):
                self.adapter.init_repository('/some/path', encryption_mode)
            assert not run_mock.called

        # Test invalid encryption_mode
        with patch('qborg.adapters.backup.borg.borg11adapter.Borg11Adapter._run_command') as run_mock:
            with self.assertRaises(TypeError):
                self.adapter.init_repository(self.location, 'none')
            assert not run_mock.called

    @patch('qborg.adapters.backup.borg.borg11adapter.Borg11Adapter._run_command')
    def test_delete_local_backup(self, run_mock):
        self.adapter.delete_archive(self.repository, self.archive_name)

        run_mock.assert_called_once_with(
            [self.borg_bin, 'delete', '--progress', '--log-json', '--show-version',
             '--show-rc',
             '::'.join([self.repository.location.borg_url, self.archive_name])], delegate=ANY)

    @patch('qborg.adapters.backup.borg.borg11adapter.Borg11Adapter._run_command')
    def test_list_repository(self, run_mock):
        repository = Repository('test', self.location, Borg11EncryptionMode.NONE)

        self.adapter.list_repository(repository)

        # FIXME run_mock.assert_called_once_with([self.borg_bin, 'list', repository.location.borg_url])

    @patch('qborg.adapters.backup.borg.borg11adapter.Borg11Adapter._run_command')
    def test_delete_local_repository(self, run_mock):
        repository = Repository('test', self.location, Borg11EncryptionMode.NONE)

        self.adapter.delete_repository(repository)

        run_mock.assert_called_once_with(
            [self.borg_bin, 'delete', self.location.borg_url, '--progress', '--log-json', '--show-version',
             '--show-rc'], delegate=ANY)


class Borg11EncryptionModeTest(TestCase):
    def test_requires_password(self):
        correct_values = {
            'none': False,
            'repokey': True,
            'keyfile': True
        }

        for mode in Borg11EncryptionMode:
            if mode.value in correct_values:
                em = mode.value
                assert correct_values[em] == mode.requires_password
            else:
                raise KeyError(
                    'Cannot test whether encryption mode %s '
                    'requires a password because there is no correct value '
                    'available.' % mode.value)
