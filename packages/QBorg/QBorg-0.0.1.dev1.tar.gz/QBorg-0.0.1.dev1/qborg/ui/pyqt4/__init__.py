from PyQt4.QtCore import pyqtSlot, QCoreApplication, QMetaObject, QObject, Qt


class GuiThreadProxy(QObject):
    def __init__(self, _self, _func, *_args, **_kwargs):
        super().__init__()
        self._guithread = QCoreApplication.instance().thread()
        self._self = _self
        self._function = _func
        self._args = _args
        self._kwargs = _kwargs
        self._returnvalue = None

    def _invoke(self):
        return self._function(self._self, *self._args, **self._kwargs)

    @pyqtSlot()
    def _async_start(self):
        self._returnvalue = self._invoke()

    def run(self):
        # Check if we are on the GUI thread already. Nested invokations using
        # invokeMethod() deadlock.
        if self.thread() != self._guithread:
            # Move this QObject to the GUI thread
            self.moveToThread(self._guithread)

            # Invoke the _async_start method on the QObject thread's event loop
            # NOTE: The connection mode needs to be blocking here, because it
            # doesn't work if the proxy QObject doesn't live until the method
            # returns(??) Adding just a little bit of work after invokeMethod(...)
            # seems to be enough to make it work.
            # Also a non-blocking call makes it difficult to handle return values
            QMetaObject.invokeMethod(self, '_async_start', Qt.BlockingQueuedConnection)
            return self._returnvalue
        else:
            return self._invoke()


def pyqtRunOnGuiThread(func):
    return lambda self, *args, **kwargs: GuiThreadProxy(self, func, *args, **kwargs).run()
