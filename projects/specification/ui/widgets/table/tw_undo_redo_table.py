from PyQt5 import QtGui, QtCore
from enum import Enum ,auto
from typing import Any, Protocol

from projects.specification.config.app_context import DATACLASSES


class DataTable(Protocol):
     def change_cell(self, row: int, column: int, role: QtCore.Qt.ItemDataRole, value: int | str | QtGui.QColor, font_param=None) -> None:
         ...


class TypeCommandChange(Enum):
    VALUE = auto()
    STYLE = auto()
    SPAN = auto()
    SIZE = auto()
    VISIBLY = auto()
    INSERT = auto()


class UndoRedoItem:
    def __init__(self, old_value: Any, new_value: Any, property_name: str):
        self.old_value = old_value
        self.new_value = new_value
    
    def undo(self) -> None:
        ...
    
    def redo(self) -> None:
        ...
        

class UndoRedoItemCell(UndoRedoItem):
    def __init__(self, row: int, column: int, old_value: Any, new_value:Any, role: QtCore.Qt.ItemDataRole, font_param: int = None):
        super().__init__(old_value, new_value)
        self.row = row
        self.column = column
        self.role = role
        self.font_param = font_param
    
    def undo(self, table_data: DataTable) -> None:
        table_data: DataTable
        table_data.change_cell(self.row, self.column, self.role, self.old_value, self.font_param)

    def redo(self, table_data: DataTable) -> None:
        table_data: DataTable
        table_data.change_cell(self.row, self.column, self.role, self.old_value, self.font_param)
        


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

    def add_cell(self, row: int, column: int, old_value: Any, new_value:Any, role: QtCore.Qt.ItemDataRole, font_param: int = None) -> None:
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
            
            item = UndoRedoItemCell(self, row, column, old_value, new_value, role, font_param)
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