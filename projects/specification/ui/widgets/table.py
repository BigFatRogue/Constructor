from typing import Optional, Union, Any
from collections import OrderedDict
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.settings import *
from projects.specification.core.database import DataBase
from projects.specification.config.enums import TypeTreeItem, TypeCreateLoadSpec
from projects.specification.config.constants import *
from projects.specification.config.table_config import TableConfigPropertyProject, TableConfigInventor

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.h_line_separate import QHLineSeparate
from projects.tools.row_counter import RowCounter


class TableWidget(QtWidgets.QTableWidget): 
    def __init__(self, parent):
        super().__init__(200, 10, parent)

    def fill_label_header(self, table_config: Union[TableConfigInventor]) -> None:
        labels = [col_name for col in table_config.columns if (col_name:=col.column_name)]
        self.setRowCount(len(labels))
        self.setHorizontalHeaderLabels(labels)

    def populate(self, dataset: list[list[Union[int, float, str]]]) -> None:
        for y, row in enumerate(dataset):
            for x, value in enumerate(row):
                qItem = QtWidgets.QTableWidgetItem(str(value))
                self.table.setItem(y, x, qItem)
                qItem.setFlags(QtCore.Qt.ItemIsEnabled)


class Table(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_widgets()
    
    def init_widgets(self) -> None:
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = TableWidget(self)
        self.table.fill_label_header(TableConfigInventor())
        self.grid_layout.addWidget(self.table)