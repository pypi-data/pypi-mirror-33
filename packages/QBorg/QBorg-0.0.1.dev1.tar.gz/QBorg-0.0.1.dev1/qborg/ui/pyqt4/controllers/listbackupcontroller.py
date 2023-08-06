import logging

from datetime import datetime

from qborg.entities.backup import BackupFile
from qborg.logic.listbackup import ListBackupLogic
from qborg.ui.pyqt4 import pyqtRunOnGuiThread
from qborg.logic.controllerdelegate import ControllerDelegate


_logger = logging.getLogger(__name__)


class ListBackupDelegate(ControllerDelegate):
    last_error = None

    def __init__(self, controller=None, parent=None, callback=None):
        self.controller = controller  # ListBackupController
        self.callback = callback

        # TODO: translation
        super().__init__(controller, parent, title="Gathering backup information...")

    def result(self, archive):
        if not isinstance(archive, list):
            _logger.error("Returned archive is not a list. Ignoring.")
            return

        if callable(self.callback):
            for file in archive:
                self.callback(self._create_backup_file_entity(file))
        else:
            _logger.info("No callback registered. List backup result is discarded.")

    def _create_backup_file_entity(self, archive_json):
        parsed_mtime = datetime.strptime(archive_json['mtime'], '%Y-%m-%dT%H:%M:%S.%f')

        return BackupFile(
            healthy=archive_json['healthy'],
            mtime=parsed_mtime,
            path=archive_json['path'],
            size=archive_json['size'],
            qtype=archive_json['type'])

    @pyqtRunOnGuiThread
    def process_finished(self, rc):
        if 0 != rc:
            # FIXME
            _logger.error('Listing backup failed')
        super().process_finished(rc)


class ListBackupController():
    def __init__(self, backup, parent, callback=None):
        self.logic = ListBackupLogic()
        self.backup = backup  # Used by the delegate

        delegate = ListBackupDelegate(controller=self, parent=parent,
                                      callback=callback)
        try:
            self.logic.list_backup(backup, delegate=delegate)
        except Exception as e:
            delegate.close_dialog()
            parent.show_error_message_box(
                message='An error occurred when listing backup %s' % backup.name,
                message_detail='%s' % e)
