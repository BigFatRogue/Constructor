from PyQt5 import QtWidgets


class MessageInforation(QtWidgets.QMessageBox):
    def __init__(self, parent, text='Внимание', title='Внимание'):
        super().__init__(parent)
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        