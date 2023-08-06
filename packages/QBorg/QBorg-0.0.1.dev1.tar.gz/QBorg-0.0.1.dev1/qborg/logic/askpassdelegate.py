import logging

from qborg.qborg import QBorgApp
from qborg.entities.repository import Repository

_logger = logging.getLogger(__name__)


class AskPassphraseDelegate():
    def __init__(self, repository, delegate=None, askpass_func=None):
        if not isinstance(repository, Repository):
            raise TypeError('Invalid repository given')

        self._repository = repository

        if callable(askpass_func):
            self._askpass_func = askpass_func
        elif callable(getattr(delegate, 'passphrase_prompt', None)):
            self._askpass_func = delegate.passphrase_prompt
        else:
            self._askpass_func = lambda: _logger.error('No askpass function available!')

    def passphrase_prompt(self, message):
        passphrase_manager = QBorgApp.instance().passphrase_manager
        try:
            return passphrase_manager.get(self._repository.name)
        except KeyError:
            return self._askpass_func(message=message)
