from PyQt5 import QtCore, QtGui, QtWidgets

from projects.specification.config.app_context.app_context import DATACLASSES

from projects.specification.core.config_table import ColumnConfig, SPECIFICATION_CONFIG
from projects.specification.core.data_tables import SpecificationDataItem

from projects.specification.ui.widgets.table_widget.tw_table_view import TableView
from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable



class Table(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.setLayout(QtWidgets.QVBoxLayout(self))

        self.table_view = TableView(self)
        self.layout().addWidget(self.table_view)
        self.model: DataTable = None

    def set_model(self, model: DataTable) -> None:
        self.model = model
        self.table_view.setModel(model)
    
    def set_edited(self, value: bool) -> None:
        if value:
            self.model.set_flags(self.model.get_flags() | QtCore.Qt.ItemFlag.ItemIsEditable)

    def cell(self, row: int, column: int) -> DATACLASSES.DATA_CELL:
        if self.model:
            return self.model.get_item_view(row, column)
    
    def cell_data(self, row: int, column: int) -> DATACLASSES.DATA_CELL:
        if self.model:
            return self.model.get_item_data(row, column)
    
    def set_cell(self, row: int, column: int, cell: DATACLASSES.DATA_CELL) -> None:
        if self.model:
            self.model.set_item_view(row, column, cell)
        
    def set_data_cell(self, row: int, column: int, cell: DATACLASSES.DATA_CELL) -> None:
        if self.model:
            self.model.set_item_data(row, column, cell)
        
    def text(self, row: int, column: int) -> str:
        if self.model:
            return self.cell(row, column).value
    
    def set_text(self, row: int, column: int, value: str) -> None:
        if self.model:
            self.cell(row, column).value = value
    
    def set_background(self, row: int, column: int, color: tuple[int, int, int, int]) -> None:
        if self.model:
            self.model.set_background(row, column, color)