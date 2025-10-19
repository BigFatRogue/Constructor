import sys
import os
import json
from typing import Union

from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    # Для тестирования модуля
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import ICO_FOLDER, PROJECT_ROOT
from ca_widgets.h_line_separate import QHLineSeparate
from ca_widgets.messege_box_question import MessegeBoxQuestion
from ca_functions.RowCounter import RowCounter



class ToolTipMessage(QtWidgets.QWidget): 
    signal_next_step = QtCore.pyqtSignal()
    signal_end = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.old_pos: QtCore.QPoint = None
        self.new_pos: QtCore.QPoint = None
        self.flag_move = False

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.installEventFilter(self)
        self.initWidgets()
    
    def initWidgets(self) -> None:
        self.setStyleSheet('''
                           ToolTipMessage {
                           background-color: white;
                           border: 3px solid #0078d4;
                           border-radius: 5px;
                           padding: 10px;
                           }''')
        self.setMinimumSize(100, 100)
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.grid_layout)

        row_counter = RowCounter()

        self.label_title = QtWidgets.QLabel(self)
        self.label_title.setMaximumHeight(20)
        self.label_title.setObjectName('label_title')
        self.label_title.setStyleSheet('#label_title {}')
        self.grid_layout.addWidget(self.label_title, row_counter.value, 0, 1, 1)

        self.btn_end_tour = QtWidgets.QPushButton(self)
        self.btn_end_tour.setObjectName('btn_end_tour')
        self.btn_end_tour.setMaximumSize(20, 20)
        self.btn_end_tour.setToolTip('Завершить')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_red_close.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_end_tour.setIcon(icon)
        self.btn_end_tour.setStyleSheet('''
                                        #btn_end_tour {
                                        border: none;
                                        border-radius: 5px;
                                        padding: 7px;
                                        }
                                        #btn_end_tour:hover {
                                        background-color: rgb(209, 235, 255);
                                        }
                                        ''')
        self.btn_end_tour.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_end_tour.clicked.connect(self.end)
        self.grid_layout.addWidget(self.btn_end_tour, row_counter.value, 1, 1, 1)

        self.line_separate = QHLineSeparate(self)
        self.grid_layout.addWidget(self.line_separate, row_counter.next(), 0, 1, 2)

        self.label_message = QtWidgets.QLabel(self)
        self.label_message.setObjectName('label_message')
        self.label_message.setWordWrap(True)
        self.label_message.setStyleSheet('''
                                        #label_message {
                                        font-size: 12pt; 
                                        }
                                        ''')
        self.label_message.setMinimumWidth(250)
        self.grid_layout.addWidget(self.label_message, row_counter.next(), 0, 1, 2)

        self.label_content = QtWidgets.QLabel(self)
        self.grid_layout.addWidget(self.label_content, row_counter.next(), 0, 1, 2)

        self.btn_next_step = QtWidgets.QPushButton(self)
        self.btn_next_step.setText('Продолжить')
        self.btn_next_step.setObjectName('btn_next_step')
        self.btn_next_step.clicked.connect(self.next_step)
        self.grid_layout.addWidget(self.btn_next_step, row_counter.next(), 0, 1, 2)
    
    def set_text(self, title: str, text: str, content_path: str, button_is_wait=False) -> None:
        self.label_title.setText(title)
        self.label_message.setText(text)
        
        if content_path:
            gif = QtGui.QMovie(content_path)
            gif.setScaledSize(QtCore.QSize(100, 100))
            self.label_content.setMovie(gif)
            self.label_content.setMaximumSize(100, 100)
            gif.start()
        else:
            self.label_content.clear()

        if button_is_wait:
            self.btn_next_step.setEnabled(False)
            self.btn_next_step.setText('Ожидание..')
        else:
            self.btn_next_step.setEnabled(True)
            self.btn_next_step.setText('Продолжить')
        
        self.adjustSize()
    
    def set_pos(self, point: QtCore.QPointF) -> None:
        self.setGeometry(int(point.x()), int(point.y()), self.width(), self.height()) 

    def next_step(self) -> None:
        self.signal_next_step.emit()

    def end(self) -> None:
        self.signal_end.emit()

    def eventFilter(self, obj, event):
        tp = event.type()
        if tp == 2:
            self.old_pos = event.pos()
            self.flag_move == True
        elif tp == 3:
            self.flag_move == False
        if tp == 5:
            self.new_pos = event.pos()
            pos = self.geometry().topLeft() + (self.new_pos - self.old_pos)
            self.set_pos(pos)

        return super().eventFilter(obj, event)


