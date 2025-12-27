import os
from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.config.app_context import SETTING, ENUMS, DATACLASSES

from projects.specification.ui.widgets.table_widget.tw_header import HeaderWithOverlayWidgets
from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable

from projects.specification.config.app_context import SETTING, ENUMS


class PopupOrder(QtWidgets.QWidget):
    signal_sorted = QtCore.pyqtSignal(ENUMS.STATE_SORTED_COLUMN)

    def __init__(self, parent):
        super().__init__(parent)
        self.current_button_header: ButtonHorizontalHeader = None
        self.is_multi_sorted = False

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
        self.btn_sorted.clicked.connect(self._click_btn_sorted)
        self.v_layout_frame.addWidget(self.btn_sorted)

        self.btn_sorted_reverse = QtWidgets.QPushButton(self.frame)
        self.btn_sorted_reverse.setText('Сортировать от Я до А]')
        ico = QtGui.QIcon()
        ico.addFile(os.path.join(SETTING.ICO_FOLDER, 'sorted_za.png'))
        self.btn_sorted_reverse.setIcon(ico)
        self.btn_sorted_reverse.clicked.connect(self._click_btn_reverse)
        self.v_layout_frame.addWidget(self.btn_sorted_reverse)

        self.check_box_multi_sorted = QtWidgets.QCheckBox(self.frame)
        self.check_box_multi_sorted.setText('Группировка по нескольким столцам')
        self.check_box_multi_sorted.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.check_box_multi_sorted.clicked.connect(self.click_check_box_multi_sorted)
        self.v_layout_frame.addWidget(self.check_box_multi_sorted)

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

    def hideEvent(self, event):
        if self.current_button_header:
            self.current_button_header.setChecked(False)
            self.is_move = False
    
    def _click_btn_sorted(self) -> None:
        if self.current_button_header.state_sorted == ENUMS.STATE_SORTED_COLUMN.SORTED:
            self.set_state_button_sorted(ENUMS.STATE_SORTED_COLUMN.EMPTY)
        else:
            self.set_state_button_sorted(ENUMS.STATE_SORTED_COLUMN.SORTED)
            self.signal_sorted.emit(ENUMS.STATE_SORTED_COLUMN.SORTED)
    
    def _click_btn_reverse(self) -> None:
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

    def set_is_multi_sort(self, value: bool) -> None:
        self.is_multi_sorted = value
        self.check_box_multi_sorted.setCheckState(QtCore.Qt.CheckState.Checked if value else QtCore.Qt.CheckState.Unchecked)

