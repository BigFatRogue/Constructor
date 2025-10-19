import sys
import ctypes
from PyQt5 import QtCore, QtGui, QtWidgets


class InitCustomWindow(QtWidgets.QFrame):
    def __init__(self, main_window: QtWidgets.QMainWindow, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._old_coord = None
        self.main_window: QtWidgets.QMainWindow = main_window

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self._old_coord = event.globalPos()


class TitleBar(InitCustomWindow):
    def __init__(self, main_window, parent, icon_folder, *args, **kwargs):
        super().__init__(main_window, parent, *args, **kwargs)
        self.folder_icon = icon_folder

        file = QtCore.QFile(r'styleQSS/styleCustomWindow.css')
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        self.setStyleSheet(stream.readAll())

        self.setMinimumSize(QtCore.QSize(0, 20))
        self.setMaximumSize(QtCore.QSize(16777215, 20))
        # self.setStyleSheet("QFrame {\n"
        #                             "    background-color: rgb(46, 52, 64);\n"
        #                             "}")
        # self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setObjectName("TitleBar")
        #-----------------------------------------------------------------------------#
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 5, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        # ---------------------------------------------------------------------------#
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        # ---------------------------------------------------------------------------#
        self.minimazeButton = QtWidgets.QPushButton(self)
        self.minimazeButton.setMinimumSize(QtCore.QSize(0, 0))
        self.minimazeButton.setMaximumSize(QtCore.QSize(20, 18))
        # self.minimazeButton.setStyleSheet("QPushButton {background-color: rgba(255, 255, 255, 0);}\n"
        #                                   "QPushButton::hover {background-color: rgb(17, 19, 24);}")
        self.minimazeButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(f"{self.folder_icon}/icon_minimaze.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minimazeButton.setIcon(icon4)
        self.minimazeButton.setIconSize(QtCore.QSize(10, 10))
        self.minimazeButton.setObjectName("minimazeButton")
        self.minimazeButton.clicked.connect(main_window.showMinimized)
        self.horizontalLayout.addWidget(self.minimazeButton)
        # ---------------------------------------------------------------------------#
        self.closeButton = QtWidgets.QPushButton(self)
        self.closeButton.setMinimumSize(QtCore.QSize(0, 0))
        self.closeButton.setMaximumSize(QtCore.QSize(20, 18))
        # self.closeButton.setStyleSheet("QPushButton { background-color: rgba(255, 255, 255, 0);}\n"
        #                                "QPushButton::hover { background-color: rgb(255, 0, 0, 200);}")
        # self.closeButton.setText("")
        self.closeButton.clicked.connect(main_window.close)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(f"{self.folder_icon}/icon_close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeButton.setIcon(icon5)
        self.closeButton.setIconSize(QtCore.QSize(10, 10))
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        # ---------------------------------------------------------------------------#

        self.mouseMoveEvent = self.moveWindow

    def moveWindow(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.main_window.move(self.main_window.pos() + event.globalPos() - self._old_coord)
            self._old_coord = event.globalPos()
            event.accept()


class CustomSide(InitCustomWindow):
    def __init__(self, main_window, parent, side: str, *args, **kwargs):
        super().__init__(main_window, parent, *args, **kwargs)
        self.side = side

        if self.side in ('l', 'r'):
            self.setMinimumSize(QtCore.QSize(10, 0))
            self.setMaximumSize(QtCore.QSize(10, 16777215))
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
        elif self.side == 'd':
            self.setMinimumSize(QtCore.QSize(0, 10))
            self.setMaximumSize(QtCore.QSize(16777215, 10))
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
        elif self.side == 'ld':
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))
        elif self.side == 'rd':
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        elif self.side == 'lu':
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        elif self.side == 'ru':
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))

        # self.setStyleSheet("QFrame { background-color: rgb(46, 52, 64); }")
        # self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setObjectName(f"{self.side}Size")

        self.mouseMoveEvent = self._resize_window

    def _resize_window(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.LeftButton:
            geometry = self.main_window.geometry()
            x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
            dx = event.globalPos().x()
            dy = event.globalPos().y()
            dw = self._old_coord.x() - dx
            dh = self._old_coord.y() - dy

            if self.side == 'l':
                new_geometry = dx, y, w + dw, h

            elif self.side == 'd':
                new_geometry = x, y, w, h - dh

            elif self.side == 'r':
                new_geometry = x, y, w - dw, h

            elif self.side == 'ld':
                new_geometry = dx, y, w + dw, h - dh

            elif self.side == 'rd':
                new_geometry = x, y, w - dw, h - dh

            elif self.side == 'lu':
                new_geometry = dx, dy, w + dw, h + dh

            else:
                new_geometry = x, dy, w - dw, h + dh

            self._old_coord = event.globalPos()

            min_size = self.main_window.minimumSize()
            min_w, min_h = min_size.width(), min_size.height()

            if w + dw >= min_w or h + dh >= min_h:
                try:
                    self.main_window.setGeometry(*new_geometry)
                except Exception:
                    ...

        event.accept()


class CustomWindow(QtWidgets.QMainWindow):
    def __init__(self, folder_icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder_icon = folder_icon

        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(f"{self.folder_icon}/icon.ico"))

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.setObjectName("MainWindow")
        self.resize(1000, 500)

        file = QtCore.QFile(r'css/window.css')
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        self.setStyleSheet(stream.readAll())

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        # ---------------------------------------------------------------------------#
        self.gridLayoutCentral = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayoutCentral.setContentsMargins(0, 0, 0, 0)
        self.gridLayoutCentral.setObjectName("gridLayoutCentral")
        # ---------------------------------------------------------------------------#
        self.MainFrame = QtWidgets.QFrame(self.centralwidget)
        # self.MainFrame.setStyleSheet("QFrame {background-color: rgb(59, 68, 83);}")
        self.MainFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.MainFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.MainFrame.setObjectName("MainFrame")
        # ---------------------------------------------------------------------------#
        self.gridLayoutMainFrame = QtWidgets.QGridLayout(self.MainFrame)
        self.gridLayoutMainFrame.setContentsMargins(0, 0, 0, 0)
        self.gridLayoutMainFrame.setSpacing(0)
        self.gridLayoutMainFrame.setObjectName("gridLayoutMainFrame")
        # ---------------------------------------------------------------------------#
        self.ContentFrame = QtWidgets.QFrame(self.MainFrame)
        self.ContentFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ContentFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ContentFrame.setObjectName("ContentFrame")
        # ---------------------------------------------------------------------------#
        self.__init__side()

        self.gridLayoutMainFrame.addWidget(self.ContentFrame, 2, 1, 1, 1)
        self.gridLayoutCentral.addWidget(self.MainFrame, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)

    def __init__side(self):
        self.TitleBar = TitleBar(main_window=self, parent=self.MainFrame, icon_folder=self.folder_icon)
        # ---------------------------------------------------------------------------#
        self.gridLayoutMainFrame.addWidget(self.TitleBar, 1, 1, 1, 1)
        # ---------------------------------------------------------------------------#
        self.RDFrame = CustomSide(main_window=self, parent=self.MainFrame, side='rd')
        self.gridLayoutMainFrame.addWidget(self.RDFrame, 5, 2, 1, 1)
        # ---------------------------------------------------------------------------#
        self.DownSize = CustomSide(main_window=self, parent=self.MainFrame, side='d')
        self.gridLayoutMainFrame.addWidget(self.DownSize, 5, 1, 1, 1)
        # ---------------------------------------------------------------------------#
        self.URFrame = CustomSide(main_window=self, parent=self.MainFrame, side='ru')
        self.gridLayoutMainFrame.addWidget(self.URFrame, 1, 2, 1, 1)
        # ---------------------------------------------------------------------------#
        self.LUFrame = CustomSide(main_window=self, parent=self.MainFrame, side='lu')
        self.gridLayoutMainFrame.addWidget(self.LUFrame, 1, 0, 1, 1)
        # ---------------------------------------------------------------------------#
        self.RightSize = CustomSide(main_window=self, parent=self.MainFrame, side='r')
        self.gridLayoutMainFrame.addWidget(self.RightSize, 2, 2, 1, 1)
        # ---------------------------------------------------------------------------#
        self.LeftSize = CustomSide(main_window=self, parent=self.MainFrame, side='l')
        self.gridLayoutMainFrame.addWidget(self.LeftSize, 2, 0, 1, 1)
        # ---------------------------------------------------------------------------#
        self.LDFrame = CustomSide(main_window=self, parent=self.MainFrame, side='ld')
        self.gridLayoutMainFrame.addWidget(self.LDFrame, 5, 0, 1, 1)


class Window(CustomWindow):
    def __init__(self, folder_icon, *args,  **kwargs):
        super().__init__(folder_icon, *args,  **kwargs)

        # file = QtCore.QFile(r'styleQSS/styleCustomWindow.css')
        # file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        # stream = QtCore.QTextStream(file)
        # self.setStyleSheet(stream.readAll())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = Window(folder_icon=r'application\icon')
    window.show()
    sys.exit(app.exec_())