class WidgetBackground(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.resize(parent.size())

        self.list_widgets: list[QtWidgets.QWidget] = []
        self.highlight_rect = QtCore.QRectF()
    
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
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(self.rect()))
        path.addRoundedRect(self.highlight_rect, 5, 5)
       
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(0, 0, 0, 180)))
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 50, 50), 2))
        
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        painter.end()

    def resizeEvent(self, event):
        self.highlight_step()
        return super().resizeEvent(event)


class HelperInteractive:
    def __init__(self, parent: QtWidgets.QWidget):
        self.parent = parent
        self.__is_visible = False

        self.dict_data: dict[int, dict[dict[str, list]]] = None
        self.curent_index_step = 0

        self.widget_background = WidgetBackground(parent)
        self.widget_tool_tip = ToolTipMessage(parent)
        self.widget_tool_tip.signal_next_step.connect(self.next_step)
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

    def add_step(self, widgets: list[QtWidgets.QWidget], message: str, content_path: str='', button_is_wait=False) -> None:
        if self.dict_data is None:
            return
        
        self.dict_data[len(self.dict_data) ] = {
            'widgets': widgets, 
            'message': message, 
            'content_path': content_path, 
            'button_is_wait': button_is_wait
            }

    def next_step(self) -> None:
        if self.dict_data is None:
            return

        if self.curent_index_step + 1 < len(self.dict_data):
            self.curent_index_step += 1
        self.widget_background.set_list_widget(self.dict_data[str(self.curent_index_step)]['widgets'])
        self.widget_tool_tip.set_text(title=f'Шаг {self.curent_index_step + 1}', 
                                      text=self.dict_data[str(self.curent_index_step)]['message'], 
                                      content_path=self.dict_data[str(self.curent_index_step)]['content_path'],
                                      button_is_wait=self.dict_data[str(self.curent_index_step)]['button_is_wait'])
       
        self.enable_event_widgets()
        self.desable_event_widgets()

        self.widget_tool_tip.set_pos(self.calc_pos_tool_tiip())
        
        self.widget_background.update()
        
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

            return QtCore.QPointF(x, y)
        else:
            return QtCore.QPointF((self.parent.width() - self.widget_tool_tip.width())/2, (self.parent.height() - self.widget_tool_tip.height())/2)

    def isVisible(self) -> bool:
        return self.__is_visible       

    def show(self) -> None:
        if self.dict_data is None:
            return

        self.__is_visible = True
        self.desable_event_widgets()

        self.widget_background.set_list_widget(self.dict_data[str(self.curent_index_step)]['widgets'])
        self.widget_tool_tip.set_text(title=f'Шаг {self.curent_index_step + 1}', 
                                      text=self.dict_data[str(self.curent_index_step)]['message'], 
                                      content_path=self.dict_data[str(self.curent_index_step)]['content_path'],
                                      button_is_wait=self.dict_data[str(self.curent_index_step)]['button_is_wait'])
        self.widget_tool_tip.set_pos(self.calc_pos_tool_tiip())

        self.widget_background.show()
        self.widget_tool_tip.show()
        
    def hide(self) -> None:
        self.__is_visible = False
        self.curent_index_step = 0
        self.enable_event_widgets()
        self.widget_background.hide()
        self.widget_tool_tip.hide()
    
    def close(self) -> None:
        mbq = MessegeBoxQuestion(self.parent, title='Завершить', question='Завершить показ интерактивной спраки?')
        if mbq.exec() == QtWidgets.QDialog.Accepted:
            self.hide()

    def resize(self, size) -> None:
        self.widget_background.resize(size)

    
    def delete(self) -> None:
        del self.widget_background
        del self.widget_tool_tip


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

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
        self.btn_3.setShortcut('F2')
        self.btn_3.clicked.connect(self.open_help)
        self.vl.addWidget(self.btn_3)

        self.helper = HelperInteractive(self)
        self.helper.load_config(os.path.join(os.path.dirname(__file__), 'config_helper_interactive.json'))
        self.helper.hide()
        # self.helper.add_step([], 'Программа предназначена для копирование сборок Autodesk Inventor с возможностью переименования файлов и компонентов')
        # self.helper.add_step([self.btn_1], 'Шаг 1', os.path.join(ICO_FOLDER, 'gif.gif'), False)
        # self.helper.add_step([self.btn_2], 'Шаг 2')
        # self.helper.show()
    
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


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())