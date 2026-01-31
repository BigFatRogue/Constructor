from PyQt5 import QtWidgets, QtCore, QtGui


class WindowFormatCell(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setWindowModality(QtCore.Qt.WindowModal)