import enum
import json
import logging
import os
from distutils.version import StrictVersion

from qborg.adapters.backup import NoPassphraseError
from qborg.adapters.backup.borg import BorgAdapter
from qborg.adapters.backup.borg.iodelegate import IODelegate
from qborg.entities.command import Command
from qborg.entities.location import Location
from qborg.entities.repository import Repository
from qborg.util.commandthread import CommandThread

_logger = logging.getLogger(__name__)

CONFIRM_DELETE = 'BORG_DELETE_I_KNOW_WHAT_I_AM_DOING'
CONFIRM = 'BORG_CHECK_I_KNOW_WHAT_I_AM_DOING'

BORGENV_PASSPHRASE = 'BORG_PASSPHRASE'
BORGENV_NEW_PASSPHRASE = 'BORG_NEW_PASSPHRASE'
BORGENV_DISPLAY_PASSPHREASE = 'BORG_DISPLAY_PASSPHRASE'
BORGENV_ACCESS_UNKNOWN_REPO_OK = 'BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK'

MAX_PASSWORD_ATTEMPTS = 3


class Borg11EncryptionMode(enum.Enum):
    NONE = 'none'
    REPOKEY = 'repokey'
    KEYFILE = 'keyfile'

    @property
    def requires_password(self):
        # all modes except for NONE require a password
        return (self != self.NONE)


class Borg11CompressionMode(enum.Enum):
    NONE = 'none'
    LZ4 = 'lz4'
    ZLIB = 'zlib'
    LZMA = 'lzma'


