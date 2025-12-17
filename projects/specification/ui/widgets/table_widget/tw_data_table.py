from PyQt5 import QtCore, QtGui, QtWidgets

from projects.specification.config.app_context.app_context import DATACLASSES

from projects.specification.core.config_table import ColumnConfig, SPECIFICATION_CONFIG
from projects.specification.core.data_tables import SpecificationDataItem


class DataTable(QtCore.QAbstractTableModel):
    def __init__(self, parent, data_item: SpecificationDataItem):
        super().__init__(parent)
        self._data_item: SpecificationDataItem = data_item
        self._config = self._data_item.config
        self._unique_config = self._data_item.unique_config
        self._columns: list[ColumnConfig] = self._config.columns + self._unique_config.columns
        self._view_columns = [col for col in self._columns if col.is_view]
        
        self._index_column_view = self._set_index_column_view()
        self._data: list[list[DATACLASSES.DATA_CELL]] = self._data_item.data

        self._flags: QtCore.Qt.ItemFlag = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
        self._colors = {}
        self._set_colors()
        self._default_bg_color = QtGui.QColor(255, 255, 255)
        self._default_fg_color = QtGui.QColor(QtCore.Qt.GlobalColor.black)

    def _set_index_column_view(self) -> dict[int, int]:
        """
        Из указанного в QTableView адреса колонки преобразует в адрес колонки в _data 
        
        :return: Сслыка видимой колонки на колонку в _data
        :rtype: dict[int, int]
        """
        dct = {}
        view_x = 0
        for x, col in enumerate(self._columns):
            if col.is_view:
                dct[view_x] = x
                view_x += 1
        return dct

    def _set_colors(self) -> None:
        for y, row in enumerate(self._data):
            for x, cell in enumerate(row):
                if cell.color is not None:
                    self._colors[(y, x)] = QtGui.QColor(*cell.color)                    

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._view_columns)
    
    def data(self, index: QtCore.QModelIndex, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        row = index.row()
        column = self._index_column_view[index.column()]

        if role in (QtCore.Qt.ItemDataRole.DisplayRole,  QtCore.Qt.ItemDataRole.EditRole):
            return self._data[row][column].value
        
        elif role == QtCore.Qt.ItemDataRole.ForegroundRole:
            return self._default_fg_color
        
        elif role == QtCore.Qt.ItemDataRole.BackgroundRole:
            if (row, column) in self._colors:
                return self._colors[(row, column)]
            else:
                return self._default_bg_color
        return None
    
    def setData(self, index: QtCore.QModelIndex, value, role=QtCore.Qt.ItemDataRole.EditRole):
        row = index.row()
        column = self._index_column_view[index.column()]
        
        self._data[row][column].value = value
        self.dataChanged.emit(index, index, [role])
        return True

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._view_columns[section].column_name
        return super().headerData(section, orientation, role)

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
        return self._flags

    def get_flags(self) -> QtCore.Qt.ItemFlag:
        return self._flags

    def set_flags(self, flag: QtCore.Qt.ItemFlag) -> None:
        self._flags = flag

    def set_item_view(self, row: int, column: int, value: DATACLASSES.DATA_CELL) -> None:
        self._data[row][self._index_column_view[column]] = value
    
    def get_item_view(self, row: int, column: int) -> DATACLASSES.DATA_CELL:
        return self._data[row][self._index_column_view[column]]

    def set_item_data(self, row: int, column: int, value: DATACLASSES.DATA_CELL) -> None:
        self._data[row][column] = value

    def get_item_data(self, row: int, column: int) -> DATACLASSES.DATA_CELL:
       return self._data[row][column]
    
    def set_background(self, row: int, column: int, color: tuple[int, int, int, int]) -> None:
        index = self.index(row, column)
        column = self._index_column_view[column]
        self._colors[(row, column)] = QtGui.QColor(*color)
        self._data[row][column].color = color
        self.dataChanged.emit(index, index, [QtCore.Qt.ItemDataRole.BackgroundRole])