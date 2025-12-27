import os
from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.config.app_context import SETTING, ENUMS, DATACLASSES

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable
from projects.specification.ui.widgets.table_widget.tw_header import HeaderWithOverlayWidgets


class CheckBoxVerticalHeader(QtWidgets.QCheckBox):
    signal_signle_choose = QtCore.pyqtSignal(tuple)
    signal_multi_choose = QtCore.pyqtSignal(tuple)

    def __init__(self, parent):
        super().__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setMouseTracking(True)
        self.index_section: int = 0
        self.is_shift = False
        self.clicked.connect(self.choose_row)

    def choose_row(self) -> None:
        state: bool = True if self.checkState() == QtCore.Qt.CheckState.Checked else False
        if self.is_shift:
            self.signal_multi_choose.emit((self.index_section, state))
        else:
            self.signal_signle_choose.emit((self.index_section, state))

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if event.modifiers() & QtCore.Qt.Modifier.SHIFT:
                self.is_shift = True
            else:
                self.is_shift = False
            
        return super().mousePressEvent(event)
    

class VerticallWithOverlayWidgets(HeaderWithOverlayWidgets):
    signal_change = QtCore.pyqtSignal()

    def __init__(self, table_view: QtWidgets.QTableWidget, range_zoom):
        super().__init__(QtCore.Qt.Orientation.Vertical, table_view, range_zoom)
        table_view.verticalScrollBar().valueChanged.connect(self._update_widgets)
        self.widgets: list[CheckBoxVerticalHeader]

        self._start_row: int = None
        self._end_row: int = None

        self._is_left_press = False
        self._is_shift_press = False
        self._is_ctrl_press = False
        self._multi_select_state = False
        self._active_select_row: int = None

        self.init_contex_menu()

    def init_contex_menu(self) -> None:
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.context_menu = QtWidgets.QMenu(self)

        self.insert_row_up = QtWidgets.QAction(self.context_menu)
        self.insert_row_up.setText('Вставить строчку выше')
        self.context_menu.addAction(self.insert_row_up)

        self.insert_row_down = QtWidgets.QAction(self.context_menu)
        self.insert_row_down.setText('Вставить строчку ниже')
        self.context_menu.addAction(self.insert_row_down)

        self.delete_row = QtWidgets.QAction(self.context_menu)
        self.delete_row.setText('Удалить строчку')
        self.context_menu.addAction(self.delete_row)

    def show_context_menu(self, position: QtCore.QPoint) -> None:
        self._active_select_row = self.logicalIndexAt(position)
        if self._active_select_row != -1:
            self.context_menu.exec_(self.viewport().mapToGlobal(position))

    def set_table_model(self, table_model):
        super().set_table_model(table_model)
        self._set_size_section()
        
    def _set_size_section(self) -> None:
        """
        Установка параметров заголовка из item_data

        Если в item_data ещё нет параметров, то они будут заданны из заголовка
        
        :param self: Описание
        """
        if self._table_model.item_data.vertical_header_data:
            for data in self._table_model.item_data.vertical_header_data:
                self.resizeSection(data.row, data.size)
        else:
            headers: list[DATACLASSES.DATA_HEADERS] = []
            for i in range(self.count()):
                header_data = DATACLASSES.DATA_HEADERS(i, -1, self.sectionSize(i), self.isVisible())
                headers.append(header_data)
            self._table_model.item_data.vertical_header_data = headers

    def set_widget(self, align: int=2):
        self._align_widget = align

        count_widgets = len(self.widgets)
        count_section = self.count()

        for widget in self.widgets:
            widget.show()

        if count_section > count_widgets:
            for i in range(count_widgets, count_section):
                check_box = CheckBoxVerticalHeader(self.table_view)
                check_box.setVisible(True)
                check_box.raise_()
                check_box.index_section = i
                check_box.signal_signle_choose.connect(self.signle_choose)
                check_box.signal_multi_choose.connect(self.signal_multi_choose)
                self.widgets.append(check_box)

                fm = self.fontMetrics()
                text_w = fm.horizontalAdvance(str(i))
                width = check_box.width()
                self.setMinimumWidth(self.sectionSize(i) + text_w + width)
        
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

        if self._table_model.item_data.vertical_header_data:
            for i, data in enumerate(self._table_model.item_data.vertical_header_data):
                state = data.parameters.get(ENUMS.PARAMETERS_HEADER.SELECT_ROW.name)
                if state is not None:
                    self.widgets[i].setCheckState(QtCore.Qt.CheckState.Checked if state else QtCore.Qt.CheckState.Unchecked)
                else:
                    self.widgets[i].setCheckState(QtCore.Qt.CheckState.Unchecked)
                    data.parameters[ENUMS.PARAMETERS_HEADER.SELECT_ROW.name] = False

    def fill_row(self, row: int, state: bool) -> None:
        if self._table_model:
            self._table_model.select_row(row, state)   

    def signle_choose(self, value: tuple[int, bool]) -> None:
        row, state = value
        self._start_row = row
        self.fill_row(row, state)

        if not state:
            self._start_row = None 
            self._end_row = None
        self.signal_change.emit()
        
    def signal_multi_choose(self, value: tuple[int, bool]) -> None:
        row, state = value

        if self._start_row is None:
            self._start_row = row
        else:
            self._end_row = row
        
        if self._end_row is not None:
            if self._start_row > self._end_row:
                self._start_row, self._end_row = self._end_row, self._start_row

            for i in range(self._start_row, self._end_row + 1):
                check_box: CheckBoxVerticalHeader = self.widgets[i]
                if not check_box.checkState() or i == self._end_row or i == self._start_row:
                    check_box.setChecked(True)
                    self.fill_row(i, True)
        self.signal_change.emit()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() & QtCore.Qt.MouseButton.LeftButton:
            if event.modifiers() & QtCore.Qt.Modifier.SHIFT and event.modifiers() & ~QtCore.Qt.Modifier.CTRL:
                self._is_left_press = True
                self._is_shift_press = True
                self._is_ctrl_press = False
                self._multi_select_state = True
            if event.modifiers() & ~QtCore.Qt.Modifier.SHIFT and event.modifiers() & QtCore.Qt.Modifier.CTRL:
                self._is_left_press = True
                self._is_shift_press = False
                self._is_ctrl_press = True
                self._multi_select_state = False

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() & QtCore.Qt.MouseButton.LeftButton:
            self._is_left_press = False
            self._is_shift_press = False
            self._is_ctrl_press = False
            self._multi_select_state = False

        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._is_left_press:
            if self.widgets:
                row = self.logicalIndexAt(event.pos())

                if self._active_select_row is None:
                    self.select_row_press_mouse(row)
                if self._active_select_row != row:
                    self.select_row_press_mouse(row)

        return super().mouseMoveEvent(event)
    
    def select_row_press_mouse(self, row: int) -> None:
        """
        Выбор ячеек введение зажатой ЛКМ по секциям (не по чек боксам)
        
        :param self: Описание
        :param pos: Описание
        :type pos: QtCore.QPoint
        """
        self._active_select_row = row
        check_box = self.widgets[row]
        state = QtCore.Qt.CheckState.Checked if self._multi_select_state else QtCore.Qt.CheckState.Unchecked
        check_box.setCheckState(state)
        self._table_model.item_data.vertical_header_data[row].parameters[ENUMS.PARAMETERS_HEADER.SELECT_ROW.name] = self._multi_select_state
        self.fill_row(row, self._multi_select_state)
        self.signal_change.emit()



 