class Borg11Adapter(BorgAdapter):
    def __init__(self, borg_bin='borg'):
        super().__init__(borg_bin=borg_bin)

        os.environ.setdefault(BORGENV_DISPLAY_PASSPHREASE, 'NO')
        os.environ.setdefault(CONFIRM_DELETE, 'YES')

    @property
    def supported_encryption_modes(self):
        return Borg11EncryptionMode

    @property
    def supported_compression_modes(self):
        return Borg11CompressionMode

    def get_borg_version(self):
        return StrictVersion('1.1')

    def delegate_call(self, target, name, args_dict):
        if not target:
            return

        func = getattr(target, name, None)
        if callable(func):
            try:
                return func(**args_dict)
            except Exception as e:
                _logger.warning('%s raised %s', func, e)
        else:
            _logger.debug('%s does not implement %s', target, name)

    def _handle_encryption(self, encryption_mode, passphrase=None):
        if encryption_mode.requires_password:
            if passphrase:
                os.environ[BORGENV_PASSPHRASE] = passphrase
            else:
                raise NoPassphraseError(
                    'encryption_mode %s requires a password, but none was provided' % encryption_mode.value)

    def _set_access_unknown_repo(self, flag):
        value = 'YES' if flag else 'NO'
        os.environ[BORGENV_ACCESS_UNKNOWN_REPO_OK] = value

    def _run_command(self, command, delegate=None, cwd=None):
        _logger.info('Running command %s' % command)
        t = CommandThread(command, delegate, cwd)
        t.start()
        return Command(t)

    # Repository commands

    def init_repository(self, location, encryption_mode, password=None,
                        append_only=False, quota=None, delegate=None):
        if not isinstance(location, Location):
            raise TypeError('location must be a Location')
        if not isinstance(encryption_mode, Borg11EncryptionMode):
            raise TypeError('encryption_mode must be a Borg11EncryptionMode')

        command = [self.borg_bin, 'init', '--progress', '--log-json',
                   '--show-version', '--show-rc']
        command.extend(['--encryption', encryption_mode.value])
        if append_only:
            command.append('--append-only')
        if quota:
            command.extend(['--storage-quota', quota])
        command.append(location.borg_url)

        self._handle_encryption(encryption_mode, password)

        return self._run_command(command, delegate=IODelegate(self, delegate))

    def list_repository(self, repository, access_unknown_repo=False, delegate=None):
        if not isinstance(repository, Repository):
            raise TypeError('Invalid repository provided')

        if repository.encryption_mode.requires_password:
            self._handle_encryption(
                repository.encryption_mode,
                self.delegate_call(delegate, 'passphrase_prompt', dict(
                    message='Enter the password for the repository %s:' % repository.name, name=repository.name)))

        class ListRepositoryDelegate(IODelegate):
            def process_terminated(self, rc):
                print(self.line_buffer)
                if 0 == rc:
                    json_dict = json.loads(self.line_buffer)
                    self.adapter.delegate_call(self.delegate, 'result',
                                               dict(archives=json_dict.get('archives', [])))

                super().process_terminated(rc)

        command = [self.borg_bin, 'list', repository.location.borg_url]
        command.extend(['--log-json', '--json'])

        self._set_access_unknown_repo(access_unknown_repo)
        return self._run_command(command, delegate=ListRepositoryDelegate(self, delegate))

    def repository_info(self, repository, access_unknown_repo=False, delegate=None):
        if not isinstance(repository, Repository):
            raise TypeError('invalid repository provided')

        command = [self.borg_bin, 'info', repository.location.borg_url]

        self._handle_encryption(repository.encryption_mode, repository.password)
        self._set_access_unknown_repo(access_unknown_repo)

        return self._run_command(command)

    def delete_repository(self, repository, access_unknown_repo=False, delegate=None):
        if not isinstance(repository, Repository):
            raise TypeError('invalid repository provided')

        if repository.encryption_mode.requires_password:
            self._handle_encryption(
                repository.encryption_mode,
                self.delegate_call(delegate, 'passphrase_prompt', dict(
                    message='Enter the password for the repository %s:' % repository.name, name=repository.name)))

        command = [self.borg_bin, 'delete', repository.location.borg_url]
        command.extend(['--progress', '--log-json', '--show-version', '--show-rc'])

        self._set_access_unknown_repo(access_unknown_repo)

        return self._run_command(command, delegate=IODelegate(self, delegate))

    # Archive commands

    def create_backup(self, repository, archive_name, compression_mode, include_paths, encryption,
                      exclude_paths=[], access_unknown_repo=False, delegate=None):
        if not isinstance(repository, Repository):
            raise TypeError('invalid repository provided')
        if not isinstance(compression_mode, Borg11CompressionMode):
            raise TypeError('compression_mode must be a Borg11CompressionMode')

        if not archive_name:
            raise ValueError('No archive_name provided')

        if repository.encryption_mode.requires_password:
            self._handle_encryption(
                repository.encryption_mode,
                self.delegate_call(delegate, 'passphrase_prompt', dict(
                    message='Enter the password for the repository %s:' % repository.name, name=repository.name)))

        command = [self.borg_bin, 'create', '--progress', '--log-json',
                   '--show-version', '--show-rc']
        command.extend(['--compression', compression_mode.value])
        command.append('::'.join([repository.location.borg_url, archive_name]))

        for path in exclude_paths:
            command.extend(['--exclude', path])

        command.extend(include_paths)

        self._set_access_unknown_repo(access_unknown_repo)
        return self._run_command(command, delegate=IODelegate(self, delegate))

    def extract_backup(self, repository, archive_name, target_path,
                       access_unknown_repo=False, delegate=None):
        if not isinstance(repository, Repository):
            raise TypeError('invalid repository provided')

        if repository.encryption_mode.requires_password:
            self._handle_encryption(
                repository.encryption_mode,
                self.delegate_call(delegate, 'passphrase_prompt', dict(
                    message='Enter the password for the repository %s:' % repository.name, name=repository.name)))

        command = [self.borg_bin, 'extract', '--progress', '--show-version',
                   '--show-rc', '--log-json',
                   '::'.join([repository.location.borg_url, archive_name])]

        self._set_access_unknown_repo(access_unknown_repo)

        return self._run_command(command, cwd=target_path,
                                 delegate=IODelegate(self, delegate))

    def list_archive(self, repository, archive_name, access_unknown_repo=False, delegate=None):
        if not isinstance(repository, Repository):
            raise TypeError('invalid repository provided')

        class ListArchiveDelegate(IODelegate):
            def stderr_line(self, line):
                _logger.debug(line)

            def process_terminated(self, rc):
                if 0 == rc:
                    archive = [json.loads(line) for line in self.line_buffer.splitlines()]
                    self.adapter.delegate_call(delegate, 'result', {'archive': archive})

                self.adapter.delegate_call(delegate, 'process_finished', {'rc': rc})

        command = [self.borg_bin, 'list', '--json-lines',
                   '::'.join([repository.location.borg_url, archive_name])]

        self._handle_encryption(repository.encryption_mode, repository.password)
        self._set_access_unknown_repo(access_unknown_repo)

        return self._run_command(command,
                                 delegate=ListArchiveDelegate(self, delegate))

    def archive_info(self, repository, archive_name, access_unknown_repo=False, delegate=None):
        if not isinstance(repository, Repository):
            raise TypeError('invalid repository provided')

        command = [self.borg_bin, 'info',
                   '::'.join([repository.location.borg_url, archive_name])]

        self._handle_encryption(repository.encryption_mode, repository.password, name=repository.name)
        self._set_access_unknown_repo(access_unknown_repo)

        return self._run_command(command)

    def delete_archive(self, repository, archive_name, access_unknown_repo=False, delegate=None):
        if not isinstance(repository, Repository):
            raise TypeError('invalid repository provided')

        if repository.encryption_mode.requires_password:
            self._handle_encryption(
                repository.encryption_mode,
                self.delegate_call(delegate, 'passphrase_prompt', dict(
                    message='Enter the password for the repository %s:' % repository.name, name=repository.name)))

        command = [self.borg_bin, 'delete', '--progress', '--log-json',
                   '--show-version', '--show-rc',
                   '::'.join([repository.location.borg_url, archive_name])]

        self._set_access_unknown_repo(access_unknown_repo)

        return self._run_command(command, delegate=IODelegate(self, delegate))

    def rename_archive(self, backup_entity, archive_name, access_unknown_repo=False, delegate=None):
        repository = backup_entity.repository
        if not isinstance(repository, Repository):
            raise TypeError('invalid repository provided')

        if repository.encryption_mode.requires_password:
            self._handle_encryption(
                repository.encryption_mode,
                self.delegate_call(delegate, 'passphrase_prompt', dict(
                    message='Enter the password for the repository %s:' % repository.name, name=repository.name)))

        command = [self.borg_bin, 'rename', '--progress', '--log-json', '--show-version', '--show-rc']
        command.append('::'.join([backup_entity.repository.location.borg_url, backup_entity.name]))
        command.append(archive_name)

        self._set_access_unknown_repo(access_unknown_repo)
        return self._run_command(command, delegate=IODelegate(self, delegate))
