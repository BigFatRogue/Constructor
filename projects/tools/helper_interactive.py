import sys
import os
import json
from typing import Union

from PyQt5 import QtCore, QtWidgets, QtGui


if __name__ == '__main__':
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent)
    sys.path.append(test_path)

from projects.tools.settings import ICO_FOLDER_HELPER
from projects.tools.custom_qwidget.h_line_separate import QHLineSeparate
from projects.tools.custom_qwidget.messege_box_question import MessegeBoxQuestion
from projects.tools.row_counter import RowCounter
from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class ToolTipMessage(QtWidgets.QWidget): 
    signal_next_step = QtCore.pyqtSignal()
    signal_prev_step = QtCore.pyqtSignal()
    signal_end = QtCore.pyqtSignal(bool)

    TEXT_BTN_NEXT_STEP = 'Следующий шаг'
    TEXT_BTN_WAIT = 'Пожалуйста, подождите...'
    TEXT_BTN_END = 'Завершить'

    def __init__(self, parent):
        super().__init__(parent)

        self.old_pos: QtCore.QPoint = None
        self.new_pos: QtCore.QPoint = None
        self.flag_move = False

        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.installEventFilter(self)
        self.init_widgets()
    
    def init_widgets(self) -> None:
        self.setMinimumSize(100, 100)
        self.setStyleSheet('''
                   ToolTipMessage {
                   background-color: white;
                   padding: 5px;
                   }''')
        self.v_layout = QtWidgets.QGridLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.v_layout)

        self.frame_tool_tip = QtWidgets.QFrame(self)
        self.frame_tool_tip.setObjectName('frame_tool_tip')
        self.frame_tool_tip.setStyleSheet('''
                           #frame_tool_tip {
                           background-color: white;
                           border: 3px solid #0078d4;
                           padding: 5px;
                           }''')
        self.v_layout.addWidget(self.frame_tool_tip)
        
        self.grid_layout = QtWidgets.QGridLayout(self.frame_tool_tip)
        self.grid_layout.setSpacing(5)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        
        row_counter = RowCounter()

        self.btn_prev_step = QtWidgets.QPushButton(self)
        self.btn_prev_step.setMaximumSize(20, 20)
        self.btn_prev_step.setObjectName('btn_prev_step')
        self.btn_prev_step.setToolTip('Предыдущий шаг')
        self.btn_prev_step.setStyleSheet('''
                                #btn_prev_step {
                                border: none;
                                border-radius: 5px;
                                }
                                #btn_prev_step:hover {
                                background-color: rgb(209, 235, 255);
                                }
                                ''')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER_HELPER, 'icon_back.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_prev_step.setIcon(icon)
        self.btn_prev_step.clicked.connect(self.prev_step)
        self.grid_layout.addWidget(self.btn_prev_step, row_counter.value, 0, 1, 1)

        self.label_title = QtWidgets.QLabel(self.frame_tool_tip)
        self.label_title.setMaximumHeight(20)
        self.label_title.setObjectName('label_title')
        self.label_title.setStyleSheet('#label_title {}')
        self.grid_layout.addWidget(self.label_title, row_counter.value, 1, 1, 1)
    
        self.btn_end_tour = QtWidgets.QPushButton(self.frame_tool_tip)
        self.btn_end_tour.setObjectName('btn_end_tour')
        self.btn_end_tour.setMaximumSize(20, 20)
        self.btn_end_tour.setToolTip('Завершить')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER_HELPER, 'icon_red_close.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_end_tour.setIcon(icon)
        self.btn_end_tour.setStyleSheet('''
                                        #btn_end_tour {
                                        border: none;
                                        border-radius: 5px;
                                        }
                                        #btn_end_tour:hover {
                                        background-color: rgb(209, 235, 255);
                                        }
                                        ''')

        self.btn_end_tour.clicked.connect(lambda: self.end(True))
        self.grid_layout.addWidget(self.btn_end_tour, row_counter.value, 2, 1, 1)

        self.line_separate = QHLineSeparate(self.frame_tool_tip)
        self.grid_layout.addWidget(self.line_separate, row_counter.next(), 0, 1, 3)

        self.label_message = QtWidgets.QLabel(self.frame_tool_tip)
        self.label_message.setObjectName('label_message')
        self.label_message.setWordWrap(True)
        self.label_message.setStyleSheet('''
                                        #label_message {
                                        font-size: 12pt; 
                                        }
                                        ''')
        self.label_message.setMinimumWidth(250)
        self.grid_layout.addWidget(self.label_message, row_counter.next(), 0, 1, 2)

        self.label_content = QtWidgets.QLabel(self.frame_tool_tip)
        self.grid_layout.addWidget(self.label_content, row_counter.next(), 0, 1, 2)
        "#1c9dff"
        self.btn_next_step = QtWidgets.QPushButton(self)
        self.btn_next_step.setText(self.TEXT_BTN_NEXT_STEP)
        self.btn_next_step.setMinimumHeight(20)
        self.btn_next_step.setObjectName('btn_next_step')
        self.btn_next_step.setStyleSheet("""
                                         #btn_next_step {
                                            border: 1px solid gray;
                                            border-radius: 6px;
                                            min-height: 20px;
                                            background-color: rgb(209, 235, 255);
                                         
                                        }
                                        #btn_next_step:hover {
                                            border: 1px solid #0078d4;
                                            background-color: rgb(180, 215, 255);
                                        }""")
        self.btn_next_step.clicked.connect(self.next_step)
        self.grid_layout.addWidget(self.btn_next_step, row_counter.next(), 0, 1, 3)
    
    def set_title(self, title: str) -> None:
        self.label_title.setText(title)

    def set_text(self, text: str) -> None:
        self.label_message.setText(text)
        QtCore.QTimer.singleShot(10, self.adjustSize)

    def set_content(self, content_path: str) -> None:
        if content_path:
            gif = QtGui.QMovie(content_path)
            self.label_content.setMovie(gif)
            gif.start()
        else:
            self.label_content.clear()
        QtCore.QTimer.singleShot(10, self.adjustSize)
            
    def set_is_button_wait(self, value: bool=False) -> None:
        if value:
            self.btn_next_step.setEnabled(False)
            self.btn_next_step.setText(self.TEXT_BTN_WAIT)
        else:
            self.btn_next_step.setEnabled(True)
            self.btn_next_step.setText(self.TEXT_BTN_NEXT_STEP)

    def set_pos(self, point: QtCore.QPointF) -> None:
        self.setGeometry(int(point.x()), int(point.y()), self.width(), self.height()) 

    def next_step(self) -> None:
        if self.btn_next_step.text() == self.TEXT_BTN_NEXT_STEP:
            self.signal_next_step.emit()
        elif self.btn_next_step.text() == self.TEXT_BTN_END:
            self.end(False)

    def prev_step(self) -> None:
        self.signal_prev_step.emit()

    def end(self, value: bool) -> None:
        self.signal_end.emit(value)

    def set_text_button(self, text: str) -> None:
        self.btn_next_step.setText(text)

    def eventFilter(self, obj, event):
        tp = event.type()

        if tp == QtCore.QEvent.FocusOut:
            event.ignore()
            return False
        if tp == 2:
            self.old_pos = event.pos()
            self.flag_move = True
        elif tp == 3:
            self.flag_move = False
        if tp == 5:
            pos = self.geometry().topLeft() + (event.pos() - self.old_pos)
            self.set_pos(pos)

        return super().eventFilter(obj, event)


