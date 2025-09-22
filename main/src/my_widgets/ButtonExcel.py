from PyQt5 import QtCore, QtGui, QtWidgets


class ButtonExcel(QtWidgets.QPushButton):
    signal_click_btn = QtCore.pyqtSignal(bool)

    def __init__(self, parent, folder_icon, *args, **kwargs):
        super().__init__(parent)

        self.folder_icon = folder_icon
        self.is_data = None

        self.init()

    def init(self):
        self.setText('')
        self.setMaximumSize(25, 25)

        self.icon = QtGui.QIcon()
        self.setIconButton()

    def setIconButton(self) -> None:
        if self.is_data is None:
            self.is_data = True

        self.is_data = not self.is_data
        if not self.is_data:
            icon_path = f"{self.folder_icon}/excel.png"
        else:
            icon_path = f"{self.folder_icon}/excel_del.png"

        self.icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setIcon(self.icon)
        self.setIconSize(QtCore.QSize(20, 20))