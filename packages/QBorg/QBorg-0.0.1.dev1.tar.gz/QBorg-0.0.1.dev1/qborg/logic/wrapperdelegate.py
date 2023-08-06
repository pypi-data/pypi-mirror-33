from qborg.adapters.backup import IBackupDelegate, TooManyAttemptsError
from qborg.qborg import QBorgApp


class WrapperDelegate(IBackupDelegate):
    def __init__(self, logic, controller_delegate):
        super().__init__()
        self.logic = logic
        self.controller_delegate = controller_delegate
        self.last_error_message = None
        self.last_error_id = None
        self.name = None

    def passphrase_prompt(self, message, name):
        self.name = name
        passphrase_manager = QBorgApp().instance().passphrase_manager
        try:
            passphrase = passphrase_manager.get(name)
        except KeyError:
            passphrase = None

        if passphrase is None:
            passphrase = self.controller_delegate.password_prompt(message)
            passphrase_manager.set(name, passphrase)

        return passphrase

    def log_message(self, name, levelname, message, **kwargs):
        if 'error' == levelname.lower() and 'borg.output.show-rc' != name:
            self.last_error = message
            self.last_error_id = kwargs.get('msgid', self.last_error_id)

    def progress_message(self, operation, message, **kwargs):
        self.controller_delegate.progress_message(operation, message)

    def progress_percent(self, **kwargs):
        self.controller_delegate.progress_percent(**kwargs)

    def result(self, **kwargs):
        self.controller_delegate.result(**kwargs)

    def process_finished(self, rc):
        if 0 == rc:
            self.controller_delegate.success()
        else:
            if 'PassphraseWrong' == self.last_error_id:
                # Saved passphrase was wrong -> delete it
                QBorgApp().instance().passphrase_manager.unset(self.name)

                # Retry
                try:
                    self.run_logic()
                except TooManyAttemptsError:
                    self.controller_delegate.too_many_attempts()
            else:
                self.controller_delegate.error(self.last_error_id, self.last_error_message)

    def run_logic(self):
        pass
