from datetime import datetime

from qborg.entities.backup import Backup
from qborg.logic.controllerdelegate import ControllerDelegate
from qborg.logic.listrepo import ListRepoLogic


class ListRepoDelegate(ControllerDelegate):
    def __init__(self, controller, parent, callback=None, backup_callback=None):
        # TODO: translation
        super().__init__(controller, parent, title="Gathering repository information...")

        self.callback = callback
        self.backup_callback = backup_callback

    def result(self, archives=[]):
        if callable(self.backup_callback):
            for archive in archives:
                backup = self._create_backup_entity(archive)
                self.backup_callback(backup)

    def _create_backup_entity(self, archive_json):
        start_date = datetime.strptime(archive_json['start'], '%Y-%m-%dT%H:%M:%S.%f')

        return Backup(
            name=archive_json['archive'],
            time=start_date,
            repository=self.controller.repository)

    def success(self):
        super().success()
        self.callback(self.controller.repository)

    def show_success_message(self):
        print('Repository %s loaded' % self.controller.repository.name)


class ListRepoController():
    def __init__(self, parent, repository, callback=None, backup_callback=None):
        self.logic = ListRepoLogic()
        self.parent = parent
        self.repository = repository

        self.delegate = ListRepoDelegate(self, self.parent, callback=callback, backup_callback=backup_callback)
        try:
            self.logic.list_repository(repository=self.repository, delegate=self.delegate)
        except Exception as e:
            self.delegate.close_dialog()
            self.parent.show_error_message_box(
                message='An error occurred when listing repository %s' % repository.name,
                message_detail='%s' % e)
