import sys
import os 
from enum import Enum, auto
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


class TypeRectSize(Enum):
    LT = auto()
    CT = auto()
    RT = auto()
    LC = auto()
    CC = auto()
    RC = auto()
    LB = auto()
    CB = auto()
    RB = auto()


class RectSetSizeCapture(QtWidgets.QFrame):
    signal_press = QtCore.pyqtSignal(TypeRectSize)
    signal_release = QtCore.pyqtSignal()

    def __init__(self, parent, tp: TypeRectSize):
        super().__init__(parent)

        self.tp = tp
        self.wh_size = 10
        self.__init_style()
        self.__init_size()

    def __init_size(self) -> None:
        if self.tp in (TypeRectSize.LT, TypeRectSize.RT, TypeRectSize.LB, TypeRectSize.RB):
            self.setMinimumSize(self.wh_size, self.wh_size)
            self.setMaximumSize(self.wh_size, self.wh_size)
        elif self.tp in (TypeRectSize.CT, TypeRectSize.CB):
            self.setMinimumHeight(self.wh_size)
            self.setMaximumHeight(self.wh_size)
        elif self.tp in (TypeRectSize.LC, TypeRectSize.RC):
            self.setMinimumWidth(self.wh_size)
            self.setMaximumWidth(self.wh_size)

    def __init_style(self) -> None:
        if self.tp in (TypeRectSize.LT, TypeRectSize.RB):
            self.setStyleSheet('RectSetSizeCapture {background-color: black;}')
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif self.tp in (TypeRectSize.RT, TypeRectSize.LB):
            self.setStyleSheet('RectSetSizeCapture {background-color: black;}')
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
        elif self.tp in (TypeRectSize.CT, TypeRectSize.CB):
            self.setCursor(QtCore.Qt.SizeVerCursor)
        elif self.tp in (TypeRectSize.LC, TypeRectSize.RC):
            self.setCursor(QtCore.Qt.SizeHorCursor)
        elif self.tp == TypeRectSize.CC:
            # self.setStyleSheet('RectSetSizeCapture {border: 1px solid black}')
            self.setCursor(QtCore.Qt.SizeAllCursor)
    
    def mousePressEvent(self, event):
        self.signal_press.emit(self.tp)
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.signal_release.emit()
        return super().mouseReleaseEvent(event)


