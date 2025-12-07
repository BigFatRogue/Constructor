from PyQt5 import QtWidgets


class QHLineSeparate(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class QVLineSeparate(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)