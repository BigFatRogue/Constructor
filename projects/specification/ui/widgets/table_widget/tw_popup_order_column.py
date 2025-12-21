import os 
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.app_context.app_context import SETTING, ENUMS


class PopupOrder(QtWidgets.QWidget):
    signal_sorted = QtCore.pyqtSignal(ENUMS.STATE_SORTED_COLUMN)

    def __init__(self, parent):
        super().__init__(parent)
        self.current_button_header: QtWidgets.QPushButton = None
        self.is_multi_sorted = False
        self.curent_column_index: int = None
        self.data_index: int = None

        self.is_left_click = False
        self.is_move = False
        self.old_pos = QtCore.QPoint(0, 0)

        self.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.init_widgets()
        self.hide()

    def init_widgets(self) -> None:
        self.setMouseTracking(True)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.v_layout)
        self.setStyleSheet('QFrame {border: 1px solid black; border-radius: 3px; background-color: white;}')
        
        self.frame = QtWidgets.QFrame(self)
        self.v_layout_frame = QtWidgets.QVBoxLayout(self.frame)
        self.v_layout_frame.setContentsMargins(2, 2, 2, 2)
        self.v_layout_frame.setSpacing(2)
        self.v_layout.addWidget(self.frame)
        
        self.btn_sorted = QtWidgets.QPushButton(self.frame)
        self.btn_sorted.setText('Сортировать от А до Я')
        ico = QtGui.QIcon()
        ico.addFile(os.path.join(SETTING.ICO_FOLDER, 'sorted_az.png'))
        self.btn_sorted.setIcon(ico)
        self.btn_sorted.clicked.connect(self.click_btn_sorted)
        self.v_layout_frame.addWidget(self.btn_sorted)

        self.btn_sorted_reverse = QtWidgets.QPushButton(self.frame)
        self.btn_sorted_reverse.setText('Сортировать от Я до А]')
        ico = QtGui.QIcon()
        ico.addFile(os.path.join(SETTING.ICO_FOLDER, 'sorted_za.png'))
        self.btn_sorted_reverse.setIcon(ico)
        self.btn_sorted_reverse.clicked.connect(self.click_btn_sorted_reverse)
        self.v_layout_frame.addWidget(self.btn_sorted_reverse)

        self.check_box_multi_sorted = QtWidgets.QCheckBox(self.frame)
        self.check_box_multi_sorted.setText('Группировка по нескольким столцам')
        self.check_box_multi_sorted.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.check_box_multi_sorted.clicked.connect(self.click_check_box_multi_sorted)
        self.v_layout_frame.addWidget(self.check_box_multi_sorted)

    def set_column_index(self, index: int) -> None:
        self.curent_column_index = index

    def set_pos(self) -> None:
        button_global_pos = self.current_button_header.mapToGlobal(QtCore.QPoint(0, 0))
        geom = self.current_button_header.geometry()
        
        h = geom.height()
        x = button_global_pos.x()
        y = button_global_pos.y() + h

        if not self.is_left_click:
            y += h
            if x + self.width() > self.parent().width():
                x = self.parent().width() - self.width() - 10
            if y + self.height()  > self.parent().height():
                y = self.parent().height() - self.height() - 10
        self.setGeometry(x, y, self.width(), self.height())

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Escape:
            self.hide()
        return super().keyPressEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.RightButton:
            self.is_move = True
            self.old_pos = event.pos()
        if event.button() == QtCore.Qt.LeftButton:
            self.is_left_click = True
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.RightButton:
            self.is_move = False
        if event.button() == QtCore.Qt.LeftButton:
            self.is_left_click = False
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.is_move:
            pos = self.geometry().topLeft() + (event.pos() - self.old_pos)
            self.setGeometry(pos.x(), pos.y(), self.width(), self.height()) 
        return super().mouseMoveEvent(event)
    
    def eventFilter(self, obj, event):
        """Фильтр событий для отслеживания кликов вне окна"""
        if event.type() == QtCore.QEvent.MouseButtonPress:
            print(event)
            if not self.geometry().contains(event.globalPos()):
                self.close()
                return True
        return super().eventFilter(obj, event)

    def show(self, button: QtWidgets.QPushButton) -> None:
        super().show()
        if self.current_button_header:
            self.current_button_header.setChecked(False)
        self.current_button_header = button
        self.current_button_header.setChecked(True)
        self.set_pos()
        self._set_state_btns_sorted()
        
    def _set_state_btns_sorted(self) -> None:
        state_sorted = self.current_button_header.state_sorted
        if state_sorted == ENUMS.STATE_SORTED_COLUMN.EMPTY:
            self.btn_sorted.setChecked(False)
            self.btn_sorted_reverse.setChecked(False)
        elif state_sorted == ENUMS.STATE_SORTED_COLUMN.SORTED:
            self.btn_sorted.setChecked(True)
            self.btn_sorted_reverse.setChecked(False)
        elif state_sorted == ENUMS.STATE_SORTED_COLUMN.REVERSE:
            self.btn_sorted.setChecked(False)
            self.btn_sorted_reverse.setChecked(True)

    def hideEvent(self, a0):
        if self.current_button_header:
            self.current_button_header.setChecked(False)

    def click_btn_sorted(self) -> None:
        if self.current_button_header.state_sorted == ENUMS.STATE_SORTED_COLUMN.SORTED:
            self.set_state_button_sorted(ENUMS.STATE_SORTED_COLUMN.EMPTY)
        else:
            self.set_state_button_sorted(ENUMS.STATE_SORTED_COLUMN.SORTED)
            self.signal_sorted.emit(ENUMS.STATE_SORTED_COLUMN.SORTED)
    
    def click_btn_sorted_reverse(self) -> None:
        if self.current_button_header.state_sorted == ENUMS.STATE_SORTED_COLUMN.REVERSE:
            self.set_state_button_sorted(ENUMS.STATE_SORTED_COLUMN.EMPTY)
        else:
            self.set_state_button_sorted(ENUMS.STATE_SORTED_COLUMN.REVERSE)
            self.signal_sorted.emit(ENUMS.STATE_SORTED_COLUMN.REVERSE)
    
    def click_check_box_multi_sorted(self, value) -> None:
        self.is_multi_sorted = value
        self.btn_sorted.setCheckable(value)
        self.btn_sorted_reverse.setCheckable(value)
    
    def set_state_button_sorted(self, state) -> None:
        if self.is_multi_sorted:
            self.current_button_header.set_sorted_state(state)
            self.btn_sorted.setChecked(state == ENUMS.STATE_SORTED_COLUMN.SORTED)
            self.btn_sorted_reverse.setChecked(state == ENUMS.STATE_SORTED_COLUMN.REVERSE)
        else: 
            self.current_button_header.set_sorted_state(ENUMS.STATE_SORTED_COLUMN.EMPTY)