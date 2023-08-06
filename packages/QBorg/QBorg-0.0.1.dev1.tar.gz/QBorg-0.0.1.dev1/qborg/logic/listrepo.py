import logging

from qborg.adapters.backup import TooManyAttemptsError
from qborg.adapters.backup.borg.borg11adapter import MAX_PASSWORD_ATTEMPTS
from qborg.logic.factories import BackupAdapterFactory
from qborg.logic.wrapperdelegate import WrapperDelegate

_logger = logging.getLogger(__name__)


class ListRepoLogic():
    def __init__(self):
        self.adapter = BackupAdapterFactory.get_adapter()

    def list_repository(self, repository, delegate=None):
        attempt = 0
        wrapper_delegate = None

        def _run_list():
            nonlocal attempt
            attempt += 1
            if attempt > MAX_PASSWORD_ATTEMPTS:
                raise TooManyAttemptsError(
                    'Reached maximum number of attempts to list repository %s', repository.name)

            self.adapter.list_repository(repository, delegate=wrapper_delegate)

        class WrapperListRepoDelegate(WrapperDelegate):
            def run_logic(self):
                _run_list()

        wrapper_delegate = WrapperListRepoDelegate(self, delegate)

        _run_list()