class WidgetBackground(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.resize(parent.size())

        self.list_widgets: list[QtWidgets.QWidget] = []
        self.highlight_rect = QtCore.QRectF()

        self.__step_transparency = 5
        self.__sign = 1
        self.__highlight_color_transparency = 255 - self.__step_transparency
        self.__timer = QtCore.QTimer()
        self.__timer.timeout.connect(self.__set_color_border_highlight)
        self.__timer.start(1000 // 60)
    
    def set_list_widget(self, widgets: Union[list[QtWidgets.QWidget], QtCore.QRect]) -> None:
        self.list_widgets = widgets
        self.highlight_step()

    def highlight_step(self) -> None:
        x0 = y0 = x1 = y1 = 0
        for widget in self.list_widgets:
            if isinstance(widget, QtCore.QRect):
                x0_widget, y0_widget = widget.x(), widget.y()
                width, heigth = widget.size().width(), widget.size().height()
                x1_widget, y1_widget = x0_widget + width, y0_widget + heigth
            else:
                x0_widget, y0_widget = widget.mapTo(self.parent(), QtCore.QPoint(0, 0)).x(), widget.mapTo(self.parent(), QtCore.QPoint(0, 0)).y()
                width, heigth = widget.size().width(), widget.size().height()
                x1_widget, y1_widget = x0_widget + width, y0_widget + heigth
                        
            if x0 == y0 == x1 == y1 == 0:
                x0, y0, x1, y1 = x0_widget, y0_widget, x1_widget, y1_widget
            else:
                if x0_widget < x0:
                    x0 = x0_widget
                if y0_widget < y0:
                    y0 = y0_widget
                if x1_widget > x1:
                    x1 = x1_widget
                if y1_widget > y1:
                    y1 = y1_widget

        point = QtCore.QPoint()
        point.setX(x0 - 5)
        point.setY(y0 - 5)
        
        size_f = QtCore.QSizeF()
        size_f.setWidth(abs(x1 - x0) + 10)
        size_f.setHeight(abs(y1 - y0) + 10)
        self.highlight_rect = QtCore.QRectF(point, size_f)
        self.update()
    
    def __set_color_border_highlight(self) -> None:
        if self.__highlight_color_transparency < 5 or self.__highlight_color_transparency > 255 - self.__step_transparency:
            self.__sign *= -1
        self.__highlight_color_transparency -= self.__step_transparency * self.__sign
        self.update(self.highlight_rect.toRect())

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(self.rect()))
        path.addRoundedRect(self.highlight_rect, 5, 5)

        painter.setPen(QtGui.QPen(QtGui.QColor(220, 80, 0, self.__highlight_color_transparency), 5))
        painter.drawRect(self.highlight_rect)

        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(0, 0, 0, 220)))
        
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        painter.end()

    def resizeEvent(self, event):
        self.highlight_step()
        return super().resizeEvent(event)