class FrameCaptureVideo(QtWidgets.QFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.is_draw = False
        self.is_press_rect_size = False
        self.tp_press_rect_size = None
        self.left_top = QtCore.QPoint(0, 0)
        self.right_bottom = QtCore.QPoint(0, 0)
        self.x0, self.y0, self.x1, self.y1 = 50, 50, 100, 100
        self.x0_old, self.y0_old, self.x1_old, self.y1_old = 0, 0, 0, 0 
        self.capture_rect = QtCore.QRect()

        self.old_pos = QtCore.QPoint()

        self.setMouseTracking(True)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.v_layout)
        self.setGeometry(self.parent().rect())
        self.setStyleSheet("FrameCaptureVideo {background-color: rgba(100, 100, 100, 0)")

        self.frame_capture_rect = QtWidgets.QFrame(self)
        self.frame_capture_rect.setObjectName('frame_capture_rect')
        self.frame_capture_rect.setStyleSheet('#frame_capture_rect {border: 1px solid black}')
        self.frame_capture_rect.setGeometry(self.x0, self.y0, abs(self.x0 - self.x1), abs(self.y0 - self.y1))
        self.v_layout.addWidget(self.frame_capture_rect)

        self.grid_frame_capture_rect = QtWidgets.QGridLayout(self.frame_capture_rect)
        self.grid_frame_capture_rect.setSpacing(0)
        self.grid_frame_capture_rect.setContentsMargins(0, 0, 0, 0)

        self.__init_frame_capture_rect()

    def __init_frame_capture_rect(self) -> None:
        self.ltr = RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.LT)
        self.ctr = RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.CT)
        self.rtr = RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.RT)
        self.lcr = RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.LC)
        self.cc = RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.CC)
        self.rcr = RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.RC)
        self.lbr= RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.LB)
        self.cbr = RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.CB)
        self.rbr = RectSetSizeCapture(self.frame_capture_rect, tp=TypeRectSize.RB)

        self.grid_frame_capture_rect.addWidget(self.ltr, 0, 0, 1, 1)
        self.grid_frame_capture_rect.addWidget(self.ctr, 0, 1, 1, 1)
        self.grid_frame_capture_rect.addWidget(self.rtr, 0, 2, 1, 1)
        self.grid_frame_capture_rect.addWidget(self.lcr, 1, 0, 1, 1)
        self.grid_frame_capture_rect.addWidget(self.cc, 1, 1, 1, 1)
        self.grid_frame_capture_rect.addWidget(self.rcr, 1, 2, 1, 1)
        self.grid_frame_capture_rect.addWidget(self.lbr, 2, 0, 1, 1)
        self.grid_frame_capture_rect.addWidget(self.cbr, 2, 1, 1, 1)
        self.grid_frame_capture_rect.addWidget(self.rbr, 2, 2, 1, 1)

        for rect_size in (self.ltr, self.ctr, self.rtr, self.lcr, self.cc, self.rcr, self.lbr, self.cbr, self.rbr):
            rect_size.signal_press.connect(self.press_rect_size)
            rect_size.signal_release.connect(self.release_rect_size)
    
    def get_rect(self) -> QtCore.QRect:
        wh_size = self.cc.wh_size
        return QtCore.QRect(self.x0 , self.y0 , abs(self.x0 - self.x1), abs(self.y0 - self.y1))

    def press_rect_size(self, tp) -> None:
        self.is_press_rect_size = True
        self.tp_press_rect_size = tp
    
    def release_rect_size(self) -> None:
        self.is_press_rect_size = False

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self.is_draw = True
        self.old_pos  = event.pos()
        self.x0_old, self.y0_old, self.x1_old, self.y1_old = self.x0, self.y0, self.x1, self.y1
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.is_draw = False
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.is_press_rect_size:
            x, y = event.pos().x(), event.pos().y()
            limit_left = -self.cc.wh_size
            limit_rigth = self.parent().geometry().width() + self.cc.wh_size
            limit_top = -self.cc.wh_size
            limit_bottom = self.parent().geometry().height() + self.cc.wh_size
            
            if x < limit_left or x > limit_rigth or y < limit_top or x > limit_bottom:
                return
            if self.tp_press_rect_size == TypeRectSize.LT:
                self.x0, self.y0 = x, y
            elif self.tp_press_rect_size == TypeRectSize.CT:
                self.y0 = y
            elif self.tp_press_rect_size == TypeRectSize.RT:
                self.x1, self.y0 = x, y
            elif self.tp_press_rect_size == TypeRectSize.LC:
                self.x0 = x
            elif self.tp_press_rect_size == TypeRectSize.CC:
                dxy = event.pos() - self.old_pos
                dx, dy = dxy.x(), dxy.y()
                if not self.x0_old + dx < limit_left and not self.x1_old + dx > limit_rigth:
                    self.x0 = self.x0_old + dx
                    self.x1 = self.x1_old + dx
                if not self.y0_old + dy < limit_top and not self.y1_old + dy > limit_bottom:
                    self.y0 = self.y0_old + dy
                    self.y1 = self.y1_old + dy
            elif self.tp_press_rect_size == TypeRectSize.RC:
                self.x1 = x
            elif self.tp_press_rect_size == TypeRectSize.LB:
                self.x0, self.y1 = x, y
            elif self.tp_press_rect_size == TypeRectSize.CB:
                self.y1 = y
            elif self.tp_press_rect_size == TypeRectSize.RB:
                self.x1, self.y1 = x, y
            self.draw_rect()
        return super().mouseMoveEvent(event)
    
    def draw_rect(self) -> None:
        if self.is_draw:
            self.capture_rect = QtCore.QRect(self.x0 , self.y0 , abs(self.x0 - self.x1) , abs(self.y0 - self.y1) )
            self.frame_capture_rect.setGeometry(self.capture_rect)


