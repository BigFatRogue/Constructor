from PyQt5 import QtWidgets
from ca_modes.error_code import ErrorCode


class MessageInforation(QtWidgets.QMessageBox):
    def __init__(self):
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setWindowTitle('Внимание')
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        
    def set_error(self, error_code: ErrorCode) -> None:
        self.setText(f'{error_code.message}\n{error_code.description}')
