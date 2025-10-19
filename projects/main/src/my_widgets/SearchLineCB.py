from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from ..my_widgets.SearchLine import SearchLine


class TBSearch(SearchLine):
    signal_press_enter = QtCore.pyqtSignal(str)

    def __init__(self, parent, default_text: str, *args, **kwargs):
        super().__init__(parent, default_text)

        # self.tb_inti()

    # def tb_inti(self) -> None:
    #     self.btn_enter = QtWidgets.QPushButton(self.frame)
    #     self.btn_enter.setMaximumSize(self.height , self.height )
    #     self.btn_enter.setStyleSheet(u"QPushButton {\n"
    #                                     "	background-color: rgb(255, 255, 255);\n"
    #                                     "	border-top: 1px solid black; \n"
    #                                     "	border-right: 1px solid black; \n"
    #                                     "	border-bottom: 1px solid black; \n"
    #                                     "	border-top-right-radius: 3px;\n"
    #                                     "	border-bottom-right-radius: 3px;\n"
    #                                     "}\n"
    #                                     "\n"
    #                                     "QPushButton:hover {\n"
    #                                     "	background-color: rgb(240, 240, 240);\n"
    #                                     "}\n"
    #                                     "QPushButton:pressed {\n"
    #                                     "	background-color: rgb(230, 230, 230);\n"
    #                                     "}")
    #     icon1 = QtGui.QIcon()
    #     icon1.addFile(u"E:/Piton/AlfaServis/v4/resources/icons/enter_ico_2.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    #     self.btn_enter.setIcon(icon1)
    #     self.btn_enter.clicked.connect(self.pressed_enter_btn)
    #     self.horizontalLayout.addWidget(self.btn_enter)
    #
    # def pressed_enter_btn(self, event) -> None:
    #     self.signal_press_enter.emit(self.lineEdit.text())
    #
    # def pressed_enter_lineedit(self, text: str) -> None:
    #     if text:
    #         self.signal_press_enter.emit(text)