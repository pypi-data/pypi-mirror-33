import logging

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QProgressDialog

from qborg.adapters.backup import NoPassphraseError
from qborg.ui.pyqt4 import pyqtRunOnGuiThread


_logger = logging.getLogger(__name__)


class ControllerDelegate:
    def __init__(self, controller, parent, title=None):
        self.controller = controller
        self.parent = parent

        self.dialog = QProgressDialog(title, 'Cancel', 0, 3)
        self.dialog.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.dialog.setWindowModality(Qt.WindowModal)
        # Only display the dialog if the process lasts longer than 1s
        self.dialog.setMinimumDuration(1000)

        self.dialog.show()

    @pyqtRunOnGuiThread
    def progress_message(self, levelname, message):
        status_text = "[%s] %s" % (levelname, message)
        _logger.debug(status_text)
        self.dialog.setLabelText(status_text)

    @pyqtRunOnGuiThread
    def progress_percent(self, **kwargs):
        if not kwargs['finished']:
            total = kwargs['total']
            if total != self.dialog.maximum():
                self.dialog.setMaximum(total)
            self.dialog.setValue(kwargs['current'])
            self.dialog.setLabelText(kwargs['message'])
        else:
            self.dialog.setValue(self.dialog.maximum())

    @pyqtRunOnGuiThread
    def close_dialog(self):
        self.dialog.reset()

    @pyqtRunOnGuiThread
    def password_prompt(self, message):
        try:
            password = self.controller.parent.ask_for_password(message=message)
        except NoPassphraseError:
            return None
        else:
            return password

    @pyqtRunOnGuiThread
    def too_many_attempts(self):
        self.parent.show_error_message_box(message='Too many password attempts',
                                           message_detail='Exceeded the maximum password retries')

    def result(self, **kwargs):
        _logger.debug('Discarding result of operation')

    @pyqtRunOnGuiThread
    def success(self):
        self.dialog.setValue(self.dialog.maximum())
        self.close_dialog()
        self.show_success_message()

    @pyqtRunOnGuiThread
    def show_success_message(self):
        self.parent.show_success()

    @pyqtRunOnGuiThread
    def error(self, error_message, error_id):
        self.close_dialog()
        self.show_error_message(error_message)

    def show_error_message(self, error_message):
        self.parent.show_error(detail=error_message)

    def process_finished(self, rc):
        _logger.debug('Process finished with rc %d' % rc)
        self.close_dialog()
