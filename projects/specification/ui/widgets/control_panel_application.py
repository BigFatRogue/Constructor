import os
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context import SETTING, SIGNAL_BUS, DECORATE



class ButtonCPA(QtWidgets.QPushButton):
    def __init__(self, parent, name_icon: str):
        super().__init__(parent)

        self.setFixedSize(23, 23)
        self.set_icon(name_icon)
    
    def set_icon(self, name_icon: str) -> None:
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(SETTING.ICO_FOLDER, name_icon))
        self.setIcon(icon)


# @DECORATE.UNDO_REDO_FOCUSABLE(type_widget=DECORATE.TYPE_WIDGET.BUTTON_UNDO)
# class ButtonCPAUndo(ButtonCPA): ...


# @DECORATE.UNDO_REDO_FOCUSABLE(type_widget=DECORATE.TYPE_WIDGET.BUTTON_REDO)
# class ButtonCPARedo(ButtonCPA): ...



class ControlPanelAppliction(QtWidgets.QWidget):
    signal_save = QtCore.pyqtSignal()

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

        self.btn_save = ButtonCPA(self.frame, 'save.png')
        self.btn_save.setToolTip('Сохранить таблицу\nCtrl + S')
        self.btn_save.setShortcut('Ctrl+S')
        self.btn_save.clicked.connect(SIGNAL_BUS.save.emit)
        self.h_layout_frame.addWidget(self.btn_save)

        self.btn_undo = ButtonCPA(self.frame, 'arrow_back.png')
        self.btn_undo.setToolTip('Отменить изменения\nCtrl + Z')
        self.btn_undo.setShortcut('Ctrl+Z')
        self.btn_undo.clicked.connect(SIGNAL_BUS.undo.emit)
        self.h_layout_frame.addWidget(self.btn_undo)
        DECORATE.UNDO_REDO_GROUP.set_btn_undo(self.btn_undo)

        self.btn_redo = ButtonCPA(self.frame, 'arrow_forward.png')
        self.btn_redo.setToolTip('Вернуть изменения\nCtrl + Shift + Z')
        self.btn_redo.setShortcut('Ctrl+Shift+Z')
        self.btn_redo.clicked.connect(SIGNAL_BUS.redo.emit)
        self.h_layout_frame.addWidget(self.btn_redo)
        DECORATE.UNDO_REDO_GROUP.set_btn_reod(self.btn_redo)
