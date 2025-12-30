from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
import ctypes

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    print(test_path)
    sys.path.append(test_path)

from projects.specification.config.app_context import SETTING, SIGNAL_BUS, ENUMS
from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button


class ColorPanel: ...


class ButtonColor(QtWidgets.QPushButton):
    signal_clicked_left = QtCore.pyqtSignal()
    signal_clicked_rigth = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        
        self.setMouseTracking(True)
        # self.setStyleSheet('ToolButtonColor:hover {background-color: white}')

        self._padding = 2
        self._line_height = 4 

        self._icon_arrow = QtGui.QIcon()
        self._icon_arrow.addFile(os.path.join(SETTING.ICO_FOLDER, 'triangle.png'))
        

        self._left_rect: QtCore.QRect= None
        self._rigth_rect: QtCore.QRect = None
        self._line_rect: QtCore.QRect = None

        self._bg_color = QtGui.QColor(255, 255, 255)
        self._bg_left_rect_color = QtGui.QColor(255, 255, 255)
        self._bg_rigth_rect_color = QtGui.QColor(255, 255, 255)
        self._current_color = QtGui.QColor(255, 128, 128)
        
        self._text = None
        self._font = QtGui.QFont()
        self._font.setBold(True)

    def set_text(self, text: str) -> None:
        self._text = text

    def set_icon(self, filepath: str) -> None:
        self._icon = QtGui.QIcon()
        self._icon.addFile(filepath)

    def set_curent_color(self, color: QtGui.QColor) -> None:
        self._current_color = color

    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        
        # ------------- Закрашивание заднего фона ------------- 
        pen = QtGui.QPen(self._bg_color)
        brush = QtGui.QBrush(self._bg_color)
        painter.setPen(pen)
        painter.setBrush(brush)

        x, y, w, h = event.rect().getCoords()
        
        # ------------- Левая часть ------------- 
        if self._left_rect is None:
            self._left_rect = QtCore.QRect(x + self._padding, y + self._padding, int(w * 0.75) - self._padding * 2, h - self._padding * 2)
        pen = QtGui.QPen(self._bg_left_rect_color)
        brush = QtGui.QBrush(self._bg_left_rect_color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self._left_rect)

        if self._line_rect is None:
            self._line_rect = QtCore.QRect(x + self._padding, h - self._padding - 4, int(w * 0.75) - self._padding * 2, self._line_height)
        pen = QtGui.QPen(self._current_color)
        brush = QtGui.QBrush(self._current_color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self._line_rect)

        if self._text:
            font_rect = QtCore.QRect(x + 3, 1, w // 2, h - 5)
            pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
            painter.setPen(pen)
            painter.setFont(self._font)
            painter.drawText(font_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self._text)
        
        if self._icon:
            size = QtCore.QSize(int(w * 0.75), event.rect().height() - self._line_height - self._padding * 4)
            point = QtCore.QPoint(self._padding * 2, self._padding * 2)
            painter.drawPixmap(point, self._icon.pixmap(size))

        # ------------- Правая часть ------------- 
        if self._rigth_rect is None:
            self._rigth_rect = QtCore.QRect(x + self._padding + int(w * 0.75) - self._padding * 2, y + self._padding, int(w * 0.25), h - self._padding * 2)
        pen = QtGui.QPen(self._bg_rigth_rect_color)
        brush = QtGui.QBrush(self._bg_rigth_rect_color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self._rigth_rect)
        painter.drawPixmap(QtCore.QPoint(self._rigth_rect.x(), self._rigth_rect.height() // 3), self._icon_arrow.pixmap(self._rigth_rect.size()))

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._left_rect:
            if self._left_rect.contains(event.pos()):
                self._bg_left_rect_color = QtGui.QColor(209, 235, 255)
                self.update()
            else:
               self._bg_left_rect_color = QtGui.QColor(255, 255, 255)
        
        if self._rigth_rect:
            if self._rigth_rect.contains(event.pos()):
                self._bg_rigth_rect_color = QtGui.QColor(209, 235, 255)
                self.update()
            else:
               self._bg_rigth_rect_color = QtGui.QColor(255, 255, 255)

        return super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if self._left_rect.contains(event.pos()):
            self.signal_clicked_left.emit()
        if self._rigth_rect.contains(event.pos()):
            self.signal_clicked_rigth.emit()
        return super().mousePressEvent(event)   

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class ColorToolButton(QtWidgets.QWidget):
    signal_get_color = QtCore.pyqtSignal(QtGui.QColor) # получить цвет от виджета
    signal_set_color = QtCore.pyqtSignal(QtGui.QColor) # задать цвет от виджету

    def __init__(self, parent):
        super().__init__(parent)

        self.btn = ButtonColor(self)
        self.btn.setFixedSize(35, 25)
        self.btn.set_icon(os.path.join(SETTING.ICO_FOLDER, 'fill_color.png'))
        self.btn.signal_clicked_left.connect(self._get_color)
        self.btn.signal_clicked_rigth.connect(self.show_popup)

        self.popup = None
    
    def _get_color(self) -> None:
        self.signal_get_color.emit(self.btn._current_color)

    def show_popup(self) -> None:
        ...

    def set_color(self, color: QtGui.QColor) -> None:
        self.btn._current_color = color
        self.btn.update()

    

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(os.path.join(SETTING.ICO_FOLDER, 'Specification.png')))

        with open(os.path.join(SETTING.RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', SETTING.ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)


        self.central_widget = QtWidgets.QWidget(self)
        self.central_widget.setObjectName('central_widget')
        self.setCentralWidget(self.central_widget)

        self.v_lauout = QtWidgets.QGridLayout(self.central_widget)
        self.v_lauout.setSpacing(5)
        self.v_lauout.setContentsMargins(0, 0, 0, 0)

        self.tool_btn = ColorToolButton(self)
        self.tool_btn.signal_get_color.connect(lambda color: print(color))
        self.v_lauout.addWidget(self.tool_btn)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())