class HelperInteractive:
    def __init__(self, parent: QtWidgets.QWidget, path_parent_resources: str):
        self.parent = parent
        self.path_parent_resources = path_parent_resources
        self.parent.moveEvent = self.move
        self.__is_visible = False
        self.path_config: str = None

        self.old_pos_tool_tip = self.parent.x(), self.parent.y()

        self.dict_data: dict[int, dict[dict[str, list]]] = None
        self.curent_index_step = 0

        self.widget_background = None
        self.widget_tool_tip = None

        self.__init_widget()

    def __init_widget(self) -> None:
        self.widget_background = WidgetBackground(self.parent)
        self.widget_tool_tip = ToolTipMessage(self.parent)
        self.widget_tool_tip.signal_next_step.connect(self.next_step)
        self.widget_tool_tip.signal_prev_step.connect(self.prev_step)
        self.widget_tool_tip.signal_end.connect(self.close)

    def __init_data(self, data: dict) -> None:
        for step, data_step in data.items():
            data_step['widgets'] = []
            for object_name in data[step]['object_names']:
                if '.' not in object_name:
                    widget = self.parent.findChild(QtCore.QObject, object_name)
                    if widget:
                        data_step['widgets'].append(widget)
                else:
                    object_name, column_number = object_name.split('.')
                    widget = self.parent.findChild(QtCore.QObject, object_name)
                    if widget:
                        rect = self.__get_rect_tree_header(widget, int(column_number))
                        data_step['widgets'].append(rect)                                  
        self.dict_data = data
    
    def load_config(self, filepath: str) -> None:
        self.path_config = filepath
        with open(filepath, 'r', encoding='utf-8') as config:
            steps: dict = json.load(config).get('steps')
            if steps:
                self.__init_data(steps)                             
    
    def _add_config(self, data: dict) -> None:
        self.__init_data(data)

    def __get_rect_tree_header(self, tree: QtWidgets.QTreeView, index: int) -> QtCore.QRect:
        header = tree.header()
        header.children()
        header_rect = header.rect()
        column_width = header.sectionSize(index)
        prev_column_width = 0
        if index > 0:
            for i in range(index):
                prev_column_width += header.sectionSize(i)
        header_pos = header.mapTo(self.parent, QtCore.QPoint(0, 0))
        return QtCore.QRect(header.x() + prev_column_width, header_pos.y(), column_width, header_rect.height())

    def next_step(self) -> None:
        if self.dict_data is None or not str(self.curent_index_step) in self.dict_data:
            return

        if self.curent_index_step + 1 < len(self.dict_data):
            self.curent_index_step += 1
        
        self.show_step()

    def prev_step(self) -> None:
        if self.dict_data is None:
            return
        
        if self.curent_index_step - 1 >= 0:
            self.curent_index_step -= 1
        
        self.show_step(button_is_wait=False)
    
    def show_step(self, button_is_wait=None) -> None:
        if not str(self.curent_index_step) in self.dict_data:
            return
        
        self.dict_data[str(self.curent_index_step)]['widgets'] = self.get_widget_from_object_name()

        if button_is_wait is None:
            button_is_wait = self.dict_data[str(self.curent_index_step)]['button_is_wait']
        if 'is_check' in self.dict_data[str(self.curent_index_step)]:
            button_is_wait = False
        
        rel_content_path = self.dict_data[str(self.curent_index_step)]['content_path']
        if rel_content_path:
            content_path = os.path.join(self.path_parent_resources, rel_content_path)
        else:
            content_path = ''

        self.widget_background.set_list_widget(self.dict_data[str(self.curent_index_step)]['widgets'])
        self.widget_tool_tip.set_title(title=f'Шаг {self.curent_index_step + 1}')
        self.widget_tool_tip.set_text(text=self.dict_data[str(self.curent_index_step)]['message'])
        self.widget_tool_tip.set_is_button_wait(button_is_wait)
        self.widget_tool_tip.set_content(content_path=content_path)

        if self.curent_index_step + 1 == len(self.dict_data):
            self.widget_tool_tip.set_text_button('Завершить')

        QtCore.QTimer.singleShot(20, lambda: self.widget_tool_tip.set_pos(self.calc_pos_tool_tiip()))
        self.enable_event_widgets()
        self.desable_event_widgets()

        self.widget_background.update()

    def get_widget_from_object_name(self, list_object_name: list[str]=None) -> list:
        if list_object_name is None:
            list_object_name = self.dict_data[str(self.curent_index_step)]['object_names']
        list_widgets = []
        for object_name in list_object_name:
            if '.' not in object_name:
                widget = self.parent.findChild(QtCore.QObject, object_name)
                if widget:
                    list_widgets.append(widget)
            else:
                object_name, column_number = object_name.split('.')
                widget = self.parent.findChild(QtCore.QObject, object_name)
                if widget:
                    rect = self.__get_rect_tree_header(widget, int(column_number))
                    list_widgets.append(rect)    
        return list_widgets

    def desable_event_widgets(self, parent=None) -> None:
        if parent is None:
            parent = self.parent
        for child in parent.children():
            if child == self.widget_tool_tip:
                continue
            if isinstance(child, (QtWidgets.QPushButton, QtWidgets.QLineEdit, QtWidgets.QCheckBox, QtWidgets.QMenuBar, QtWidgets.QTreeView)) and child not in self.dict_data[str(self.curent_index_step)]['widgets']:
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
                child.setFocusPolicy(QtCore.Qt.NoFocus)
            self.desable_event_widgets(child)

    def enable_event_widgets(self, parent=None) -> None:
        if parent is None:
            parent = self.parent
        for child in parent.children():
            if isinstance(child, (QtWidgets.QPushButton, QtWidgets.QLineEdit, QtWidgets.QCheckBox, QtWidgets.QMenuBar, QtWidgets.QTreeView)):
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
                child.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.enable_event_widgets(child)

    def calc_pos_tool_tiip(self) -> QtCore.QPoint:
        if self.dict_data[str(self.curent_index_step)]['widgets']:
            rect = self.widget_background.highlight_rect
            x, y = rect.x(), rect.y()

            if rect.x() + self.widget_tool_tip.width() > self.parent.width():
                x = self.parent.width() - self.widget_tool_tip.width() - 10
            else:
                x += 10
            if rect.y() + rect.height() + self.widget_tool_tip.height() > self.parent.height():
                y -= self.widget_tool_tip.height() + 10
            else:
                y += rect.height() + 10

            return QtCore.QPointF(x + self.parent.geometry().x(), y + self.parent.geometry().y())
        else:
            x = self.parent.x() + (self.parent.width()  - self.widget_tool_tip.width())/2
            y = self.parent.y() + (self.parent.height() - self.widget_tool_tip.height())/2
            return QtCore.QPointF(x, y)

    def reset(self) -> None:
        self.load_config(self.path_config)

    def isVisible(self) -> bool:
        return self.__is_visible       

    def show(self) -> None:

        self.__is_visible = True
        
        self.widget_background.resize(self.parent.size())
        self.widget_background.show()
        self.widget_tool_tip.show()
        self.show_step()
        
    def hide(self) -> None:
        self.__is_visible = False
        self.curent_index_step = 0
        self.enable_event_widgets()
        self.widget_background.hide()
        self.widget_tool_tip.hide()
    
    def close(self, with_dialog_window=True) -> None:
        if with_dialog_window:
            mbq = MessegeBoxQuestion(self.parent, title='Завершить', question='Завершить показ интерактивной спраки?')
            if mbq.exec() == QtWidgets.QDialog.Accepted:
                self.hide()
        else:
            self.hide()

    def resize(self, size) -> None:
        self.widget_background.resize(size)

    def delete(self) -> None:
        del self.widget_background
        del self.widget_tool_tip

        self.widget_background = None
        self.widget_tool_tip = None

    def move(self, event: QtGui.QMoveEvent) -> None:
        if self.widget_tool_tip:
            d_pos = event.pos() - event.oldPos()
            dx, dy = d_pos.x(), d_pos.y()
            xt, yt, wt, ht = self.widget_tool_tip.geometry().getRect()
            self.widget_tool_tip.setGeometry(xt + dx, yt + dy, wt, ht)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(500, 500)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setObjectName("centra_lwidget")

        self.vl = QtWidgets.QVBoxLayout(self.central_widget)
        self.init_widgets()

    def init_widgets(self) -> None:
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
        self.btn_3.setShortcut('F2')
        self.btn_3.clicked.connect(self.open_help)
        self.vl.addWidget(self.btn_3)

        self.helper = HelperInteractive(self, 'd:\Python\AlfaServis\Constructor\projects\copy_assembly')
        self.helper.load_config(r'D:\Python\AlfaServis\Constructor\projects\copy_assembly\resources\config_helper_interactive.json')
        self.helper.show()

    def open_help(self) -> None:
        self.helper.show()
    
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        return super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if key == QtCore.Qt.Key.Key_Escape and self.helper.isVisible():
            self.helper.close()
        if key == QtCore.Qt.Key.Key_CapsLock:
            self.helper.next_step()
        return super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        if self.helper.isVisible():
            self.helper.resize(self.size())
        return super().resizeEvent(event)

    def moveEvent(self, a0):
        return super().moveEvent(a0)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())