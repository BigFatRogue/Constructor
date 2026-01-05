import os
from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.config.app_context import DATACLASSES

from projects.specification.ui.widgets.table.tw_header_with_overlay_widgets import HeaderWithOverlayWidgets


class HorizontalWithOverlayWidgets(HeaderWithOverlayWidgets):
    """
    Базовый класс для горизональных заголовков
    """
    signal_change = QtCore.pyqtSignal()

    def __init__(self, table_view: QtWidgets.QTableWidget, range_zoom):
        super().__init__(QtCore.Qt.Orientation.Horizontal, table_view, range_zoom)
        table_view.horizontalScrollBar().valueChanged.connect(self._update_widgets)

    def set_table_model(self, table_model):
        """
        Установка модели данных для заголовка и настройка заголовка из полученных данных
        
        :param table_model: Описание
        """
        super().set_table_model(table_model)
        self._set_size_section()
        self._set_scroll_x()
    
    def _set_scroll_x(self) -> None:
        """
        Установка координат скрола из table_model
        """
        if self.table_model.item_data.table_parameter:
            self.table_view.horizontalScrollBar().setValue(self.table_model.item_data.table_parameter.scroll_x)

    def update_scroll_x(self) -> None:
        """
        Обновление в значений скрола в table_model
        """
        if self.table_model and self.table_model.item_data.table_parameter:
            self.table_model.item_data.table_parameter.scroll_x = self.table_view.horizontalScrollBar().value()

    def _set_size_section(self) -> None:
        """
        Установка параметров заголовка из item_data

        Если в item_data ещё нет параметров, то они будут заданны из заголовка
        
        :param self: Описание
        """
        if self._table_model.item_data.horizontal_header_parameter:
            for data in self._table_model.item_data.horizontal_header_parameter:
                self.resizeSection(data.column, data.size)
        else:
            headers: list[DATACLASSES.DATA_HEADERS] = []
            for i in range(self.count()):
                header_data = DATACLASSES.DATA_HEADERS(-1, i, self.sectionSize(i), self.isVisible())
                headers.append(header_data)
            self._table_model.item_data.horizontal_header_parameter = headers

    def _set_parameters_widget(self) -> None:
        """
        Установка параметров заголовка из item_data

        Если в item_data ещё нет параметров, то они будут заданны из заголовка
        
        :param self: Описание
        """    
    

        
            