import os
from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.config.app_context import SETTING, ENUMS, DATACLASSES

from projects.specification.ui.widgets.table.tw_header_with_overlay_widgets import HeaderWithOverlayWidgets

from projects.tools.functions.create_action_menu import create_action



class VerticallWithOverlayWidgets(HeaderWithOverlayWidgets):
    signal_change = QtCore.pyqtSignal()

    def __init__(self, table_view: QtWidgets.QTableWidget, range_zoom):
        super().__init__(QtCore.Qt.Orientation.Vertical, table_view, range_zoom)
        table_view.verticalScrollBar().valueChanged.connect(self._update_widgets)

        self.init_contex_menu()

    def init_contex_menu(self) -> None:
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.context_menu = QtWidgets.QMenu(self)

        create_action(menu=self.context_menu ,
            title='Вставить строчку выше',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'insert_row_up.png'),
            triggerd=self.insert_row_up)
        
        create_action(menu=self.context_menu ,
            title='Вставить строчку ниже',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'insert_row_down.png'),
            triggerd=self.insert_row_down)

        create_action(menu=self.context_menu ,
            title='Удалить строчку',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'delete_row.png'),
            triggerd=self.delete_row)

    def show_context_menu(self, position: QtCore.QPoint) -> None:
        if self._is_edited:
            self._active_select_row = self.logicalIndexAt(position)
            if self._active_select_row != -1:
                self.context_menu.exec_(self.viewport().mapToGlobal(position))

    def set_table_edited(self, value: bool) -> None:
        self._is_edited = value

    def insert_row_up(self) -> None:
        if self._active_select_row == 0:
            self.table_model.insert_row(0)
        else:
            self.table_model.insert_row(self._active_select_row - 1)

    def insert_row_down(self) -> None:
        self.table_model.insert_row(self._active_select_row + 1)

    def delete_row(self) -> None:
        self.table_model.delete_row(self._active_select_row)

    def set_table_model(self, table_model):
        super().set_table_model(table_model)
        self._set_size_section()
        self._set_scroll_y()
    
    def _set_scroll_y(self) -> None:
        if self.table_model.item_data.table_parameter:
            self.table_view.verticalScrollBar().setValue(self.table_model.item_data.table_parameter.scroll_y)

    def update_scroll_y(self) -> None:
        if self.table_model and self.table_model.item_data.table_parameter:
            self.table_model.item_data.table_parameter.scroll_y = self.table_view.verticalScrollBar().value()

    def _set_size_section(self) -> None:
        """
        Установка параметров заголовка из item_data

        Если в item_data ещё нет параметров, то они будут заданны из заголовка
        
        :param self: Описание
        """
        if self._table_model.item_data.vertical_header_parameter:
            for data in self._table_model.item_data.vertical_header_parameter:
                self.resizeSection(data.row, data.size)
        else:
            headers: list[DATACLASSES.DATA_HEADERS] = []
            for i in range(self.count()):
                header_data = DATACLASSES.DATA_HEADERS(i, -1, self.sectionSize(i), self.isVisible())
                headers.append(header_data)
            self._table_model.item_data.vertical_header_parameter = headers



 
