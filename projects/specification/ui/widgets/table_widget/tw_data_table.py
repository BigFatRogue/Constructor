from dataclasses import fields
from copy import deepcopy
from enum import Enum ,auto
from typing import Any

from PyQt5 import QtCore, QtGui, QtWidgets

from projects.specification.config.app_context import DATACLASSES, ENUMS

from projects.specification.core.config_table import ColumnConfig, SPECIFICATION_CONFIG
from projects.specification.core.data_tables import SpecificationDataItem


class UndoRedoItem:
    def __init__(self, old_value: Any, new_value: Any):
        self.old_value = old_value
        self.new_value = new_value
    
    def undo(self) -> None:
        ...
    
    def redo(self) -> None:
        ...
        

class UndoRedoItemCell(UndoRedoItem):
    def __init__(self, cell: DATACLASSES.DATA_CELL, row: int, column: int, old_value: Any, new_value:Any, role: QtCore.Qt.ItemDataRole, font_param: int = None):
        super().__init__(old_value, new_value)
        self.cell = cell
        self.row = row
        self.column = column
        self.role = role
        self.font_param = font_param
    
    def undo(self, table_data) -> None:
        table_data: DataTable
        table_data._change_cell(self.row, self.column, self.role, self.old_value, self.font_param)

    def redo(self, table_data) -> None:
        table_data: DataTable
        table_data._change_cell(self.row, self.column, self.role, self.old_value, self.font_param)
        

class UndoRedoTable:
    def __init__(self, table_data):
        self.table_data: DataTable = table_data

        self.list_undo: list[list[UndoRedoItem]] = []
        self.list_redo: list[list[UndoRedoItem]] = []
        self.list_change: list[UndoRedoItem] = []
        self.is_start_transaction = False
        self.has_add_change = True

    def start_transaction(self) -> None:
        self.is_start_transaction = True

    def end_transaction(self) -> None:
        self.is_start_transaction = False
        self.list_undo.append(self.list_change)
        self.list_change = []

    def add_cell(self, cell: DATACLASSES.DATA_CELL, row: int, column: int, old_value: Any, new_value:Any, role: QtCore.Qt.ItemDataRole, font_param: int = None) -> None:
        """
        Добавления в лист undo информации об изменение ячейки
        
        :param self: Описание
        :param row: Описание
        :type row: int
        :param column: Описание
        :type column: int
        :param old_value: Описание
        :type old_value: Any
        :param new_value: Описание
        :type new_value: Any
        :param role: Описание
        :type role: QtCore.Qt.ItemDataRole
        :param font_param: Описание
        :type font_param: int
        """
        if self.has_add_change:
            if self.list_redo:
                # если добавляется новое значение, то лист возврата изменений вперёд очищается
                self.list_redo.clear()
            
            item = UndoRedoItemCell(self, cell, row, column, old_value, new_value, role, font_param)
            if self.is_start_transaction:
                self.list_change.append(item)
            else:
                self.list_undo.append([item])
    
    def undo(self) -> None:
        self.has_add_change = False
        if self.list_undo:
            last_item = self.list_undo.pop()
            self.list_redo.append(last_item)
            try:
                for item in last_item:
                    item.undo()
            except Exception:
                self.list_redo.append(last_item)
        self.has_add_change = True
            
    def redo(self) -> None:
        self.has_add_change = False
        if self.list_redo:
            last_item = self.list_redo.pop()
            self.list_undo.append(last_item)
            try:
                for item in last_item:
                    item.redo()
            except Exception:
                self.list_redo.append(last_item)
        self.has_add_change = True


