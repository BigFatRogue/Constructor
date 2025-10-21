import sys
import os 
from PyQt5 import QtCore, QtGui, QtWidgets


class TempWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)

        self.resize(500, 500)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setObjectName("centra_lwidget")

        self.vl = QtWidgets.QVBoxLayout(self.central_widget)
        self.initWidgets()

    def initWidgets(self) -> None:
        self.btn_1 = QtWidgets.QPushButton(self)
        self.btn_1.setObjectName('btn_choose_path_assembly')
        self.btn_1.setText('Кнопка 1') 
        self.btn_1.clicked.connect(lambda e: print('click btn 1'))
        self.vl.addWidget(self.btn_1)

        self.btn_2 = QtWidgets.QPushButton(self)
        self.btn_2.setText('Кнопка 2') 
        self.btn_2.clicked.connect(lambda e: print('click btn 2'))
        self.vl.addWidget(self.btn_2)

        self.btn_3 = QtWidgets.QPushButton(self)
        self.btn_3.setText('Помощь') 
        self.vl.addWidget(self.btn_3)
    
    def open_help(self) -> None:
        self.helper.show()


class QHLineSeparate(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class FrameCaptureVideo(QtWidgets.QFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.is_draw = False
        self.left_top = QtCore.QPoint(0, 0)
        self.right_bottom = QtCore.QPoint(0, 0)

        self.setMouseTracking(True)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.v_layout)
        self.setGeometry(self.parent().rect())
        self.setStyleSheet("FrameCaptureVideo {background-color: rgba(100, 100, 100, 100);}")

        self.label_capture_rect = QtWidgets.QLabel(self)
        self.label_capture_rect.setObjectName('label_capture_rect')
        self.label_capture_rect.setGeometry(0, 0, 50, 50)
        self.label_capture_rect.setStyleSheet("#label_capture_rect {background-color: green}")
        # self.layout().addWidget(self.label_capture_rect)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.is_draw = True
        self.left_top = event.pos()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.is_draw = False
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.is_draw:
            self.right_bottom = event.pos()
            self.draw_rect()
        return super().mouseMoveEvent(event)
    
    def draw_rect(self) -> None:
        if self.is_draw:
            print('asd')
            self.label_capture_rect.setGeometry(QtCore.QRect(self.left_top, self.right_bottom))

class MarkerSlider(QtWidgets.QSlider):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


class WidgetMp4ToGif(QtWidgets.QWidget): 
    def __init__(self, parent=None, app=None):
        super().__init__(parent)

        self.app = app

        self.initWindow()
        self.initWidgets()
        self.__run_application()
    
    def initWindow(self) -> None:
        self.resize(650, 320)
        self.setWindowTitle('mp4 to gif')
        
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setObjectName("gridLayoutCentral")

    def initWidgets(self) -> None:
        self.label_video = QtWidgets.QLabel(self)
        self.label_video.setText('Укажите область захвата')
        self.label_video.setAlignment(QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(self.label_video, 0, 0, 1, 5)

        self.h_line_separate = QHLineSeparate(self)
        self.grid_layout.addWidget(self.h_line_separate, 1, 0, 1, 5)
        
        self.btn_play = QtWidgets.QPushButton("▶️ / ⏸️")
        self.btn_play.setMaximumWidth(50)
        self.grid_layout.addWidget(self.btn_play, 2, 0, 1, 1)

        self.btn_select_rect = QtWidgets.QPushButton("[..]")
        self.btn_select_rect.setMaximumWidth(50)
        self.btn_select_rect.clicked.connect(self.draw_rect_rec)
        self.grid_layout.addWidget(self.btn_select_rect, 2, 1, 1, 1)

        self.btn_rec = QtWidgets.QPushButton("🔴")
        self.btn_rec.setMaximumWidth(25)
        self.grid_layout.addWidget(self.btn_rec, 2, 2, 1, 1)

        self.slider = MarkerSlider(parent=self, orientation=QtCore.Qt.Horizontal)
        self.grid_layout.addWidget(self.slider, 2, 3, 1, 1)

        self.label_time = QtWidgets.QLabel("00:00 / 00:00")
        self.label_time.setAlignment(QtCore.Qt.AlignRight)
        self.grid_layout.addWidget(self.label_time, 2, 4, 1, 1)

    def draw_rect_rec(self) -> None:
        self.desable_event_widgets(self.app)
        self.frame_capture_video = FrameCaptureVideo(self.app)
        self.app.layout().addWidget(self.frame_capture_video)
        self.frame_capture_video.label_capture_rect.setText('Захват экрана')
        # self.frame_capture_video.setGeometry(50, 50, 100, 100)
        # print(self.frame_capture_video.parent())

    def desable_event_widgets(self, parent=None) -> None:
        if parent is None:
            parent = self.parent
        for child in parent.children():
            if hasattr(child, 'setAttribute'):
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            self.enable_event_widgets(child) 

    def enable_event_widgets(self, parent=None) -> None:
        if parent is None:
            parent = self.parent
        for child in parent.children():
            if hasattr(child, 'setAttribute'):
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
            self.enable_event_widgets(child) 

    def __run_application(self) -> None:
        self.app = TempWindow(self)
        self.app.show()


    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = WidgetMp4ToGif()
    player.show()
    sys.exit(app.exec_())