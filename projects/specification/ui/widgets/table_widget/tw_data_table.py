from dataclasses import fields
from copy import deepcopy
from PyQt5 import QtCore, QtGui, QtWidgets

from projects.specification.config.app_context.app_context import DATACLASSES

from projects.specification.core.config_table import ColumnConfig, SPECIFICATION_CONFIG
from projects.specification.core.data_tables import SpecificationDataItem


class DataTable(QtCore.QAbstractTableModel):
    FONT_PARAM_FAMILY = 1
    FONT_PARAM_SIZE = 2
    FONT_PARAM_BOLD = 3
    FONT_PARAM_ITALIC = 4
    FONT_PARAM_UNDERLINE = 5

    def __init__(self, parent, data_item: SpecificationDataItem, range_zoom):
        super().__init__(parent)
        self._data_item: SpecificationDataItem = data_item
        self.range_zoom = range_zoom
        self.current_zoom = 100
        self.min_font_size = 2
        self.dict_zoom_steps: dict[int, dict[int: int]] = {}

        self._config = self._data_item.config
        self._unique_config = self._data_item.unique_config
        self._columns: list[ColumnConfig] = self._config.columns + self._unique_config.columns
        self._view_columns = [col for col in self._columns if col.is_view]
        
        self._index_column_view = self._set_index_column_view()
        self._data: list[list[DATACLASSES.DATA_CELL]] = self._data_item.data

        self._flags: QtCore.Qt.ItemFlag = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled

        self._styles: dict[tuple[int, int, int], QtGui.QFont | QtGui.QColor | int] = {}

        self._default_family = 'Arial'
        self._default_font_size = 12
        self._default_bold = False
        self._default_italic = False
        self._default_underline = False
        self._default_align = int(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self._default_bg_color = QtGui.QColor(255, 255, 255)
        self._default_fg_color = QtGui.QColor(QtCore.Qt.GlobalColor.black)
        self._set_styles()
        
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
    
    def _set_styles(self) -> None:
        for y, row in enumerate(self._data):
            for x, cell in enumerate(row):
                x = self._index_column_view.get(x)
                if x:
                    if cell.color is not None:
                        self._styles[(y, y, QtCore.Qt.ItemDataRole.ForegroundRole)] = QtGui.QColor(*cell.color)
                    if cell.background is not None:
                        self._styles[(y, x, QtCore.Qt.ItemDataRole.BackgroundRole)] = QtGui.QColor(*cell.color)

                    font = QtGui.QFont()
                    font.setFamily(cell.font_family or self._default_family)
                    font.setPointSize(cell.font_size or self._default_font_size)
                    font.setBold(cell.bold if cell.bold is not None else self._default_bold)
                    font.setItalic(cell.italic if cell.italic is not None else self._default_italic)
                    font.setUnderline(cell.underline if cell.underline is not None else self._default_underline)
                    self._styles[(y, x, QtCore.Qt.ItemDataRole.FontRole)] = font

    def get_view_font_size(self, value: int) -> int:
        if value not in self.dict_zoom_steps:
            dct = {}
            value = int(value)
            for step in range(*self.range_zoom):
                size = int(value * step / 100)
                if size < self.min_font_size:
                    size = self.min_font_size
                elif size == 100:
                    size = value

                dct[step] = size
            self.dict_zoom_steps[value] = dct

        return self.dict_zoom_steps[value][self.current_zoom]
        
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._view_columns)
    
    def data(self, index: QtCore.QModelIndex, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        row = index.row()
        column = self._index_column_view[index.column()]

        if role in (QtCore.Qt.ItemDataRole.DisplayRole, QtCore.Qt.ItemDataRole.EditRole):
            return self._data[row][column].value
        
        elif (row, column, role) in self._styles:
            return self._styles[(row, column, role)]
      
        return None
    
    def setData(self, index: QtCore.QModelIndex, value, role=QtCore.Qt.ItemDataRole.EditRole):
        row = index.row()
        column = self._index_column_view[index.column()]
        
        self._data[row][column].value = value
        self.dataChanged.emit(index, index, [role])
        return True

    def set_range_style(self, ranges: list[QtCore.QItemSelectionRange], role: QtCore.Qt.ItemDataRole, value: int | str | QtGui.QColor, font_param=None) -> None:
        if not ranges:
            return

        for rng in ranges:
            for row in range(rng.top(), rng.bottom() + 1):
                for column in range(rng.left(), rng.right() + 1):
                    cell = self._data[row][self._index_column_view[column]]
                    if role == QtCore.Qt.ItemDataRole.FontRole and font_param:
                        font = self._styles[(row, self._index_column_view[column], role)]
                        self._set_cell_font_style(cell=cell, font=font, value=value, font_param=font_param)
                    elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
                        cell.align_h = value & QtCore.Qt.AlignmentFlag.AlignHorizontal_Mask
                        cell.align_v = value & QtCore.Qt.AlignmentFlag.AlignVertical_Mask
                        self._styles[(row, self._index_column_view[column], role)] = value

            self.dataChanged.emit(self.index(rng.top(), rng.left()), self.index(rng.bottom(), rng.right()), [role])

    def _set_cell_font_style(self, cell: DATACLASSES.DATA_CELL, font, value: int, font_param: int) -> None:
        if font_param == self.FONT_PARAM_SIZE:
            cell.font_size = value
            font.setPointSize(self.get_view_font_size(int(value)))
        elif font_param == self.FONT_PARAM_FAMILY:
            cell.font_family = value
            font.setFamily(value)
        elif font_param == self.FONT_PARAM_BOLD:
            cell.bold = value
            font.setBold(value)
        elif font_param == self.FONT_PARAM_ITALIC:
            cell.italic = value
            font.setItalic(value)
        elif font_param == self.FONT_PARAM_UNDERLINE:
            cell.underline = value
            font.setUnderline(value)

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

    def set_edited(self, value: bool) -> None:
        if value:
            self.set_flags(self.get_flags() | QtCore.Qt.ItemFlag.ItemIsEditable)

    def set_zoom(self, step: int) -> None:
        self.current_zoom = step
        role = QtCore.Qt.ItemDataRole.FontRole
        
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                column = self._index_column_view[column]
                cell = self._data[row][column]
                font = self._styles[(row, column, role)]

                font.setPointSize(self.get_view_font_size(cell.font_size))

        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()), [QtCore.Qt.ItemDataRole.FontRole])

    def select_row(self, value: tuple[int, bool]) -> None:
        row, state = value
        role = QtCore.Qt.ItemDataRole.BackgroundRole

        column = self._data_item.get_index_from_name_filed('is_select')
        self._data[row][column].value = state

        color = (200, 60, 60, 200) if state else (255, 255, 255)
        
        for x in range(self.columnCount()):
            self._styles[(row, self._index_column_view[x], role)] = QtGui.QColor(*color)
            self._data[row][self._index_column_view[x]].background = color
        
        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount()), [role])

    def get_style_selection(self, selection: list[QtCore.QItemSelectionRange]) -> DATACLASSES.CELL_STYLE:
        style_ranges = None
        for rng in selection:
            for row in range(rng.top(), rng.bottom() + 1):
                for column in range(rng.left(), rng.right() + 1):
                    cell: DATACLASSES.DATA_CELL = self._data[row][self._index_column_view[column]]

                    if style_ranges is None:
                        style_ranges = deepcopy(cell)
                    
                    for cell_field in fields(cell):
                        value_cell = getattr(cell, cell_field.name)
                        value_range = getattr(style_ranges, cell_field.name)
                        if value_cell != value_range:
                            setattr(style_ranges, cell_field.name, None)
        
        return style_ranges

    def reset_style(self, ranges: list[QtCore.QItemSelectionRange]) -> None:
        if not ranges:
            return

        for rng in ranges:
            for row in range(rng.top(), rng.bottom() + 1):
                for column in range(rng.left(), rng.right() + 1):
                    cell = self._data[row][self._index_column_view[column]]
                    
                    font = self._styles[(row, self._index_column_view[column], QtCore.Qt.ItemDataRole.FontRole)]
                    self._set_cell_font_style(cell=cell, font=font, value=self._default_family, font_param=self.FONT_PARAM_FAMILY)
                    self._set_cell_font_style(cell=cell, font=font, value=self._default_font_size, font_param=self.FONT_PARAM_SIZE)
                    self._set_cell_font_style(cell=cell, font=font, value=self._default_bold, font_param=self.FONT_PARAM_BOLD)
                    self._set_cell_font_style(cell=cell, font=font, value=self._default_italic, font_param=self.FONT_PARAM_ITALIC)
                    self._set_cell_font_style(cell=cell, font=font, value=self._default_underline, font_param=self.FONT_PARAM_UNDERLINE)

                    cell.align_h = self._default_align & QtCore.Qt.AlignmentFlag.AlignHorizontal_Mask
                    cell.align_v = self._default_align & QtCore.Qt.AlignmentFlag.AlignVertical_Mask
                    self._styles[(row, self._index_column_view[column], QtCore.Qt.ItemDataRole.TextAlignmentRole)] = self._default_align
                    
                    cell.background = self._default_bg_color
                    self._styles[(row, self._index_column_view[column], QtCore.Qt.ItemDataRole.BackgroundColorRole)] = self._default_bg_color
                    
                    cell.color = self._default_fg_color
                    self._styles[(row, self._index_column_view[column], QtCore.Qt.ItemDataRole.ForegroundRole)] = self._default_fg_color
                        

            role = [QtCore.Qt.ItemDataRole.FontRole, QtCore.Qt.ItemDataRole.TextAlignmentRole, QtCore.Qt.ItemDataRole.BackgroundColorRole, QtCore.Qt.ItemDataRole.ForegroundRole]
            self.dataChanged.emit(self.index(rng.top(), rng.left()), self.index(rng.bottom(), rng.right()), role)