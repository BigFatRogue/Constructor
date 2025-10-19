import os

from PyQt5 import QtCore, QtGui, QtWidgets, Qt


class MyLineEditSearch(QtWidgets.QLineEdit):
    signal_press_enter = QtCore.pyqtSignal(str)
    signal_enter_text = QtCore.pyqtSignal(str)

    def __init__(self, parent, default_text, *args, **kwargs):
        super().__init__(parent)

        self.default_text = default_text
        self.setText(self.default_text)

    def set_state_default(self):
        self.setText(self.default_text)
        self.setStyleSheet(u"QLineEdit {\n"
                           "border: 0px;\n"
                           "border-top: 1px solid black;\n"
                           "border-bottom: 1px solid black;\n"
                           "color: gray;}")

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super(MyLineEditSearch, self).mousePressEvent(event)

        if self.text() == self.default_text:
            self.clear()
            self.setStyleSheet(u"QLineEdit {\n"
                               "border: 0px;\n"
                               "border-top: 1px solid black;\n"
                               "border-bottom: 1px solid black;\n"
                               "color: black;}")

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        super(MyLineEditSearch, self).focusOutEvent(event)
        if not self.text():
            self.set_state_default()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super(MyLineEditSearch, self).keyPressEvent(event)
        if event.key() == 16777220:
            self.signal_press_enter.emit(self.text())

        self.signal_enter_text.emit(self.text())


class SearchLine(QtWidgets.QWidget):
    signal_enter_text = QtCore.pyqtSignal(str)
    signal_event_clear = QtCore.pyqtSignal(bool)

    def __init__(self, parent, default_text: str = 'Поиск', height: int = 20, *args, **kwargs):
        super().__init__(parent)
        self.icon_folder = f'{os.getcwd()}\\src\\resources\\icons'
        self.default_text = default_text
        self.height = height
        self.btn_clear_dct_sh = {
                               'not_active': """QPushButton {
                               background-color: rgb(255, 255, 255);
                               border-bottom: 1px solid black;
                               border-top-right-radius: 3px;
                               border-bottom-right-radius: 3px;
                               border-top: 1px solid black; 
                               border-right: 1px solid black;}""",

                               'active': """QPushButton {
                               background-color: rgb(255, 255, 255);
                               border-top: 1px solid black; 
                               border-right: 1px solid black; 
                               border-bottom: 1px solid black; 
                               border-top-right-radius: 3px;
                               border-bottom-right-radius: 3px;}
                               
                               QPushButton:hover {
                               background-color: rgb(240, 240, 240);}
                               
                               QPushButton:pressed {
                               background-color: rgb(230, 230, 230);}"""}


        self.init()

    def init(self) -> None:
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setMaximumSize(16777215, self.height )

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(self.frame)
        self.label.setMinimumSize(self.height , self.height )
        self.label.setMaximumSize(self.height , self.height )
        self.label.setStyleSheet(u"QLabel {\n"
                                        "	background-color: rgb(255, 255, 255);\n"
                                        "	border-top: 1px solid black; \n"
                                        "	border-left: 1px solid black; \n"
                                        "	border-bottom: 1px solid black; \n"
                                        "	border-top-left-radius: 3px;\n"
                                        "	border-bottom-left-radius: 3px;\n"
                                        "}")
        self.label.setPixmap(QtGui.QPixmap(f"{self.icon_folder}/search_ico.png"))
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.horizontalLayout.addWidget(self.label)

        self.lineEdit = MyLineEditSearch(parent=self.frame, default_text=self.default_text)
        self.lineEdit.setMaximumSize(16777215, self.height )
        self.lineEdit.setStyleSheet(u"QLineEdit {\n"
                                    "border: 0px;\n"
                                    "border-top: 1px solid black;\n"
                                    "border-bottom: 1px solid black;\n"
                                    "color: gray;}")
        self.lineEdit.signal_enter_text.connect(self.enter_text)
        self.horizontalLayout.addWidget(self.lineEdit)

        self.btn_clear = QtWidgets.QPushButton(self.frame)
        self.btn_clear.setMaximumSize(self.height , self.height)
        self.btn_clear.setStyleSheet(self.btn_clear_dct_sh['not_active'])

        self.icon_clear = QtGui.QIcon()
        self.icon_clear.addFile(f"{self.icon_folder}/clear_ico.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_clear.setIcon(QtGui.QIcon())
        self.btn_clear.clicked.connect(self.clear_lineedit)
        self.horizontalLayout.addWidget(self.btn_clear)

        self.verticalLayout.addWidget(self.frame)

    def enter_text(self, text: str):
        if text and text != self.default_text:
            self.btn_clear.setIcon(self.icon_clear)
            self.btn_clear.setStyleSheet(self.btn_clear_dct_sh['active'])
        else:
            self.btn_clear.setIcon(QtGui.QIcon())
            self.btn_clear.setStyleSheet(self.btn_clear_dct_sh['not_active'])

        self.signal_enter_text.emit(text)

    def clear_lineedit(self):
        self.lineEdit.clear()
        self.btn_clear.setIcon(QtGui.QIcon())
        self.lineEdit.set_state_default()
        self.btn_clear.setStyleSheet(self.btn_clear_dct_sh['not_active'])
        self.signal_event_clear.emit(True)