class DataTable(QtCore.QAbstractTableModel):
    """
    Модель данных для таблиц
    """
    
    signal_change = QtCore.pyqtSignal()

    FONT_PARAM_FAMILY = 1
    FONT_PARAM_SIZE = 2
    FONT_PARAM_BOLD = 3
    FONT_PARAM_ITALIC = 4
    FONT_PARAM_UNDERLINE = 5

    def __init__(self, item_data: SpecificationDataItem, range_zoom: tuple[int, int , int]=None):
        """
        :param data_item: элемент источника и сохранения данных
        :type data_item: SpecificationDataItem
        :param range_zoom: диапазон для масштабирования (мин, макс, шаг)
        """
        super().__init__(None)
        self.item_data: SpecificationDataItem = item_data

        self._range_zoom = range_zoom
        self._current_zoom = 100
        self._min_font_size = 2
        self._dict_zoom_steps: dict[int, dict[int: int]] = {}

        self._config = self.item_data.general_config
        self._unique_config = self.item_data.unique_config
        self._columns: list[ColumnConfig] = self._config.columns + self._unique_config.columns
        self._view_columns = [col for col in self._columns if col.is_view]
        
        self._index_column_view = self._set_index_column_view()
        self._data: list[list[DATACLASSES.DATA_CELL]] = self.item_data.data

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

        self.undo_redo = UndoRedoTable(table_data=self)
        
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
        """
        Создание словаря для стилей ячеек для быстрого отображения
        
        :param self: Описание
        """
        number_index = self.item_data.get_index_from_name_filed('number_row')
        for y, row in enumerate(self._data):
            for x, cell in enumerate(row):
                if number_index == x:
                    cell.value = y
                    
                if cell.color is not None:
                    self._styles[(y, x, QtCore.Qt.ItemDataRole.ForegroundRole)] = QtGui.QColor(*cell.color)
                if cell.background is not None:
                    self._styles[(y, x, QtCore.Qt.ItemDataRole.BackgroundRole)] = QtGui.QColor(*cell.background)

                font = QtGui.QFont()
                font.setFamily(cell.font_family or self._default_family)
                font.setPointSize(cell.font_size or self._default_font_size)
                font.setBold(cell.bold if cell.bold is not None else self._default_bold)
                font.setItalic(cell.italic if cell.italic is not None else self._default_italic)
                font.setUnderline(cell.underline if cell.underline is not None else self._default_underline)
                self._styles[(y, x, QtCore.Qt.ItemDataRole.FontRole)] = font

                self._styles[(y, x, QtCore.Qt.ItemDataRole.TextAlignmentRole)] = cell.align_h | cell.align_v

        role = [QtCore.Qt.ItemDataRole.FontRole, QtCore.Qt.ItemDataRole.TextAlignmentRole, QtCore.Qt.ItemDataRole.BackgroundColorRole, QtCore.Qt.ItemDataRole.ForegroundRole]
        self.dataChanged.emit(self.index(0, 0), self.index(len(self._data), len(self._data[0])), role)

    def get_view_font_size(self, value: int) -> int:
        """
        Размер текста для заданного масштаба
        
        :param value: размер заданный в ячейки
        :type value: int
        :return: размер текста соответствующий масштабу (в данных не меняется)
        :rtype: int
        """
        if value not in self._dict_zoom_steps:
            dct = {}
            value = int(value)
            for step in range(*self._range_zoom):
                size = int(value * step / 100)
                if size < self._min_font_size:
                    size = self._min_font_size
                elif size == 100:
                    size = value

                dct[step] = size
            self._dict_zoom_steps[value] = dct

        return self._dict_zoom_steps[value][self.item_data.table_parameter.current_zoom]
    
    def set_range_step_zoom(self, range_zoom: tuple[int, int, int]) -> None:
        """
        Установка диапазона для масштабирования
        
        :param self: Описание
        :param range_zoom: диапазон для масштабирования (мин, макс, шаг)
        :type range_zoom: tuple[int, int, int]
        """
        self._range_zoom = range_zoom

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
        """
        Установка стиля ячеек в диапазоне
        
        :param ranges: диапазоны
        :type ranges: list[QtCore.QItemSelectionRange]
        :param role: роль (свойство)
        :type role: QtCore.Qt.ItemDataRole
        :param value: значение
        :type value: int | str | QtGui.QColor
        :param font_param: какой параметр текста (размер, шрифт и др.)
        """
        if not ranges:
            return

        for rng in ranges:
            for row in range(rng.top(), rng.bottom() + 1):
                for column in range(rng.left(), rng.right() + 1):
                    self.change_cell(row=row, column=column, value=value, role=role, font_param=font_param)
            self.dataChanged.emit(self.index(rng.top(), rng.left()), self.index(rng.bottom(), rng.right()), [role])
        self.signal_change.emit()

    def change_cell(self, row: int, column: int, role: QtCore.Qt.ItemDataRole, value: int | str | QtGui.QColor, font_param=None) -> None:
        """
        Изменение свойств одной ячейки DATACLASS.CELL_DATA
        
        :param row: номер строки
        :type row: int
        :param column: номер столбца
        :type column: int
        :param role: роль
        :type role: QtCore.Qt.ItemDataRole
        :param value: значение
        :type value: int | str | QtGui.QColor
        :param font_param: какой параметр текста (размер, шрифт и др.)
        """
        cell = self._data[row][self._index_column_view[column]]
        # self.undo_redo.add_cell()

        if role == QtCore.Qt.ItemDataRole.FontRole and font_param:
            font = self._styles[(row, self._index_column_view[column], role)]
            
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
        
        elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            cell.align_h = value & QtCore.Qt.AlignmentFlag.AlignHorizontal_Mask
            cell.align_v = value & QtCore.Qt.AlignmentFlag.AlignVertical_Mask
            self._styles[(row, self._index_column_view[column], role)] = value
        
        elif role  == QtCore.Qt.ItemDataRole.BackgroundColorRole:
            if isinstance(value, (tuple, list)):
                self._styles[(row, self._index_column_view[column], role)] = QtGui.QColor(*value)
                cell.background = tuple(*value)
            if isinstance(value, QtGui.QColor):
                self._styles[(row, self._index_column_view[column], role)] = value
                cell.background = value.getRgb()
            if value is None:
                cell.background = (255, 255, 255, 255) 
                self._styles[(row, self._index_column_view[column], role)] = QtGui.QColor(255, 255, 255, 255)
        
        elif role  == QtCore.Qt.ItemDataRole.ForegroundRole:
            if isinstance(value, (tuple, list)):
                self._styles[(row, self._index_column_view[column], role)] = QtGui.QColor(*value)
                cell.color = tuple(*value)
            if isinstance(value, QtGui.QColor):
                self._styles[(row, self._index_column_view[column], role)] = value
                cell.color = value.getRgb()
            if value is None:
                self._styles[(row, self._index_column_view[column], role)] = QtGui.QColor(0, 0, 0, 255)
                cell.color = (0, 0, 0, 0) 

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._view_columns[section].column_name
        
        # elif role == QtCore.Qt.ItemDataRole.BackgroundColorRole :
        #     return QtGui.QColor(255, 0, 0)
        
        return super().headerData(section, orientation, role)

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
        return self._flags

    def get_flags(self) -> QtCore.Qt.ItemFlag:
        return self._flags

    def set_flags(self, flag: QtCore.Qt.ItemFlag) -> None:
        self._flags = flag

    def set_edited(self, value: bool) -> None:
        """
        Включение / выключение режима редактирования ячеек
        - True  - включить
        - False - выключить\n
        по умолчанию выключено
        """
        if value:
            self.set_flags(self.get_flags() | QtCore.Qt.ItemFlag.ItemIsEditable)

    def set_zoom(self, step) -> None:
        """
        Установка текущего шага масштабирования
        
        :param step: шаг масташабирования (%)
        :type step: int
        """
        if step == self._current_zoom:
            return
        
        self._current_zoom = step
        self.item_data.table_parameter.current_zoom = step
        role = QtCore.Qt.ItemDataRole.FontRole
        
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                column = self._index_column_view[column]
                cell = self._data[row][column]
                font = self._styles[(row, column, role)]

                font.setPointSize(self.get_view_font_size(cell.font_size))

        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()), [QtCore.Qt.ItemDataRole.FontRole])

    def select_row(self, row: int, state: bool) -> None:
        """
        Выбор строки. Для таблиц у которых есть поле в БД is_select
        
        :param row: Номер строки
        :type row: int
        :param state: True - выбрана, False - не выбрана
        :type state: bool
        """
        role = QtCore.Qt.ItemDataRole.BackgroundRole

        column = self.item_data.get_index_from_name_filed('is_select')
        if column >= 0:
            # self._data[row][column].value = state
            self.item_data.vertical_header_parameter[row].parameters[ENUMS.PARAMETERS_HEADER.SELECT_ROW.name] = state

            color = (200, 60, 60, 200) if state else (255, 255, 255)
            
            for x in range(self.columnCount()):
                self._styles[(row, self._index_column_view[x], role)] = QtGui.QColor(*color)
                self._data[row][self._index_column_view[x]].background = color

        self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount()), [role])
        # self.headerDataChanged.emit(QtCore.Qt.Orientation.Vertical, row, row + 1)

    def get_style_selection(self, selection: list[QtCore.QItemSelectionRange]) -> DATACLASSES.DATA_CELL:
        """
        Получение значения стиля диапазонов
        
        :param selection: выделение в QtableView
        :type selection: list[QtCore.QItemSelectionRange]
        :return: ячейка содержащая общие стили диапазонов
        :rtype: CELL_STYLE
        """
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
        """
        Сброс стиля диапазона до стандартных значений
        
        :param ranges: выделение в QtableView
        :type ranges: list[QtCore.QItemSelectionRange]
        """
        if not ranges:
            return

        for rng in ranges:
            for row in range(rng.top(), rng.bottom() + 1):
                for column in range(rng.left(), rng.right() + 1):
                    
                    for font_param, value in zip((self.FONT_PARAM_FAMILY, self.FONT_PARAM_SIZE, self.FONT_PARAM_BOLD, self.FONT_PARAM_ITALIC, self.FONT_PARAM_UNDERLINE),
                                          (self._default_family, self._default_font_size,self._default_bold, self._default_italic, self._default_underline)):
                        self.change_cell(row=row, column=column, role=QtCore.Qt.ItemDataRole.FontRole, value=value, font_param=font_param)
                    
                    self.change_cell(row=row, column=column, value=self._default_align, role=QtCore.Qt.ItemDataRole.TextAlignmentRole)
                    self.change_cell(row=row, column=column, value=self._default_bg_color, role=QtCore.Qt.ItemDataRole.BackgroundColorRole)
                    self.change_cell(row=row, column=column, value=self._default_fg_color, role=QtCore.Qt.ItemDataRole.ForegroundRole)
                        
            role = [QtCore.Qt.ItemDataRole.FontRole, QtCore.Qt.ItemDataRole.TextAlignmentRole, QtCore.Qt.ItemDataRole.BackgroundColorRole, QtCore.Qt.ItemDataRole.ForegroundRole]
            self.dataChanged.emit(self.index(rng.top(), rng.left()), self.index(rng.bottom(), rng.right()), role)
        self.signal_change.emit()
    
    def sorted_column(self, state_sorted: list[ENUMS.STATE_SORTED_COLUMN]) -> None:
        """
        Сортировка по нескольким столбца

        После сортировки перенумирования строк и перевыделение выделенных строк 
        
        :param self: Описание
        :param state_sorted: Описание
        :type state_sorted: list[ENUMS.STATE_SORTED_COLUMN]
        """
        
        index_column = [*range(len(state_sorted))]

        for column, state in zip(index_column[::-1], state_sorted[::-1]):
            if state != ENUMS.STATE_SORTED_COLUMN.EMPTY:
                self._data.sort(key=lambda x: x[self._index_column_view[column]].value, reverse=state == ENUMS.STATE_SORTED_COLUMN.REVERSE)

            self.item_data.horizontal_header_parameter[column].parameters[ENUMS.PARAMETERS_HEADER.STATE_SORTED.name] = state.value 
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()), [QtCore.Qt.ItemDataRole.DisplayRole])

        self._update_number_row()
    
    def _update_number_row(self) -> None:
        number_row = self.item_data.get_index_from_name_filed('number_row')
        if number_row != -1:
            state_select_row = {}

            for row in range(self.rowCount()):
                data = self._data[row][number_row]
                
                if ENUMS.PARAMETERS_HEADER.SELECT_ROW.name in self.item_data.vertical_header_parameter[row].parameters:
                    state_select_row[row] = self.item_data.vertical_header_parameter[row].parameters[ENUMS.PARAMETERS_HEADER.SELECT_ROW.name]
                    
                    if data.value in state_select_row:
                        state = state_select_row[data.value]
                    else:
                        state = self.item_data.vertical_header_parameter[data.value].parameters[ENUMS.PARAMETERS_HEADER.SELECT_ROW.name]
                    
                    self.select_row(row, state)                
                
                data.value = row
    
    def insert_row(self, row: int) -> None:
        self.item_data.insert_row(row)
        self._set_styles()
        self._update_number_row()
        self.layoutChanged.emit()
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()), [QtCore.Qt.ItemDataRole.DisplayRole])
        self.signal_change.emit()
    
    def delete_row(self, row: int) -> None:
        self.item_data.delete_row(row) 
        self.layoutChanged.emit()
        self.signal_change.emit()