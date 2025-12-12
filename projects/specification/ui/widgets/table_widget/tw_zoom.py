import os
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.app_context.app_context import SETTING, SIGNAL_BUS, ENUMS, CONSTANTS

from projects.specification.ui.widgets.table_widget.tw_table import Table, HeaderWithOverlayWidgets, TableItem
from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button


class CustomSlider(QtWidgets.QSlider):
    def __init__(self, perent, min_value=10, step=5):
        super().__init__(perent)

        self.setStyleSheet('MarkerSlider:groove {border: 1px solid white; background-color: white}')
        self.min_value = min_value
        self.step = step
        self.steps = [i for i in range(min_value, 100 + step, step)]
        self.steps_x = None

        self.curren_x = 0
        self.width_groove = 6
        self.width_line = 2
        self.is_click_groove = False

    def __genarate_steps_x(self) -> list[int]:
        return [int(step * self.width() / 100)  for step in self.steps]

    def paintEvent(self, event):
        if self.steps_x is None:
            self.steps_x = self.__genarate_steps_x()

        painter = QtGui.QPainter(self)
        
        pen = QtGui.QPen(QtCore.Qt.white, self.width_line, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)

        if self.curren_x:
            pen = QtGui.QPen(QtCore.Qt.white, self.width_groove, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(self.curren_x, 5, self.curren_x, self.height() - 5)

    def __set_closets_value(self, x: int) -> tuple[int, int]:
        for i, close_x in enumerate(self.steps_x):
            if abs(x - close_x) <= self.step:  
                return close_x, i

    def setValue(self, value):
        self.curren_x = int(self.width() * value / 100)
        return super().setValue(value)
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        x = event.pos().x()
        if event.button() == QtCore.Qt.LeftButton:
            if self.curren_x - self.width_groove < x < self.curren_x + self.width_groove:
                self.is_click_groove = True
            else:
                info = self.__set_closets_value(x)
                if info is not None:
                    self.curren_x, index = self.__set_closets_value(x)
                    value = self.steps[index]
                    self.setValue(value)
                    self.sliderMoved.emit(value)
        event.ignore()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.is_click_groove = False
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        x = event.pos().x()
        if self.is_click_groove:
            if x > self.width_groove / 2 and x < self.width():
                if x in self.steps_x:
                    self.curren_x, index = self.__set_closets_value(x)
                    value = self.steps[index]
                    self.sliderMoved.emit(value)
                    self.update()
        return super().mouseMoveEvent(event)


@decorater_set_hand_cursor_button([QtWidgets.QPushButton, QtWidgets.QSlider])
class ZoomTable(QtWidgets.QWidget):
    signal_change_zoom = QtCore.pyqtSignal()

    def __init__(self, parent, table: Table):
        super().__init__(parent)

        self.table: Table = table
        self.min_zoom = table.min_zoom
        self.max_zoom = table.max_zoom
        self.step_zoom = table.step_zoom
        self.current_zoom = 100

        self.old_size_vh: list[int] = None
        self.old_size_hh: list[int] = None

        self.init_widgets()

    def init_widgets(self) -> None:
        self.__max_heigth = 18
        self.setMaximumHeight(self.__max_heigth + 4)

        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(0)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setObjectName('zoom_widget_frame')
        self.frame.setMaximumHeight(self.__max_heigth + 4)
        self.h_layout.addWidget(self.frame)

        self.h_layout_frame = QtWidgets.QHBoxLayout(self.frame)
        self.h_layout_frame.setContentsMargins(1, 1, 1, 1)
        self.h_layout_frame.setSpacing(0)
        self.h_layout_frame.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        
        self.btn_zoom_out = QtWidgets.QPushButton(self.frame)
        self.btn_zoom_out.setObjectName('btn_zoom_out')
        self.btn_zoom_out.setToolTip('Уменьшить масштаб')
        self.btn_zoom_out.setFixedSize(20, self.__max_heigth)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(SETTING.ICO_FOLDER, 'white_minus.png'))
        self.btn_zoom_out.setIcon(icon)
        self.btn_zoom_out.clicked.connect(self.click_btn_zoom_out)
        self.h_layout_frame.addWidget(self.btn_zoom_out)

        self.slider = CustomSlider(self.frame, 10)
        self.slider.setMinimumWidth(150)
        self.slider.setMaximumWidth(150)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setValue(self.current_zoom // 2)
        self.slider.sliderMoved.connect(self.moved_slider)
        self.h_layout_frame.addWidget(self.slider)

        self.btn_zoom_in = QtWidgets.QPushButton(self.frame)
        self.btn_zoom_in.setObjectName('btn_zoom_in')
        self.btn_zoom_in.setToolTip('Увеличить масштаб')
        self.btn_zoom_in.setFixedSize(20, self.__max_heigth)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(SETTING.ICO_FOLDER, 'white_plus.png'))
        self.btn_zoom_in.setIcon(icon)
        self.btn_zoom_in.clicked.connect(self.click_btn_zoom_in)
        self.h_layout_frame.addWidget(self.btn_zoom_in)

        self.label = QtWidgets.QLabel(self.frame)
        self.label.setMaximumSize(40, self.__max_heigth)
        self.label.setText('100%')
        self.label.setStyleSheet('QLabel {color: white}')
        self.h_layout_frame.addWidget(self.label)
    
    def set_value(self) -> None:
        self.label.setText(f'{self.current_zoom}%')
        self.slider.setValue(self.current_zoom // 2)
        self.apply_zoom()
        self.signal_change_zoom.emit()

    def click_btn_zoom_in(self) -> None:
        self.zoom_in()
        self.set_value()
    
    def click_btn_zoom_out(self) -> None:
        self.zoom_out()
        self.set_value()

    def moved_slider(self, value: int) -> None:
        self.current_zoom = value * 2
        self.label.setText(f'{self.current_zoom}%')
        self.apply_zoom()
        self.signal_change_zoom.emit()

    def zoom_in(self) -> None:
        zoom = self.current_zoom + self.step_zoom
        if zoom < self.max_zoom:
            self.current_zoom = zoom
        self.set_value()
    
    def zoom_out(self) -> None:
        zoom = self.current_zoom - self.step_zoom
        if zoom > self.min_zoom:
            self.current_zoom = zoom
        self.set_value()

    def apply_zoom(self):
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item: TableItem = self.table.item(row, col)
                item.set_zoom(self.current_zoom)
        
        for header in (self.table.verticalHeader(), self.table.horizontalHeader()):
            header: HeaderWithOverlayWidgets
            header.set_zoom(self.current_zoom)
    
