import os
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent)
    sys.path.append(test_path)


from projects.specification.config.settings import *
from projects.tools.custom_qwidget.line_separate import QHLineSeparate, QVLineSeparate


class ControlPanelAppliction(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.__init_widget()

    def __init_widget(self) -> None:
        self.setMinimumHeight(25)
        self.setMaximumHeight(30)
        self.setStyleSheet('QFrame {border-bottom: 1px solid gray; border-top: none; border-left: none; border-right: none}')
        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.setContentsMargins(0, 0, 0, 2)
        self.h_layout.setSpacing(0)

        self.frame = QtWidgets.QFrame(self)
        self.h_layout.addWidget(self.frame)
            
        self.h_layout_frame = QtWidgets.QHBoxLayout(self.frame)
        self.frame.setLayout(self.h_layout_frame)
        self.h_layout_frame.setContentsMargins(0, 0, 0, 2)
        self.h_layout_frame.setSpacing(2)
        self.h_layout_frame.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        self.btn_save = QtWidgets.QPushButton(self.frame)
        self.btn_save.setFixedSize(23, 23)
        self.btn_save.setToolTip('Сохранить таблицу\nCtrl + S')
        self.btn_save.setShortcut('Ctrl+S')
        self.btn_save.clicked.connect(self.click_save_table)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'save.png'))
        self.btn_save.setIcon(icon)
        self.h_layout_frame.addWidget(self.btn_save)

        self.btn_back = QtWidgets.QPushButton(self.frame)
        self.btn_back.setFixedSize(23, 23)
        self.btn_back.setToolTip('Отменить изменения\nCtrl + Z')
        self.btn_back.setShortcut('Ctrl+Z')
        self.btn_back.clicked.connect(self.click_back)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'arrow_back.png'))
        self.btn_back.setIcon(icon)
        self.h_layout_frame.addWidget(self.btn_back)

        self.btn_forward = QtWidgets.QPushButton(self.frame)
        self.btn_forward.setFixedSize(23, 23)
        self.btn_forward.setToolTip('Вернуть изменения\nCtrl + Shift + Z')
        self.btn_forward.setShortcut('Ctrl+Shift+Z')
        self.btn_forward.clicked.connect(self.click_forward)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'arrow_forward.png'))
        self.btn_forward.setIcon(icon)
        self.h_layout_frame.addWidget(self.btn_forward)


    def click_save_table(self) -> None:
        ...
    
    def click_back(self) -> None:
        ...

    def click_forward(self) -> None:
        ...