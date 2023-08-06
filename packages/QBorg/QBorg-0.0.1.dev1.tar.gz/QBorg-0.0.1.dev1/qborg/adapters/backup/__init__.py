import enum


class IBackupAdapter:
    @property
    def supported_encryption_modes(self):
        # Returns a 'none' only enum by default
        return enum.Enum('NONE', 'none')

    @property
    def supported_compression_modes(self):
        # Returns a 'none' only enum by default
        return enum.Enum('NONE', 'none')

    # Repository commands

    def init_repository(self, location, encryption_mode, password=None, delegate=None):
        raise NotImplementedError('init_repository not implemented')

    def list_repository(self, repository, access_unknown_repo=False, delegate=None):
        raise NotImplementedError('list_repository not implemented')

    def repository_info(self, repository, access_unknown_repo=False, delegate=None):
        raise NotImplementedError('repository_info not implemented')

    def delete_repository(self, repository, access_unknown_repo=False, delegate=None):
        raise NotImplementedError('delete_repository not implemented')

    # Archive commands

    def create_backup(self, repository, archive_name, compression_method, include_paths, exclude_paths,
                      access_unknown_repo=False, delegate=None):
        raise NotImplementedError('create_backup not implemented')

    def extract_backup(self, repository, archive_name, target_path,
                       access_unknown_repo=False, delegate=None):
        raise NotImplementedError('extract_backup not implemented')

    def list_archive(self, repository, archive_name, access_unknown_repo=False, delegate=None):
        raise NotImplementedError('list_archive not implemented')

    def archive_info(self, repository, archive_name, access_unknown_repo=False, delegate=None):
        raise NotImplementedError('archive_info not implemented')

    def delete_archive(self, repository, archive_name, access_unknown_repo=False, delegate=None):
        raise NotImplementedError('delete_archive not implemented')


class IBackupDelegate():
    def passphrase_prompt(self, **kwargs):
        raise NotImplementedError('passphrase_prompt not implemented')

    def progress(self, **kwargs):
        raise NotImplementedError('progress not implemented')

    def progress_message(self, **kwargs):
        raise NotImplementedError('progress_message not implemented')

    def log_message(self, **kwargs):
        raise NotImplementedError('log_message not implemented')

    def result(self, **kwargs):
        raise NotImplementedError('result not implemented')

    def process_finished(self, rc):
        raise NotImplementedError('process_finished not implemented')


class NoPassphraseError(Exception):
    pass


class PassphraseWrongError(Exception):
    pass


class TooManyAttemptsError(Exception):
    pass