class ButtonHorizontalHeader(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__(parent)

        self.index_section: int = None
        self.is_checked = False
        self.state_sorted = ENUMS.STATE_SORTED_COLUMN.EMPTY 

        self.resize(22, 22)
        self.setCheckable(True)
        
        self.dict_icon = {}
        for icon_name, state, tool_tip in zip(
            ('filter.png', 'filter_az.png', 'filter_za.png'),
            (ENUMS.STATE_SORTED_COLUMN.EMPTY, ENUMS.STATE_SORTED_COLUMN.SORTED, ENUMS.STATE_SORTED_COLUMN.REVERSE),
            ('Установить фильтр', 'Установлен фильтр от А до Я', 'Установлен фильтр от Я до А')
            ):

            ico = QtGui.QIcon()
            ico.addFile(os.path.join(SETTING.ICO_FOLDER, icon_name))
            self.dict_icon[state] = (ico, tool_tip)

        self.reset_view_sorted()

    def reset_view_sorted(self) -> None:
        self.set_sorted_state(ENUMS.STATE_SORTED_COLUMN.EMPTY)

    def set_sorted_state(self, state: ENUMS.STATE_SORTED_COLUMN) -> None:
        """
        Установка отображения состояния сортировки.Можно передать int, так как и БД приходит int
        """
        if isinstance(state, int):
            for st in ENUMS.STATE_SORTED_COLUMN:
                if st.value == state:
                    state = st
                    break

        self.state_sorted = state
        ico, tool_tip = self.dict_icon[state]
        self.setIcon(ico)
        self.setToolTip(tool_tip)
    

class HorizontalWithOverlayWidgets(HeaderWithOverlayWidgets):
    signal_change = QtCore.pyqtSignal()

    def __init__(self, table_view: QtWidgets.QTableWidget, range_zoom):
        super().__init__(QtCore.Qt.Orientation.Horizontal, table_view, range_zoom)
        self.widgets: list[ButtonHorizontalHeader]

        table_view.horizontalScrollBar().valueChanged.connect(self._update_widgets)

        self._state_column_sorted: tuple[int, ...] | list [int] = None
        self.popup_order = PopupOrder(self.table_view)
        self.popup_order.signal_sorted.connect(self._set_state_column_sorted)
    
    def set_table_model(self, table_model):
        super().set_table_model(table_model)
        self._set_size_section()
        
    def _set_size_section(self) -> None:
        """
        Установка параметров заголовка из item_data

        Если в item_data ещё нет параметров, то они будут заданны из заголовка
        
        :param self: Описание
        """
        if self._table_model.item_data.horizontal_header_data:
            for data in self._table_model.item_data.horizontal_header_data:
                self.resizeSection(data.column, data.size)
        else:
            headers: list[DATACLASSES.DATA_HEADERS] = []
            for i in range(self.count()):
                header_data = DATACLASSES.DATA_HEADERS(-1, i, self.sectionSize(i), self.isVisible())
                headers.append(header_data)
            self._table_model.item_data.horizontal_header_data = headers

    def set_widget(self, align: int=2) -> None:
        self._align_widget = align

        count_widgets = len(self.widgets)
        count_section = self.count()

        for widget in self.widgets:
            widget.show()

        if count_section > count_widgets:
            for i in range(count_widgets, count_section):
                btn_order = ButtonHorizontalHeader(self.table_view)
                btn_order.setVisible(True)
                btn_order.raise_()
                btn_order.index_section = i
                btn_order.clicked.connect(self._show_popup)
                self.widgets.append(btn_order)
        
        elif count_widgets > count_section:
            for widget in self.widgets[count_widgets - count_section:]:
                widget.hide()
        
        self._set_parameters_widget()
        self._update_widgets()

    def _set_parameters_widget(self) -> None:
        """
        Установка параметров заголовка из item_data

        Если в item_data ещё нет параметров, то они будут заданны из заголовка
        
        :param self: Описание
        """
        horizontal_header_data = self._table_model.item_data.horizontal_header_data
        if horizontal_header_data:
            column_sorted: dict[int, int] = {}
            for i, data in enumerate(horizontal_header_data):
                self.widgets[data.column].reset_view_sorted()
                state_sorted = data.parameters.get(ENUMS.PARAMETERS_HEADER.STATE_SORTED.name)
                if state_sorted is not None:
                    if state_sorted != 0:
                        column_sorted[i] = state_sorted
            
            is_multi_sort = len(column_sorted) > 1
            if is_multi_sort:
                for i, state in column_sorted.items():
                    self.widgets[i].set_sorted_state(state)

            self.popup_order.set_is_multi_sort(is_multi_sort)

    def _show_popup(self) -> None:
        """
        Показ окна настройки сортировки
        """
        self.popup_order.show(self.sender())
    
    def _set_state_column_sorted(self, state: ENUMS.STATE_SORTED_COLUMN) -> None:
        if self._table_model:
            """
            Сортировка столбцов
            """
            btn: ButtonHorizontalHeader = self.popup_order.current_button_header
            column = btn.index_section
            is_multi_sorted = self.popup_order.is_multi_sorted

            state_column_sorted = None
            if is_multi_sorted:
                state_column_sorted = [btn.state_sorted for btn in self.widgets]
            else:
                state_column_sorted = [ENUMS.STATE_SORTED_COLUMN.EMPTY] * self.count()
                for btn in self.widgets:
                    btn.set_sorted_state(ENUMS.STATE_SORTED_COLUMN.EMPTY)
                state_column_sorted[column] = state
            
            self._table_model.sorted_column(state_column_sorted)
            self.signal_change.emit()
    
    

        
            