class MarkerSlider(QtWidgets.QSlider):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setStyleSheet('MarkerSlider:groove {border: 1px solid black; border-radius: 2px}')
        self.curren_x = 0
        self.width_groove = 10
        self.is_click_groove = False
        
    def setValue(self, value):
        self.curren_x = int(value / self.maximum() * self.width())
        return super().setValue(value)

    def paintEvent(self, event):
        super().paintEvent(event)
        # curren_x = int(self.value() / self.maximum() * self.width())

        if self.curren_x:
            painter = QtGui.QPainter(self)
            pen = QtGui.QPen(QtCore.Qt.black, self.width_groove, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(self.curren_x, 0, self.curren_x, self.height())
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        x = event.pos().x()

        if self.curren_x - self.width_groove < x < self.curren_x + self.width_groove:
            self.is_click_groove = True
        else:
            self.curren_x = x
            value = int(self.curren_x / self.width() * self.maximum())
            self.setValue(value)
            self.sliderMoved.emit(value)
        event.ignore()
        # return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self.is_click_groove = False
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.is_click_groove:
            x = event.pos().x()
            if x > self.width_groove / 2 and x < self.width() - self.width_groove / 2:
                self.curren_x = event.pos().x()
                value = int(self.curren_x / self.width() * self.maximum())
                self.sliderMoved.emit(value)
                self.update()
        return super().mouseMoveEvent(event)


class WidgetMp4ToGif(QtWidgets.QWidget): 
    def __init__(self, parent=None, app=None):
        super().__init__(parent)

        self.app = app
        self.is_recording = False
        self.current_frame = 0
        self.count_frame = 0
        self.is_play = False
        self.frames = []
        self.fps = 20

        self.__init_window()
        self.__init_widgets()

        self.__run_application()

        self.__init_recorder()
        self.__init_player()
        self.__init_capture_video()
        self.start_draw_capture_rect()

    def __init_window(self) -> None:
        self.resize(650, 320)
        self.setWindowTitle('mp4 to gif')
        
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setObjectName("gridLayoutCentral")

    def __init_widgets(self) -> None:
        self.label_video = QtWidgets.QLabel(self)
        self.label_video.setText('Укажите область захвата')
        self.label_video.setAlignment(QtCore.Qt.AlignCenter)
        self.grid_layout.addWidget(self.label_video, 0, 0, 1, 5)

        self.h_line_separate = QHLineSeparate(self)
        self.grid_layout.addWidget(self.h_line_separate, 1, 0, 1, 5)
        
        self.btn_play = QtWidgets.QPushButton("▶️")
        self.btn_play.setMaximumWidth(50)
        self.btn_play.clicked.connect(self.start_play)
        self.grid_layout.addWidget(self.btn_play, 2, 0, 1, 1)

        self.btn_select_rect = QtWidgets.QPushButton("[..]")
        self.btn_select_rect.setMaximumWidth(50)
        # self.btn_select_rect.clicked.connect(self.start_draw_capture_rect)
        self.grid_layout.addWidget(self.btn_select_rect, 2, 1, 1, 1)

        self.btn_rec = QtWidgets.QPushButton("🔴")
        self.btn_rec.setObjectName('btn_rec')
        self.btn_rec.setMaximumWidth(25)
        self.btn_rec.clicked.connect(self.start_recording)
        self.grid_layout.addWidget(self.btn_rec, 2, 2, 1, 1)

        self.slider = MarkerSlider(parent=self, orientation=QtCore.Qt.Horizontal)
        self.slider.sliderMoved.connect(self.slider_moved)
        # self.slider.setEnabled(False)
        self.grid_layout.addWidget(self.slider, 2, 3, 1, 1)

        self.label_time = QtWidgets.QLabel(self)
        self.set_time_label()
        self.label_time.setAlignment(QtCore.Qt.AlignRight)
        self.grid_layout.addWidget(self.label_time, 2, 4, 1, 1)
        

    def __init_capture_video(self):
        self.frame_capture_video = FrameCaptureVideo(self.app)
        self.app.layout().addWidget(self.frame_capture_video)
        self.frame_capture_video.hide()
        self.desable_event_widgets(self.app)

    def __init_recorder(self) -> None:
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.capture_frame)
        self.timer.start(1000 // self.fps)

    def __init_player(self) -> None:
        self.playback_timer = QtCore.QTimer()
        self.playback_timer.timeout.connect(self.show_next_frame)
    
    def desable_event_widgets(self, parent=None) -> None:
        if parent is None:
            parent = self.parent
        for child in parent.children():
            if child == self.frame_capture_video:
                continue
            if hasattr(child, 'setAttribute'):
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            self.desable_event_widgets(child) 

    def enable_event_widgets(self, parent=None) -> None:
        if parent is None:
            parent = self.parent
        for child in parent.children():
            if child == self.frame_capture_video:
                continue
            if hasattr(child, 'setAttribute'):
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
            self.enable_event_widgets(child) 

    def set_time_label(self) -> None:
        self.label_time.setText(f'{self.current_frame // self.fps:02}:{self.current_frame % self.fps:02} / {self.count_frame // self.fps:02}:{self.count_frame % self.fps:02}')

    def start_draw_capture_rect(self) -> None:
        self.frame_capture_video.show()

    def start_recording(self) -> None:
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.frames.clear()
            self.current_frame = 0
            self.count_frame = 0
            self.btn_rec.setStyleSheet('#btn_rec {border: 2px solid black}')
            self.enable_event_widgets(self.app)
            self.frame_capture_video.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            self.slider.setEnabled(False)
        else:
            self.btn_rec.setStyleSheet('#btn_rec {border: 1px solid black}')
            self.frame_capture_video.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
            self.slider.setMaximum(self.count_frame)
            self.slider.setEnabled(True)
            self.set_time_label()
    
    def capture_frame(self):
        if not self.is_play:
            self.frame_capture_video.hide()
            rect = self.frame_capture_video.get_rect().getRect()
            pixmap = self.app.screen().grabWindow(self.app.winId(), *rect)
            
            self.draw_cursor(pixmap)
            qimage = pixmap.toImage()
            pixmap = QtGui.QPixmap.fromImage(qimage)
            
            self.label_video.setPixmap(pixmap)
            self.frame_capture_video.show()
            if self.is_recording:
                self.count_frame += 1
                self.frames.append(qimage)
                self.set_time_label()

    def draw_cursor(self, pixmap) -> None:
        cursor_pos = QtGui.QCursor.pos()
        app_pos = self.app.mapToGlobal(QtCore.QPoint(0, 0))

        capture_rect = self.frame_capture_video.get_rect()
        pos_x = cursor_pos.x() - app_pos.x() - capture_rect.x()
        pos_y = cursor_pos.y() - app_pos.y() - capture_rect.y()

        painter = QtGui.QPainter(pixmap)

        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.white)
        r = 2
        painter.drawEllipse(pos_x - r, pos_y - r, r * 2, r * 2)
                
        painter.end()

    def start_play(self) -> None:
        self.is_play = not self.is_play
        if self.is_play and self.frames:
            self.btn_play.setText('⏸️')
            self.playback_timer.start(1000 // self.fps)
        else:
            self.btn_play.setText('▶️')

        self.show_current_frame()
    
    def slider_moved(self, pos) -> None:
        self.current_frame = pos
        self.show_current_frame()

    def show_next_frame(self):
        if self.is_play:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.current_frame = 0 
                self.is_play = not self.is_play
            self.show_current_frame()
        else:
            self.btn_play.setText('▶️')

    def show_current_frame(self) -> None:
        if self.current_frame < len(self.frames):
            self.label_video.setPixmap(QtGui.QPixmap.fromImage(self.frames[self.current_frame]))
            self.slider.setValue(self.current_frame)
            self.set_time_label()

    def __run_application(self) -> None:
        self.app = TempWindow(self)
        self.app.show()

    def showEvent(self, a0):
        geom = self.geometry()
        self.app.setGeometry(geom.x() + geom.width() + 50, self.app.y(), self.app.width(), self.app.height())
        return super().showEvent(a0)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = WidgetMp4ToGif()
    player.show()
    sys.exit(app.exec_())