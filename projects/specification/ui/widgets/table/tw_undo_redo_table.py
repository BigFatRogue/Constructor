from PyQt5 import QtGui, QtCore, QtWidgets
from enum import Enum ,auto
from typing import Any, Protocol, Sequence
from copy import deepcopy

from projects.specification.config.app_context import DATACLASSES


class ModelDataTable(Protocol):
    def change_cell(self, row: int, column: int, role: QtCore.Qt.ItemDataRole, value: int | str | QtGui.QColor, font_param=None) -> None:
         ...
    
    def insert_row(self, row: int, row_data: list[DATACLASSES.DATA_CELL] = None, vertical_header_data: list[DATACLASSES.DATA_HEADERS]=None) -> None:
        ...
    
    def delete_row(self, rows: Sequence[int], is_undo:bool = False) -> None:
        ...


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


class UndoRedoItemRowInsert(UndoRedoItem):
    def __init__(self, table_model: ModelDataTable, row: int):
        super().__init__(None, None)

        self.table_model = table_model
        self.row = row
    
    def undo(self):
        self.table_model.delete_rows(rows=(self.row, ), is_undo=True)

    def redo(self):
        self.table_model.insert_row(row=self.row)


class UndoRedoItemRowDelete(UndoRedoItem):
    def __init__(self, table_model: ModelDataTable, number_rows: Sequence[int], rows: list[list[DATACLASSES.DATA_CELL]], verical_headers: list[DATACLASSES.DATA_HEADERS]):
        super().__init__(None, None)

        self.table_model = table_model
        self.number_rows = number_rows
        self.vartical_headers = verical_headers
        self.rows = rows

    def undo(self):
        for number_row, row_data, header_data in zip(self.number_rows, self.rows, self.vartical_headers):
            self.table_model.insert_row(row=number_row, row_data=row_data, vertical_header_data=header_data)
    
    def redo(self):
        self.table_model.delete_rows(self.number_rows)


# TODO реазиловать
class UndoRedoItemBrowerInsert(UndoRedoItem): ...

# TODO реазиловать
class UndoRedoItemBrowerDelete(UndoRedoItem): ...


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

    def _check_add_item(self) -> bool:
        if self.has_add_change:
            if self.list_redo:
                # если добавляется новое значение, то лист возврата изменений вперёд очищается
                self.list_redo.clear()
            return True
        return False

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
        if not self._check_add_item():
            return
                    
        item = UndoRedoItemCell(table_model=self.table_model, row=row, column=column, old_value=old_value, new_value=new_value, role=role, font_param=font_param)
        if item.new_value != item.old_value:
            if self.is_start_transaction:
                self.list_change.append(item)
            else:
                self.list_undo.append([item])
    
    def add_insert_row(self, row: int) -> None:
        if not self._check_add_item():
            return
        
        item = UndoRedoItemRowInsert(table_model=self.table_model, row=row)
        if self.is_start_transaction:
            self.list_change.append(item)
        else:
            self.list_undo.append([item])

    def add_delete_row(self, number_rows: Sequence[int], rows: list[DATACLASSES.DATA_CELL], vertival_headers: list[DATACLASSES.DATA_HEADERS]) -> None:
        if not self._check_add_item():
            return
        
        item = UndoRedoItemRowDelete(table_model=self.table_model, number_rows=number_rows, rows=rows, verical_headers=vertival_headers)
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