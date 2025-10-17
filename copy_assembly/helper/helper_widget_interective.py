import sys
from PyQt5 import QtCore, QtWidgets, QtGui


class ToolTipMessage(QtWidgets.QWidget): 
    signal_next_step = QtCore.pyqtSignal()
    signal_end = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.initWidgets()
    
    def initWidgets(self) -> None:
        # self.resize(100, 100)
        self.setMinimumSize(150, 100)
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.grid_layout)

        self.label_message = QtWidgets.QLabel(self)
        self.label_message.setWordWrap(True)
        self.label_message.setMinimumWidth(200)
        self.grid_layout.addWidget(self.label_message, 0, 0, 1, 1)

        self.btn_next_step = QtWidgets.QPushButton(self)
        self.btn_next_step.setText('Продолжить')
        self.btn_next_step.setObjectName('btn_next_step')
        self.btn_next_step.clicked.connect(self.next_step)
        self.grid_layout.addWidget(self.btn_next_step, 1, 0, 1, 1)
        
        self.btn_end_tour = QtWidgets.QPushButton(self)
        self.btn_end_tour.setText('Завершить')
        self.btn_end_tour.clicked.connect(self.end)
        self.grid_layout.addWidget(self.btn_end_tour, 1, 1, 1, 1)

    def next_step(self) -> None:
        self.signal_next_step.emit()

    def end(self) -> None:
        self.signal_end.emit()

    def add_message(self, text: str) -> None:
        self.label_message.setText(text)
    
    def set_pos(self, point: QtCore.QPointF) -> None:
        self.setGeometry(int(point.x()), int(point.y()), self.width(), self.height()) 


class WidgetBackground(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.resize(parent.size())

        self.list_widgets: list[QtWidgets.QWidget] = []
        self.highlight_rect = QtCore.QRectF()
    
    def add_widgets(self, widgets: list[QtWidgets.QWidget]) -> None:
        self.list_widgets = widgets
        self.highlight_step()

    def highlight_step(self) -> None:
        x0 = y0 = x1 = y1 = 0
        for widget in self.list_widgets:
            x0_widget, y0_widget = widget.mapTo(self.parent(), QtCore.QPoint(0, 0)).x(), widget.mapTo(self.parent(), QtCore.QPoint(0, 0)).y()
            width, heigth = widget.size().width(), widget.size().height()
            x1_widget, y1_widget = x0_widget + width, y0_widget + heigth
                        
            if x0 == y0 == x1 == y1 == 0:
                x0, y0, x1, y1 =  x0_widget, y0_widget, x1_widget, y1_widget
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
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(self.rect()))
        # self.highlight_widgets()
        path.addRoundedRect(self.highlight_rect, 5, 5)
       
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(0, 0, 0, 180)))
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 50, 50), 2))
        
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        painter.end()

    def resizeEvent(self, event):
        self.highlight_step()
        return super().resizeEvent(event)


class HelperInteractive:
    def __init__(self, parent):
        self.parent = parent
        self.__is_visible = False

        self.list_widgets: list[tuple[list[QtWidgets.QWidget], str]] = []
        self.list_message: list[str] = []
        self.curent_index_step = 0

        self.widget_background = WidgetBackground(parent)
        self.widget_tool_tip = ToolTipMessage(parent)
        self.widget_tool_tip.setObjectName('widget_tool_tip')
        self.widget_tool_tip.setStyleSheet('''
            #widget_tool_tip {
                background-color: white;
                border: 1px solid black;
                border-radius: 5px;
            }
        ''')
        self.widget_tool_tip.signal_next_step.connect(self.next_step)
        self.widget_tool_tip.signal_end.connect(self.hide)

    def add_step(self, step: list[QtWidgets.QWidget], message: str) -> None:
        self.list_widgets.append(step)
        self.list_message.append(message)

    def next_step(self) -> None:
        if self.curent_index_step + 1 < len(self.list_widgets):
            self.curent_index_step += 1
        self.widget_background.add_widgets(self.list_widgets[self.curent_index_step])
        rect = self.widget_background.highlight_rect
        point = QtCore.QPointF(rect.x() + int(rect.width() * 0.1), rect.y() + rect.height())
        self.widget_tool_tip.set_pos(point)
        self.widget_background.update()
        
    def desable_event_widgets(self, parent=None) -> None:
        if parent is None:
            parent = self.parent
        for child in parent.children():
            if child == self.widget_tool_tip:
                continue
            if isinstance(child, (QtWidgets.QPushButton, QtWidgets.QLineEdit, QtWidgets.QCheckBox, QtWidgets.QMenuBar)) and child not in self.list_message:
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
                child.setFocusPolicy(QtCore.Qt.NoFocus)
            self.desable_event_widgets(child)

    def enable_event_widgets(self, parent=None) -> None:
        if parent is None:
            parent = self.parent
        for child in parent.children():
            if isinstance(child, (QtWidgets.QPushButton, QtWidgets.QLineEdit, QtWidgets.QCheckBox, QtWidgets.QMenuBar)):
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
                child.setFocusPolicy(QtCore.Qt.StrongFocus)
            self.enable_event_widgets(child)

    def isVisible(self) -> bool:
        return self.__is_visible       

    def show(self) -> None:
        self.__is_visible = True
        self.desable_event_widgets()

        self.widget_background.add_widgets(self.list_widgets[self.curent_index_step])
        self.widget_background.show()
        
        self.widget_tool_tip.add_message(self.list_message[self.curent_index_step])
        self.widget_tool_tip.show()
        rect = self.widget_background.highlight_rect
        point = QtCore.QPointF(rect.x() + int(rect.width() * 0.1), rect.y() + rect.height())
        self.widget_tool_tip.set_pos(point)
    
    def hide(self) -> None:
        self.__is_visible = False
        self.curent_index_step = 0
        self.enable_event_widgets()

        self.widget_background.hide()
        self.widget_tool_tip.hide()
    
    def resize(self, size) -> None:
        self.widget_background.resize(size)


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
        self.helper.hide()
        self.helper.add_step([self.btn_1], 'Шаг 1')
        self.helper.add_step([self.btn_2], 'Шаг 2')
        # self.helper.show()
    
    def open_help(self) -> None:
        self.helper.show()
    
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        print(key)
        if key == QtCore.Qt.Key.Key_Escape and self.helper.isVisible():
            self.helper.hide()
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