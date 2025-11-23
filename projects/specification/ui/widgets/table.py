from typing import Optional, Union, Any
from collections import OrderedDict
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.settings import *
from projects.specification.core.database import DataBase
from projects.specification.config.constants import *
from projects.specification.core.data_tables import InventorSpecificationDataItem

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.h_line_separate import QHLineSeparate
from projects.tools.row_counter import RowCounter


class Table(QtWidgets.QTableWidget): 
    def __init__(self, parent):
        super().__init__(parent)
        self.v_header = self.verticalHeader()
        self.v_header.sectionClicked.connect(self.select_vertical_section)
        self.toggle_sort_v_header = True

        self.h_header = self.horizontalHeader()
        self.h_header.sectionClicked.connect(self.click_horizontal_header)

    def populate(self, table_data: InventorSpecificationDataItem, is_read_only=True) -> None:
        dataset = table_data.get_data()
        
        columns = tuple(col for col in table_data.config.columns + table_data.unique_config.columns if not col.is_foreign_key)
        columns_name = tuple(col.column_name for col in table_data.config.columns + table_data.unique_config.columns if col.is_view)
        
        self.setRowCount(len(dataset))
        self.setColumnCount(len(columns_name))
        self.setHorizontalHeaderLabels(columns_name)

        for y, row in enumerate(dataset):
            view_columns = tuple(value for value, col in zip(row, columns) if col.is_view)
            for x, value in enumerate(view_columns):
                value = '' if value is None else value
                qItem = QtWidgets.QTableWidgetItem(str(value))
                self.setItem(y, x, qItem)
                
                if is_read_only:
                    qItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                else:
                    qItem.setFlags(qItem.flags())
    
    def click_horizontal_header(self, col) -> None:
        sort_order = QtCore.Qt.SortOrder.DescendingOrder if self.toggle_sort_v_header else QtCore.Qt.SortOrder.AscendingOrder
        self.toggle_sort_v_header = not self.toggle_sort_v_header
        self.model().sort(col, sort_order)

    def select_vertical_section(self, row) -> None:
        print(row)