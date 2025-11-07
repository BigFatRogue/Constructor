from PyQt5 import QtCore, QtGui, QtWidgets



class CustomItemComboBox(QtWidgets.QLabel):
    signal_is_drag = QtCore.pyqtSignal(bool)
    signal_current_index = QtCore.pyqtSignal(int)
    signal_curent_y = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.index: int = 0
        self.is_move = False
        self.old_pos_y = 0
        self.start_y = 0
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
    
    def __move_y(self, dy: int) -> None:
        new_y = self.y() + dy
        if 0 < new_y < self.parent().height() - self.height(): 
            self.signal_curent_y.emit(new_y)
            self.setGeometry(self.x(), new_y, self.width(), self.height())
        
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.signal_current_index.emit(self.index)
            self.signal_is_drag.emit(True)
            self.is_move = True
            self.old_pos_y = event.pos().y()
            self.start_y = self.y()
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.signal_is_drag.emit(False)
            self.is_move = False
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.is_move:
            self.raise_()
            y = event.pos().y() - self.old_pos_y 
            self.__move_y(y)


class CustomComboBox(QtWidgets.QWidget):
    signal_select_item = QtCore.pyqtSignal(tuple)
    signal_is_swap_item = QtCore.pyqtSignal(tuple)

    def __init__(self, parent):
        super().__init__(parent)
        self.is_drag_item: bool = False
        self.current_item_index: int = 0
        self.start_drag_index: int = None
        self.end_drag_index: int = None
        self.has_swap = False
        self.is_show_list = False
        self.seek_index = 0

        self.list_item: list[QtWidgets.QLabel] = []
        
        self.custom_heigth = 20
        
        self.init_widgets()
    
    def init_widgets(self) -> None:
        self.setMouseTracking(True)
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)
        self.setLayout(self.grid_layout)

        self.lineedit = QtWidgets.QLineEdit(self)
        self.lineedit.setReadOnly(True)
        self.lineedit.setMinimumHeight(self.custom_heigth)
        self.lineedit.setMaximumHeight(self.custom_heigth)
        self.lineedit.mousePressEvent = self.mouseMoveEvent
        self.grid_layout.addWidget(self.lineedit, 0, 0, 1, 1)

        self.btn_toggle = QtWidgets.QPushButton(self)
        self.btn_toggle.setText('▼')
        self.btn_toggle.setMinimumSize(self.custom_heigth, self.custom_heigth)
        self.btn_toggle.setMaximumSize(self.custom_heigth, self.custom_heigth)
        self.btn_toggle.clicked.connect(self.toggle_view_list)
        self.grid_layout.addWidget(self.btn_toggle, 0, 1, 1, 1)

        self.frame_items = QtWidgets.QFrame(self)
        self.frame_items.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_items.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self.frame_items.leaveEvent = self.leaveEvent
        self.frame_items.enterEvent = self.enterEvent

        self.vl_frame_items = QtWidgets.QVBoxLayout(self.frame_items)
        self.vl_frame_items.setContentsMargins(0, 0, 0, 0)
        self.vl_frame_items.setSpacing(0)

        self.setStyleSheet("""
        QLineEdit, QPushButton, QLabel {
            border: none;
            background-color: white;
        }
        QPushButton:hover {
            background-color: #e0effe;
        }
        QLabel {
            border: none;
        }    
        QLabel:hover {
            background-color: #e0effe;
        }                    
        """)

    def text(self) -> str:
        return self.lineedit.text()

    def setCurrentIndex(self, index: int) -> None:
        if index is not None:
            if 0 <= index < len(self.list_item):
                self.current_item_index = index
                self.lineedit.setText(self.list_item[index].text())
            else:
                raise IndexError

    def addItem(self, text: str) -> None:
        if self.seek_index < len(self.list_item):
            item = self.list_item[self.seek_index]
            item.setText(text)
            item.show()
        else:
            self.__addItem(text)
        self.seek_index += 1
        self.view_curent_item()
    
    def __addItem(self, item: str) -> None:
        label = CustomItemComboBox(self.frame_items)
        label.index = len(self.list_item)
        label.signal_current_index.connect(self.set_drag_index)
        label.signal_is_drag.connect(self.toggle_is_drag_item)
        label.signal_curent_y.connect(self.get_item_from_mouse_pos_y)
        label.setText(item)
        label.setMinimumHeight(self.custom_heigth)
        label.setMaximumHeight(self.custom_heigth)
        self.vl_frame_items.addWidget(label)
        self.list_item.append(label)

        self.frame_items.setMaximumHeight((self.seek_index + 1) * self.custom_heigth)
    
    def view_curent_item(self) -> None:
        if self.current_item_index:
            self.lineedit.setText(self.list_item[self.current_item_index].text())
            if not self.has_swap:
                self.frame_items.hide()
            self.has_swap = False
        
    def toggle_view_list(self) -> None:
        self.has_swap = False

        if self.is_show_list:
            self.frame_items.hide()
            self.is_show_list = False
        else:
            self.show_dropdown()
            self.is_show_list = True
    
    def show_dropdown(self):
        global_pos = self.lineedit.mapToGlobal(QtCore.QPoint(0, self.lineedit.height()))
        self.frame_items.move(global_pos)
        self.frame_items.resize(self.lineedit.width() + self.btn_toggle.width(), self.seek_index * self.custom_heigth)
        self.frame_items.show()
        self.frame_items.raise_()

    def toggle_is_drag_item(self, value: bool) -> None:
        self.is_drag_item = value
        if not value:
            self.current_item_index = self.start_drag_index
            self.__swap_item()          
            self.view_curent_item()
            self.is_show_list = False
            self.signal_select_item.emit((self.current_item_index, self.text()))
            
    def __swap_item(self) -> None:
        if self.end_drag_index is not None:
            drag_item = self.list_item.pop(self.start_drag_index)
            self.list_item.insert(self.end_drag_index, drag_item)

            self.vl_frame_items.removeWidget(drag_item)
            self.vl_frame_items.insertWidget(self.end_drag_index, drag_item)

            drag_item.setGeometry(drag_item.x(), drag_item.start_y, drag_item.width(), drag_item.height())
            self.__update_index()
            self.signal_is_swap_item.emit((self.start_drag_index, self.end_drag_index))
            self.end_drag_index = None
        else:
            if self.start_drag_index is not None:
                drag_item = self.list_item[self.start_drag_index]
                drag_item.setGeometry(drag_item.x(), drag_item.start_y, drag_item.width(), drag_item.height())
        self.start_drag_index = None

    def __update_index(self) -> None:
        self.has_swap = True
        for i, item in enumerate(self.list_item):
            item.index = i

    def set_drag_index(self, index: int) -> None:
        self.start_drag_index = index

    def get_item_from_mouse_pos_y(self, y_drag_item: int) -> None:
        for label in self.list_item:
            y = label.y()
            if y - 10 < y_drag_item < y + 10:
                if label.index != self.start_drag_index:
                    item = self.list_item[self.start_drag_index]
                    item.setGeometry(item.x(), y, item.width(), item.height())
                    label.setGeometry(label.x(), item.start_y, label.width(), label.height())
                    item.start_y = y
                    self.end_drag_index = label.index
    
    def clear(self) -> None:
        self.seek_index = 0
        for item in self.list_item:
            item.setText('')
            item.hide()

    def mousePressEvent(self, event):
        self.toggle_view_list()
        return super().mousePressEvent(event)

    def leaveEvent(self, event):
        self.is_show_list = False
        return super().leaveEvent(event)


if __name__ == '__main__':
    class TestWidget(QtWidgets.QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.init_widget()

        def init_widget(self):
            self.v_layout = QtWidgets.QVBoxLayout(self)
            self.setLayout(self.v_layout)

            self.combo_box = CustomComboBox(self)
            self.populate_combo_box()
            self.combo_box.signal_is_swap_item.connect(self.swap_item)
            self.v_layout.addWidget(self.combo_box)

        def populate_combo_box(self):
            for i in range(1, 10):
                self.combo_box.addItem(f'Элемент {i}')

        def swap_item(self, data):
            self.combo_box.addItem('AAAAAA')
            # for item in self.combo_box.list_item:
                # print(item.text(), item.index, item.y())
            # self.combo_box.clear()
            # self.populate_combo_box()
            # # for item in self.combo_box.list_item:
            # #     print(item.text(), item.index)



    import sys
    app = QtWidgets.QApplication(sys.argv)

    window = TestWidget()
    window.show()
    sys.exit(app.exec_())