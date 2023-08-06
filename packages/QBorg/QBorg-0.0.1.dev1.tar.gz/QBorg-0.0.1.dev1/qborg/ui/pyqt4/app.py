import os
from PyQt4 import QtGui
from PyQt4.QtGui import QIcon, QPixmap
from PyQt4.QtCore import QTranslator, QLibraryInfo, QLocale

from qborg.ui.pyqt4.controllers.maincontroller import MainController

from . import resources  # noqa: ignore=F401


def _get_locale(args):
    # Get language from environment variables
    envvars = ['LC_ALL', 'LC_MESSAGES', 'LANG']  # first found wins

    for var in envvars:
        _val = os.getenv(var)
        if _val:
            return _val

    # Fall back to value returned by Qt
    return QLocale.system().name()


def _load_icon():
    icon = QIcon()
    icon_sizes = [16, 24, 32, 48, 64, 96, 128, 256, 512]
    for size in icon_sizes:
        filename = ':/icons/qborg-%ux%u.png' % (size, size)
        icon.addPixmap(QPixmap(filename))

    # Use X11 themed icon if available, otherwise fall back to "original" icon
    return QIcon.fromTheme('qborg', icon)


def run(qargs):
    locale = _get_locale(qargs)
    app = QtGui.QApplication(qargs)
    app.setApplicationName('QBorg')

    # Load application icon
    app.setWindowIcon(_load_icon())

    # Load translators
    qt_translator = QTranslator()
    qt_translator.load("qt_" + locale,
                       QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)

    translator = QTranslator()
    translator.load(locale,
                    os.path.join(os.path.dirname(__file__), 'translations'))
    app.installTranslator(translator)

    # Initialise main controller
    main = MainController()
    main.show()

    return app.exec_()
