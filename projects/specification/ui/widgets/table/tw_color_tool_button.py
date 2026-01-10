from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import os
import ctypes

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context import SETTING
from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button

from projects.tools.custom_qwidget.line_separate import QHLineSeparate


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class PopupColorPanel(QtWidgets.QWidget):
    property_color_rbg = 'color'
    property_color_index = 'index'

    signal_get_color = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)

        self.current_color_btn: QtWidgets.QPushButton = None

        self.colors = [[{'color': (255, 255, 255, 255), 'index': 2}, {'color': (0, 0, 0, 255), 'index': 1}, {'color': (238, 236, 225, 255), 'index': 19}, {'color': (31, 73, 125, 255), 'index': 55}, {'color': (79, 129, 189, 255), 'index': 47}, {'color': (192, 80, 77, 255), 'index': 18}, {'color': (155, 187, 89, 255), 'index': 48}, {'color': (128, 100, 162, 255), 'index': 47}, {'color': (75, 172, 198, 255), 'index': 42}, {'color': (247, 150, 70, 255), 'index': 45}], [{'color': (242, 242, 242, 255), 'index': 2}, {'color': (128, 128, 128, 255), 'index': 16}, {'color': (221, 217, 196, 255), 'index': 15}, {'color': (197, 217, 241, 255), 'index': 24}, {'color': (220, 230, 241, 255), 'index': 20}, {'color': (242, 220, 219, 255), 'index': 19}, {'color': (235, 241, 222, 255), 'index': 19}, {'color': (228, 223, 236, 255), 'index': 24}, {'color': (218, 238, 243, 255), 'index': 20}, {'color': (253, 233, 217, 255), 'index': 19}], [{'color': (217, 217, 217, 255), 'index': 15}, {'color': (89, 89, 89, 255), 'index': 56}, {'color': (196, 189, 151, 255), 'index': 15}, {'color': (141, 180, 226, 255), 'index': 37}, {'color': (184, 204, 228, 255), 'index': 24}, {'color': (230, 184, 183, 255), 'index': 15}, {'color': (216, 228, 188, 255), 'index': 35}, {'color': (204, 192, 218, 255), 'index': 15}, {'color': (183, 222, 232, 255), 'index': 24}, {'color': (252, 213, 180, 255), 'index': 40}], [{'color': (191, 191, 191, 255), 'index': 15}, {'color': (64, 64, 64, 255), 'index': 56}, {'color': (148, 138, 84, 255), 'index': 16}, {'color': (83, 141, 213, 255), 'index': 42}, {'color': (149, 179, 215, 255), 'index': 37}, {'color': (218, 150, 148, 255), 'index': 48}, {'color': (196, 215, 155, 255), 'index': 15}, {'color': (177, 160, 199, 255), 'index': 15}, {'color': (146, 205, 220, 255), 'index': 37}, {'color': (250, 191, 143, 255), 'index': 40}], [{'color': (166, 166, 166, 255), 'index': 48}, {'color': (38, 38, 38, 255), 'index': 56}, {'color': (73, 69, 41, 255), 'index': 56}, {'color': (22, 54, 92, 255), 'index': 49}, {'color': (54, 96, 146, 255), 'index': 55}, {'color': (150, 54, 52, 255), 'index': 18}, {'color': (118, 147, 60, 255), 'index': 12}, {'color': (96, 73, 122, 255), 'index': 47}, {'color': (49, 134, 155, 255), 'index': 50}, {'color': (226, 107, 10, 255), 'index': 46}], [{'color': (128, 128, 128, 255), 'index': 16}, {'color': (13, 13, 13, 255), 'index': 1}, {'color': (29, 27, 16, 255), 'index': 52}, {'color': (29, 27, 16, 255), 'index': 52}, {'color': (36, 64, 98, 255), 'index': 49}, {'color': (99, 37, 35, 255), 'index': 56}, {'color': (79, 98, 40, 255), 'index': 56}, {'color': (64, 49, 81, 255), 'index': 56}, {'color': (33, 89, 103, 255), 'index': 49}, {'color': (151, 71, 6, 255), 'index': 53}], [{'color': (192, 0, 0, 255), 'index': 3}, {'color': (255, 0, 0, 255), 'index': 3}, {'color': (255, 192, 0, 255), 'index': 44}, {'color': (255, 255, 0, 255), 'index': 6}, {'color': (146, 208, 80, 255), 'index': 43}, {'color': (0, 176, 80, 255), 'index': 14}, {'color': (0, 176, 240, 255), 'index': 33}, {'color': (0, 112, 192, 255), 'index': 23}, {'color': (0, 32, 96, 255), 'index': 49}, {'color': (112, 48, 160, 255), 'index': 47}]]
        
        self.item_color_not_fill = {'color': None, 'index': 16777215}

        self.dict_color_btn: dict[tuple[int, int, int], QtWidgets.QPushButton] = {}
        self.list_last_color: list[tuple[int, int, int, int]] = [None] * len(self.colors[0])
        self.setWindowFlags(QtCore.Qt.WindowType.Popup | QtCore.Qt.WindowType.NoDropShadowWindowHint)

        self.central_layout = QtWidgets.QVBoxLayout(self)
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.central_frame = QtWidgets.QFrame(self)
        self.central_frame.setObjectName('central_frame')
        self.central_frame.setStyleSheet('#central_frame {background-color: white; border: 1px solid black}')
        self.central_layout.addWidget(self.central_frame)

        self.v_lauout = QtWidgets.QGridLayout(self.central_frame)
        self.v_lauout.setSpacing(0)
        self.v_lauout.setContentsMargins(0, 0, 0, 0)

        self._init_widgets()

        # self.setFixedSize(self.layout().sizeHint())

    def _init_widgets(self) -> None:
        # --------------------------------- ROW 1 --------------------------------------
        self.lable_title = self._create_label(text='Цвета темы')
        self.v_lauout.addWidget(self.lable_title)
        
        self.frame_title_color, self.h_layout_title_color = self._create_frame_row()
        self.v_lauout.addWidget(self.frame_title_color)

        for item_color in self.colors[0]:
            btn = self._create_btn(self.frame_title_color, item_color)
            self.h_layout_title_color.addWidget(btn)
        
        # --------------------------------- ROW 2 --------------------------------------
        self.frame_grid_color, self.h_layout_grid_color = self._create_frame_row(4)
        self.v_lauout.addWidget(self.frame_grid_color)
        
        for x in range(len(self.colors[0])):
            color_column = self._create_color_column(self.frame_grid_color, x)
            self.h_layout_grid_color.addWidget(color_column)

        # --------------------------------- ROW 2 --------------------------------------
        self.label_popular_color = self._create_label(text='Стандартные цвета')
        self.v_lauout.addWidget(self.label_popular_color)

        self.frame_popular_color, self.h_layout_popular_color = self._create_frame_row()
        self.v_lauout.addWidget(self.frame_popular_color)

        for item_color in self.colors[-1]:
            btn = self._create_btn(self.frame_popular_color, item_color)
            self.h_layout_popular_color.addWidget(btn)
        
        # --------------------------------- ROW 4 --------------------------------------
        self.btn_not_fill = QtWidgets.QPushButton(self)
        self.btn_not_fill.setCheckable(True)
        self.btn_not_fill.setObjectName('btn_not_fill')
        self.btn_not_fill.setStyleSheet('#btn_not_fill {background-color: white; border: none; padding: 3px} #btn_not_fill:hover {background-color: rgb(238, 238, 238)}')
        self.btn_not_fill.setText('Нет заливки')
        self.btn_not_fill.setFixedHeight(20)
        self.btn_not_fill.clicked.connect(self._click_not_fill)
        self.v_lauout.addWidget(self.btn_not_fill)

        # --------------------------------- ROW 5 --------------------------------------
        h_line_separate = QHLineSeparate(self)
        self.v_lauout.addWidget(h_line_separate)

        # --------------------------------- ROW LAST COLOR --------------------------------------
        self.label_last_color = self._create_label(text='Последние цвета')
        self.v_lauout.addWidget(self.label_last_color)
        self.label_last_color.hide()

        self.frame_last_color, self.h_layout_last_color = self._create_frame_row(spacing=6)
        self.h_layout_last_color.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.v_lauout.addWidget(self.frame_last_color)
        self.frame_last_color.hide()

        # --------------------------------- OTHER COLOR  --------------------------------------
        self.color_dialog = QtWidgets.QColorDialog(self)

        self.btn_get_other_color = QtWidgets.QPushButton(self)
        self.btn_get_other_color.setObjectName('btn_get_other_color')
        self.btn_get_other_color.setStyleSheet('#btn_get_other_color {background-color: white; border: none; padding: 3px} #btn_get_other_color:hover {background-color: rgb(238, 238, 238)}')
        self.btn_get_other_color.setText('Другие цветы...')
        self.btn_get_other_color.setFixedHeight(20)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(SETTING.ICO_FOLDER, 'color_wheel.png'))
        self.btn_get_other_color.setIcon(icon)
        self.btn_get_other_color.clicked.connect(self._get_other_color)
        self.v_lauout.addWidget(self.btn_get_other_color)

    def _create_label(self, text: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(self.central_frame)
        label.setText(f'<b>{text}</b>')
        label.setStyleSheet('QLabel {background-color: rgb(238, 238, 238); color: #77778C}')
        label.setFixedHeight(25)
        return label
        
    def _create_btn(self, parent: QtWidgets.QFrame, item_color: dict[str, tuple[int, ...], int], is_border=True) -> QtWidgets.QPushButton:
        color_rgb, color_index = item_color['color'], item_color['index']
        
        btn_name = f'btn_{len(self.dict_color_btn) + 1}'

        btn = QtWidgets.QPushButton(parent)
        btn.setObjectName(btn_name)
        btn.setFixedSize(12, 12)
        btn.setProperty(self.property_color_rbg, color_rgb)
        btn.setProperty(self.property_color_index, color_index)
        
        str_color = ', '.join([str(i) for i in color_rgb])
        bg = f"background-color: rgba({str_color})"
        str_border = 'border: 1px solid gray;' if is_border else 'border: none;'
        btn.setStyleSheet(f'#{btn_name} {{{bg};{str_border}; border-radius: none;}} #{btn_name}:focus {{border: 1px solid red; outline: 1px solid white;}} #{btn_name}:hover {{border: 1px solid red}}')
    
        btn.clicked.connect(self._get_color)

        self.dict_color_btn[color_rgb] = btn

        return btn
    
    def _create_frame_row(self, spacing: int = 5) -> tuple[QtWidgets.QFrame, QtWidgets.QHBoxLayout]:
        frame = QtWidgets.QFrame(self.central_frame)
        self.v_lauout.addWidget(frame, 4, 0, 1, 1)

        h_layout = QtWidgets.QHBoxLayout(frame)
        h_layout.setContentsMargins(2, 2, 2, 2)
        h_layout.setSpacing(spacing)

        return frame, h_layout

    def _create_color_column(self, parent: QtWidgets.QFrame, column: int) -> QtWidgets.QFrame:
        frame = QtWidgets.QFrame(parent)
        frame.setStyleSheet('QFrame {border: 1px solid gray}')

        v_layout = QtWidgets.QVBoxLayout(frame)
        v_layout.setSpacing(0)
        v_layout.setContentsMargins(0, 0, 0, 0)

        for y in range(1, len(self.colors) - 1):
            item_color = self.colors[y][column]
            btn = self._create_btn(parent=frame, item_color=item_color, is_border=False)
            v_layout.addWidget(btn)
        
        return frame

    def _click_not_fill(self) -> None:
        self.btn_not_fill.setChecked(True)
        self.btn_not_fill.setFocus()
        self.signal_get_color.emit(None)
        self.hide()

    def _get_color(self) -> None:
        """
        Нажатие на кнопку выбора цвета
        """
        btn: QtWidgets.QPushButton = self.sender()
        self.current_color_btn = btn
        self.hide()
        self.signal_get_color.emit(QtGui.QColor(*btn.property(self.property_color_rbg))) 

    def _create_other_color_btn(self, color: tuple[int, int, int, int]) -> None:
        """
        Создание и добавление на слой кнопки с нестандартным цветом
        
        :param self: Описание
        :param color: Описание
        :type color: tuple[int, int, int, int]
        """
        item_color = {'color': color, 'index': None}
        btn = self._create_btn(self.frame_last_color, item_color)
        self.current_color_btn = btn
            
        if self.h_layout_last_color.count() == len(self.colors[0]):
            self.h_layout_last_color.removeWidget(self.h_layout_last_color.itemAt(self.h_layout_last_color.count() - 1).widget())
            
        self.h_layout_last_color.insertWidget(0, btn)
        self.label_last_color.show()
        self.frame_last_color.show()
        self.resize(self.v_lauout.sizeHint())

    def _get_other_color(self) -> None:
        """
        Выбора не стандартного цвета
        """
        color = self.color_dialog.getColor()
        if color.isValid():
            tuple_color = tuple(color.getRgb())
            if tuple_color not in self.dict_color_btn:
                self._create_other_color_btn(tuple_color)
            self.signal_get_color.emit(color)

    def _view_color(self, color: tuple[int, int, int, int] | None) -> None:
        if color is None:
            if self.current_color_btn:
                self.current_color_btn.setFocus()
        else:
            btn = self.dict_color_btn.get(color)
            if btn:
                btn.setFocus()
            else:
                self._create_other_color_btn(color)
                
    def show(self, color: tuple[int, int, int, int] | None):
        self._view_color(color)
        return super().show()


class ButtonColor(QtWidgets.QPushButton):
    """
    Самописный ToolButton, так как надо было рисовать внутри кнопки
    """
    signal_clicked = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, parent):
        super().__init__(parent)
        
        self.setMouseTracking(True)

        self._padding = 3
        self._line_height = 4 
        self._rect: QtCore.QRect= None
        self._line_rect: QtCore.QRect = None
        self._bg_color = QtGui.QColor(255, 255, 255, 255)
        self._current_color = QtGui.QColor(255, 0, 0, 255)
        
        self._icon = None

        self._text = None
        self._font = QtGui.QFont()
        self._font.setBold(True)

        self.clicked.connect(lambda: self.signal_clicked.emit(self._current_color))

    def set_text(self, text: str) -> None:
        self._text = text

    def set_icon(self, filepath: str) -> None:
        self._icon = QtGui.QIcon()
        self._icon.addFile(filepath)

    def set_current_color(self, color: QtGui.QColor) -> None:
        self._current_color = color
        self.update()

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
        if self._rect is None:
            self._rect = QtCore.QRect(x + self._padding, y + self._padding, w - self._padding * 2, h - self._padding * 2)
        pen = QtGui.QPen(self._bg_color)
        brush = QtGui.QBrush(self._bg_color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self._rect)

        if self._line_rect is None:
            self._line_rect = QtCore.QRect(x + self._padding, h - self._padding - 4, w - self._padding * 2, self._line_height)

        pen = QtGui.QPen(self._current_color)
        brush = QtGui.QBrush(self._current_color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self._line_rect)

        pen = QtGui.QPen(QtCore.Qt.GlobalColor.lightGray)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(w, self._padding, w, h - self._padding)

        if self._text:
            font_rect = QtCore.QRect(x, y - self._line_height // 2,  w, h)
            pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
            painter.setPen(pen)
            painter.setFont(self._font)
            painter.drawText(font_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self._text)
        
        if self._icon:
            size = QtCore.QSize(w, h - self._line_height - self._padding * 2)
            point = QtCore.QPoint(self._padding * 2, self._padding)
            painter.drawPixmap(point, self._icon.pixmap(size))


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class ColorToolButton(QtWidgets.QWidget):
    """
    Основной виджет добавляемый в приложение
    """
    signal_get_color = QtCore.pyqtSignal(object) # получить цвет от виджета
    signal_set_color = QtCore.pyqtSignal(object) # задать цвет от виджету

    def __init__(self, parent):
        super().__init__(parent)

        self._current_color: tuple[int, int, int, int] = None

        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(0)

        self.btn_left = ButtonColor(self)
        self.btn_left.setObjectName('btn_left')
        self.btn_left.signal_clicked.connect(self._get_color)
        self.h_layout.addWidget(self.btn_left)

        self.btn_rigth = QtWidgets.QPushButton(self)
        self.btn_rigth.setObjectName('btn_rigth')
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(SETTING.ICO_FOLDER, 'triangle.png'))
        self.btn_rigth.setIcon(icon)
        self.btn_rigth.setIconSize(QtCore.QSize(10, 10))
        self.btn_rigth.clicked.connect(self._show_popup)
        self.h_layout.addWidget(self.btn_rigth)

        self.popup = PopupColorPanel(self)
        self.popup.signal_get_color.connect(self._get_color)
    
    def setFixedSize(self, w: int, h: int) -> None:
        self.setMaximumSize(w, h)
        self.btn_left.setFixedSize(int(w * 0.7), h)
        self.btn_rigth.setFixedSize(int(w * 0.3), h)

    def set_icon(self, filepath: str) -> None:
        self.btn_left.set_icon(filepath)

    def set_text(self, text: str) -> None:
        self.btn_left.set_text(text)

    def _get_color(self, color: QtGui.QColor = None) -> None:
        if color:
            self.btn_left.set_current_color(color)
        if color is None:
            self.btn_left.set_current_color(QtGui.QColor(255, 0, 0))
        self.signal_get_color.emit(color)

    def set_color(self, color: QtGui.QColor | tuple[int, int, int]) -> None:
        if isinstance(color, QtGui.QColor):
            color = tuple(color.getRgb())
        elif isinstance(color, list):
            color = tuple(color)
        self._current_color = color

    def _show_popup(self) -> None: 
        button_global_pos = self.btn_left.mapToGlobal(QtCore.QPoint(0, 0))
        geom = self.btn_left.geometry()
        
        h = geom.height()
        x = button_global_pos.x()
        y = button_global_pos.y() + h
        self.popup.setGeometry(x, y, self.popup.width(), self.popup.height())
        self.popup.show(self._current_color)


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
        self.tool_btn.setFixedSize(40, 25)
        # self.tool_btn.set_text('A')
        self.tool_btn.set_icon(os.path.join(SETTING.ICO_FOLDER, 'fill_color.png'))
        # self.tool_btn.signal_get_color.connect(lambda color: print(color))
        self.v_lauout.addWidget(self.tool_btn)

        self.resize(500, 500)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())