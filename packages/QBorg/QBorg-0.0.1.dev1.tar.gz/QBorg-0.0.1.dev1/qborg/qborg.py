import argparse
import logging
import sys

from qborg import __description__, __version__
from qborg.logic.detection import ToolDetection
from qborg.logic.config_file_manager import ConfigFileManager
from qborg.util.passphrasemanager import PassphraseManager


LOGLEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
qborg_ui = 'qt4'


class QBorgApp():
    class __QBorgAppSingleton():
        def __init__(self, config_path=None):
            self._config_manager = ConfigFileManager(config_file=config_path)
            self._passphrase_manager = PassphraseManager()

        @property
        def config_manager(self):
            return self._config_manager

        @property
        def detection(self):
            return ToolDetection

        @property
        def passphrase_manager(self):
            return self._passphrase_manager

    _instance = None

    @classmethod
    def _init(cls, **kwargs):
        if not cls._instance:
            cls._instance = cls.__QBorgAppSingleton(**kwargs)

    @classmethod
    def instance(cls):
        return cls._instance


def _init_logging(loglevel):
    logger = logging.getLogger(__package__)
    logger.setLevel(loglevel)
    logger.addHandler(logging.StreamHandler(stream=sys.stderr))

    logger.debug('Initialised logging')


def _parse_arguments():
    parser = argparse.ArgumentParser(description='QBorg - %s' % __description__)
    parser.add_argument('--log', type=str.upper, choices=LOGLEVELS,
                        default='WARNING', dest='loglevel')
    parser.add_argument('--version', action='version',
                        version='QBorg %s' % __version__)
    return parser.parse_args()


def main():
    args = _parse_arguments()

    # Initialise logging
    loglevel = getattr(logging, getattr(args, 'loglevel').upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    _init_logging(loglevel=loglevel)

    # Initialise QBorgApp singleton
    QBorgApp._init()

    # Startup tasks, detection of Borg
    borg_version = QBorgApp.instance().detection.get_borg_version()
    if borg_version:
        print("Detected BorgBackup version: %s" % borg_version)
    else:
        print("Could not find borg. Did you install it?")

    # start the gui
    if 'qt4' == qborg_ui:
        from qborg.ui.pyqt4 import app
        return app.run(sys.argv)
