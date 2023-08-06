import os

from PyQt4 import uic
from PyQt4.QtGui import QMessageBox, QInputDialog, QLineEdit

from qborg.adapters.backup import NoPassphraseError
from qborg.ui.pyqt4 import pyqtRunOnGuiThread


FORMS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'forms')


class QBorgGui():

    @pyqtRunOnGuiThread
    def show_ui(self, name):
        """
        Loads the QT ui-file and shows it

        :param str name: name of the QT ui-file
        """
        name = os.path.join(FORMS_PATH, name)
        uic.loadUi(name, self)
        self.show()

    @pyqtRunOnGuiThread
    def show_success_message_box(self, message, message_detail=None, function=None):
        """
        Displays a dialog with an information icon, the given texts and an ok button

        :param str message: message that is shown as the main message
        :param str message_detail: detail that is shown as the detailed message
        :param function: function that will be executed when the user clicks on ok
        """
        msg = self.get_message_box(QMessageBox.Information, self.tr("Success"), message, message_detail,
                                   function=function)
        msg.show()

    @pyqtRunOnGuiThread
    def show_error_message_box(self, message, message_detail=None, function=None):
        """
        Displays a dialog with a critical icon, the given texts and an ok button

        :param str message: message that is shown as the main message
        :param str message_detail: detail that is shown as the detailed message
        :param function: function that will be executed when the user clicks on ok
        """
        msg = self.get_message_box(QMessageBox.Critical, self.tr("Error"), message, message_detail,
                                   function=function)
        msg.show()

    @pyqtRunOnGuiThread
    def show_input_error_message_box(self, message, message_detail=None, function=None):
        """
        Displays a dialog with a warning icon, the given texts and an ok button

        :param str message: message that is shown as the main message
        :param str message_detail: detail that is shown as the detailed message
        :param function: function that will be executed when the user clicks on ok
        """
        msg = self.get_message_box(QMessageBox.Warning, self.tr("Error"), message, message_detail,
                                   function=function)
        msg.show()

    @pyqtRunOnGuiThread
    def show_prompt_message_box(self, title, message):
        """
        Displays a dialog with a query and yes/no buttons.
        Use the return value of this function to perform the correct action

        :param str title: text to show as title
        :param message: message that is shown as the main message
        :return: returns the id of the clicked button
        """
        msg = self.get_message_box(QMessageBox.Question, title, message,
                                   standard_buttons=QMessageBox.Yes | QMessageBox.No)
        return msg.exec_()

    def get_message_box(self, icon, title, message, message_detail=None, standard_buttons=QMessageBox.Ok,
                        function=None):
        """
        Creates a QMessageBox with the given parameters

        :param icon: icon to show in the message box
        :type icon: QMessageBox.{Information, ...}
        :param str title: title of the message box
        :param str message: primary message
        :param str message_detail: secondary/detail message
        :param standard_buttons: buttons that are visible to the user
        :type standard_buttons: QMessageBox.{Ok, ...}
        :param function: function that will be executed when the user clicks on a button
        :return: created MessageBox
        :rtype: QMessageBox
        """
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(standard_buttons)

        if message_detail is not None:
            msg.setInformativeText(message_detail)

        if function is not None:
            msg.buttonClicked.connect(function)

        return msg

    @pyqtRunOnGuiThread
    def ask_for_password(self, title='Password prompt', message=''):
        """
        Displays a password box with a specific title and description

        :param str title: title of the password box
        :param str message: message to tell the user why you need a password
        :return: the password and whether the user clicked ok or not
        :rtype: tuple (str, bool)
        """
        password, ok = QInputDialog.getText(
            self, self.tr(title), self.tr(message), QLineEdit.Password)
        if not ok:
            raise NoPassphraseError('User cancelled password prompt')
        return password

    @pyqtRunOnGuiThread
    def get_input_dialog(self, title, label, defaultname):
        """
        Displays a dialog box with a specific title and description

        :param str title: title of the dialog box
        :param str label: is the text which is shown to the user (it should say what should be entered)
        :param str defaultname: is the default text which is placed in the line edit.
        :return: the new archive name, if the user clicked ok or not
        :rtype: tuple (str, bool)
        """
        archive_name, ok = QInputDialog.getText(self, title, label, QLineEdit.Normal, defaultname)
        return archive_name, ok
