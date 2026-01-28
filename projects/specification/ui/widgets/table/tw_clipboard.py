
from PyQt5 import QtWidgets, QtCore
from enum import Enum, auto
from dataclasses import dataclass
from typing import Any

from projects.specification.core.data_tables import SpecificationDataItem
from projects.specification.config.app_context import DATACLASSES
from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable


class TypeItemClipboard(Enum):
    CELLS = auto()
    LINK = auto()
    VALUE = auto()


@dataclass
class ItemClipboard:
    tp: TypeItemClipboard = None
    data: Any = None
    text: str = None
    rows: list[int] = None
    columns: list[int] = None


class __Clipboard:
    def __init__(self):
        self.current_model: ModelDataTable = None
        self.current_item_clipboard: ItemClipboard = None

        self._copy_type_clipboard: dict[TypeItemClipboard, callable] = {
            TypeItemClipboard.CELLS: self._copy_cells, 
            TypeItemClipboard.LINK: self._copy_link,
            TypeItemClipboard.VALUE: self._copy_value
        }

        self._paste_type_clipboard: dict[TypeItemClipboard, callable] = {
            TypeItemClipboard.CELLS: self._paste_cells, 
            TypeItemClipboard.LINK: self._paste_link,
            TypeItemClipboard.VALUE: self._paste_value
        }
    
    def copy(self, model: ModelDataTable, selection: QtCore.QItemSelection, type_item_clipboard: TypeItemClipboard = TypeItemClipboard.CELLS) -> None:
        self.current_model = model
        self.current_item_clipboard = ItemClipboard(tp=type_item_clipboard)
        self._copy_type_clipboard[type_item_clipboard](selection)

    def _copy_cells(self, selection) -> None:
        rows = set()
        columns = set()
        for rng in selection:
            numbe_rows, number_column = self.current_model.get_visible_coords(rng.top(), rng.left(), rng.bottom(), rng.right())
            rows.add(numbe_rows)
            columns.add(number_column)
        
        rows = sorted([r for row in rows for r in row])
        columns = sorted([c for col in columns for c in col])

        text, html = self._create_html_table(rows, columns)

        clipboard = QtWidgets.QApplication.clipboard()
        mime_data = QtCore.QMimeData()
        mime_data.setHtml(html)
        mime_data.setText(text)
        clipboard.setMimeData(mime_data)

        self.current_item_clipboard.rows = rows
        self.current_item_clipboard.columns = columns
        self.current_item_clipboard.text = text
        self.current_item_clipboard.data = html

    def _copy_value(self, selection: QtCore.QItemSelection) -> None:
        ...
    
    def _copy_link(self, selection: QtCore.QItemSelection) -> None:
        index = selection.takeFirst().topLeft()
        row_id = self.current_model.item_data.data[index.row()][0].value
        link = self.current_model.item_data.data_link.get(row_id)
        self.current_item_clipboard = ItemClipboard(tp=TypeItemClipboard.LINK,
                                                    data=link)

    def _create_html_table(self, rows: list[int], columns: list[int]) -> tuple[str, str]:
        """
        Создание где стобцы разделены табуляцией, а строки переносом строки и создание и HTML таблицы, 
        """
        
        lines_html = []
        lines_text = []
        for row in rows:
            html_line = []
            text_line = []
            for column in columns:
                cell = self.current_model.item_data.data[row][column]
                html_line.append(cell.get_td_html())
                text_line.append(str(cell.value))

            lines_html.append(f'<tr>{"".join(html_line)}</tr>')
            lines_text.append('\t'.join(text_line))
        
        html_table = fr'<table cellspacing="0" cellpadding="3" style="border-collapse: collapse;">{"".join(lines_html)}</table>'
        text = "\n".join(lines_text)

        return text, html_table

    def paste(self, target_model: ModelDataTable, row: int, column: int) -> None:
        # TODO доработать, чтобы вставлять значения не только в ячейку но и в диапазон, если единичное значение

        if self.current_item_clipboard is None:
            return
        
        if self.current_item_clipboard.text == QtWidgets.QApplication.clipboard().text() or self.current_item_clipboard.text == None:
            self._paste_type_clipboard[self.current_item_clipboard.tp](target_model, row, column)
        else:
            # TODO орагнизовать проверку данных в буфере
            ...
        
    def _paste_cells(self, target_model: ModelDataTable, row: int, column: int) -> None:
        target_model.paste_value_from_model(source_model=self.current_model, 
                                            source_rows=self.current_item_clipboard.rows, 
                                            source_columns=self.current_item_clipboard.columns,
                                            target_address=(row, column))
    
    def _paste_value(self, target_model: ModelDataTable, row: int, column: int) -> None:
        ...
    
    def _paste_link(self, target_model: ModelDataTable, row: int, column: int) -> None:
        row_id = target_model.item_data.data[row][0].value
        if row_id in target_model.item_data.data_link:
            target_model.item_data.data_link[row_id].extend(self.current_item_clipboard.data)
        else:
            target_model.item_data.data_link[row_id] = self.current_item_clipboard.data
            
                

CLIPBOARD = __Clipboard()