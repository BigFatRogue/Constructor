import sys
import os
import ctypes
from PyQt5 import QtCore, QtGui, QtWidgets


class InitCustomWindow(QtWidgets.QFrame):
    def __init__(self, main_window: QtWidgets.QMainWindow, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._old_coord = None
        self.main_window: QtWidgets.QMainWindow = main_window

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self._old_coord = event.globalPos()


class CustomTitleBar(InitCustomWindow):
    def __init__(self, main_window, parent, h: int, resources, *args, **kwargs):
        super().__init__(main_window, parent, *args, **kwargs)
        self.resources = resources

        self.setMinimumSize(QtCore.QSize(0, h))
        self.setMaximumSize(QtCore.QSize(16777215, h))
        self.setStyleSheet("QFrame { background-color: rgb(46, 52, 64); }")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 5, 0)
        self.horizontalLayout.setSpacing(0)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.minimazeButton = QtWidgets.QPushButton(self)
        self.minimazeButton.setMinimumSize(QtCore.QSize(0, 0))
        self.minimazeButton.setMaximumSize(QtCore.QSize(20, 18))
        self.minimazeButton.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(f"{self.resources}/icons/icon_minimaze.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minimazeButton.setIcon(icon4)
        self.minimazeButton.setIconSize(QtCore.QSize(10, 10))
        self.minimazeButton.setObjectName("minimazeButton")
        self.minimazeButton.setStyleSheet("""
        #minimazeButton {background-color: rgba(255, 255, 255, 0);}
        #minimazeButton:hover {background-color: rgb(17, 19, 24);}
        """)
        self.minimazeButton.clicked.connect(main_window.showMinimized)
        self.horizontalLayout.addWidget(self.minimazeButton)
        # ---------------------------------------------------------------------------#
        self.closeButton = QtWidgets.QPushButton(self)
        self.closeButton.setMinimumSize(QtCore.QSize(0, 0))
        self.closeButton.setMaximumSize(QtCore.QSize(20, 18))
        self.closeButton.clicked.connect(main_window.close)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(f"{self.resources}/icons/icon_close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeButton.setIcon(icon5)
        self.closeButton.setIconSize(QtCore.QSize(10, 10))
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setStyleSheet("""
        #closeButton {background-color: rgba(255, 255, 255, 0);}
        #closeButton:hover {background-color: rgb(255, 0, 0, 200);}
        """)
        self.horizontalLayout.addWidget(self.closeButton)

        self.mouseMoveEvent = self.moveWindow

    def moveWindow(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.main_window.move(self.main_window.pos() + event.globalPos() - self._old_coord)
            self._old_coord = event.globalPos()
            event.accept()


class CustomSide(InitCustomWindow):
    def __init__(self, main_window, parent, side: str, w: int, h: int, *args, **kwargs):
        super().__init__(main_window, parent, *args, **kwargs)
        self.side = side

        if self.side in ('l', 'r'):
            self.setMinimumSize(QtCore.QSize(w, h))
            self.setMaximumSize(QtCore.QSize(w, 16777215))
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
        elif self.side in ('d', 'u'):
            self.setMinimumSize(QtCore.QSize(w, h))
            self.setMaximumSize(QtCore.QSize(16777215, h))
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeVerCursor))
        elif self.side == 'ld':
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))
        elif self.side == 'rd':
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        elif self.side == 'lu':
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeFDiagCursor))
        elif self.side == 'ru':
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeBDiagCursor))

        if self.side in ('ld', 'rd', 'lu', 'ru'):
            self.setMinimumSize(QtCore.QSize(w, h))
            self.setMaximumSize(QtCore.QSize(w, h))

        self.setStyleSheet("QFrame { background-color: rgb(46, 52, 64); }")

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

            elif self.side == 'u':
                new_geometry = x, dy, w, h + dh

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
    def __init__(self, resources, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resources = resources

        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(f"{self.resources}/logo.ico"))
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

        self.resize(550, 300)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.gridLayoutCentral = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayoutCentral.setContentsMargins(0, 0, 0, 0)
        self.gridLayoutCentral.setSpacing(0)

        self.__init__side()

    def __init__side(self):
        h_tb = 20
        w, h = 10, 10
        k_h = 7
        # ---------------------------------------------------------------------------#
        self.LUFrame = CustomSide(main_window=self, parent=self, side='lu', w=w, h=h + h_tb-k_h)
        self.gridLayoutCentral.addWidget(self.LUFrame, 0, 0, 2, 1)
        # ---------------------------------------------------------------------------#
        self.UPFrame = CustomSide(main_window=self, parent=self, side='u', w=w, h=h-k_h)
        self.gridLayoutCentral.addWidget(self.UPFrame, 0, 1, 1, 1)
        # ---------------------------------------------------------------------------#
        self.TitleBar = CustomTitleBar(main_window=self, parent=self, resources=self.resources, h=h_tb)
        self.gridLayoutCentral.addWidget(self.TitleBar, 1, 1, 1, 1)
        #---------------------------------------------------------------------------#
        self.URFrame = CustomSide(main_window=self, parent=self, side='ru', w=w, h=h + h_tb-k_h)
        self.gridLayoutCentral.addWidget(self.URFrame, 0, 2, 2, 1)
        # ---------------------------------------------------------------------------#
        self.LeftSize = CustomSide(main_window=self, parent=self, side='l', w=w, h=h)
        self.gridLayoutCentral.addWidget(self.LeftSize, 2, 0, 1, 1)
        #---------------------------------------------------------------------------#
        self.ContentFrame = QtWidgets.QFrame(self)
        self.ContentFrame.setObjectName('ContentFrame')
        self.ContentFrame.setStyleSheet('#ContentFrame {background-color:  rgb(59, 68, 83)}')
        self.gridLayoutCentral.addWidget(self.ContentFrame, 2, 1, 1, 1)
        # ---------------------------------------------------------------------------#
        self.RightSize = CustomSide(main_window=self, parent=self, side='r', w=w, h=h)
        self.gridLayoutCentral.addWidget(self.RightSize, 2, 2, 1, 1)
        #---------------------------------------------------------------------------#
        self.RDFrame = CustomSide(main_window=self, parent=self, side='rd', w=w, h=h)
        self.gridLayoutCentral.addWidget(self.RDFrame, 4, 2, 1, 1)
        # ---------------------------------------------------------------------------#
        self.DownSize = CustomSide(main_window=self, parent=self, side='d', w=w, h=h)
        self.gridLayoutCentral.addWidget(self.DownSize, 4, 1, 1, 1)
        # ---------------------------------------------------------------------------#
        self.LDFrame = CustomSide(main_window=self, parent=self, side='ld', w=w, h=h)
        self.gridLayoutCentral.addWidget(self.LDFrame, 4, 0, 1, 1)


class Window(CustomWindow):
    def __init__(self, resources, *args,  **kwargs):
        super().__init__(resources, *args,  **kwargs)

        self.gridContentLayout = QtWidgets.QGridLayout(self.ContentFrame)

        self.btn = QtWidgets.QPushButton(self.ContentFrame)
        self.gridContentLayout.addWidget(self.btn)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    r = '\\'.join(os.getcwd().split('\\')[:-1]) + '\\resources'
    window = Window(resources=r)
    window.show()
    sys.exit(app.exec_())


