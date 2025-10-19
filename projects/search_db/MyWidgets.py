from PyQt5 import QtCore, QtGui, QtWidgets


class LineEdit(QtWidgets.QLineEdit):
    signal_text = QtCore.pyqtSignal(tuple)

    def __init__(self, parent, text_default=''):
        super().__init__(parent)
        self.text_default = text_default
        self.setStyleSheet('border-radius: 5px; color: gray')
        self.setMaximumSize(10000, 50)
        self.setText(text_default)

        self.setDragEnabled(False)
        self.setObjectName("lineEdit")

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super(LineEdit, self).keyPressEvent(event)
        self.signal_text.emit((self.text(), event))

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        super(LineEdit, self).focusInEvent(event)
        if self.text() == self.text_default:
            self.setStyleSheet('border-radius: 5px; color: black')
            self.setText('')

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        super(LineEdit, self).focusOutEvent(event)
        if self.text() == self.text_default or len(self.text()) == 0:
            self.setStyleSheet('border-radius: 5px; color: gray')
            self.setText(self.text_default)


class IconLabel(QtWidgets.QLabel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        super().mouseMoveEvent(ev)
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        super(self, IconLabel).mousePressEvent(ev)
        print('asd')
    
    def eventFilter(self, obj: QtWidgets.QWidget, event: QtCore.QEvent) -> bool:
        super().eventFilter(obj, event)