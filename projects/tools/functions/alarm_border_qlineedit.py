from PyQt5 import QtWidgets, QtCore


def alarm_border_qlineedit(widget: QtWidgets.QLineEdit) -> None:
    style_sheet = widget.styleSheet()
    widget.setStyleSheet(f'#{widget.objectName()} {{border: 1px solid red}}')
    QtCore.QTimer.singleShot(3500, lambda: widget.setStyleSheet(''))