from PyQt5 import QtGui, QtCore, QtWidgets
from enum import Enum ,auto
from typing import Any, Protocol
from copy import deepcopy

from projects.specification.config.app_context import DATACLASSES


class ModelDataTable(Protocol):
    FONT_PARAM_FAMILY = 1
    FONT_PARAM_SIZE = 2
    FONT_PARAM_BOLD = 3
    FONT_PARAM_ITALIC = 4
    FONT_PARAM_UNDERLINE = 5

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
    def __init__(self, old_value: Any, new_value: Any):
        self.old_value = old_value
        self.new_value = new_value
    
    def undo(self) -> None:
        ...
    
    def redo(self) -> None:
        ...
        

class UndoRedoItemCell(UndoRedoItem):
    def __init__(self, table_model: ModelDataTable, row: int, column: int, old_value: DATACLASSES.DATA_CELL, new_value:Any, role: QtCore.Qt.ItemDataRole, font_param: int = None):
        old_value = old_value if not isinstance(old_value, QtGui.QColor) else new_value.getRgb()
        new_value = new_value if not isinstance(new_value, QtGui.QColor) else new_value.getRgb()
        
        super().__init__(old_value, new_value)
        
        self.table_model = table_model
        self.row = row
        self.column = column
        self.role = role
        self.font_param = font_param
    
    def undo(self) -> None:
        self.table_model.change_cell(self.row, self.column, self.role, self.old_value, self.font_param)
        self.table_model.layoutChanged.emit()

    def redo(self) -> None:
        self.table_model.change_cell(self.row, self.column, self.role, self.new_value, self.font_param)
        self.table_model.layoutChanged.emit()
        

class UndoRedoTable:
    def __init__(self, table_model):
        self.table_model: ModelDataTable = table_model

        self.list_undo: list[list[UndoRedoItem]] = []
        self.list_redo: list[list[UndoRedoItem]] = []
        self.list_change: list[UndoRedoItem] = []
        self.is_start_transaction = False
        self.has_add_change = True

    def start_transaction(self) -> None:
        self.is_start_transaction = True

    def end_transaction(self) -> None:
        self.is_start_transaction = False
        if self.list_change:
            self.list_undo.append([i for i in self.list_change])
            self.list_change.clear()

    def add_cell(self, row: int, column: int, old_value: Any, new_value: Any, role: QtCore.Qt.ItemDataRole, font_param: int = None) -> None:
        """
        Добавления в лист undo информации об изменение ячейки
        
        :param row: Номер строки
        :type row: int
        :param column: Номер строки в TableView
        :type column: int
        :param old_value: Старое значение
        :type old_value: Any
        :param new_value: Новое значение
        :type new_value: Any
        :param role: Роль
        :type role: QtCore.Qt.ItemDataRole
        :param font_param: какой параметр текста изменяется
        :type font_param: int
        """

        if self.has_add_change:
            if self.list_redo:
                # если добавляется новое значение, то лист возврата изменений вперёд очищается
                self.list_redo.clear()
            
            item = UndoRedoItemCell(table_model=self.table_model, row=row, column=column, old_value=old_value, new_value=new_value, role=role, font_param=font_param)
            if item.new_value != item.old_value:
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
            except Exception as error:
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