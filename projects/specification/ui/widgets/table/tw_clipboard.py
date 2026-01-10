
from PyQt5 import QtWidgets, QtCore

from projects.specification.core.data_tables import SpecificationDataItem
from projects.specification.config.app_context import DATACLASSES
from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable


class __Clipboard:
    def __init__(self):
        self.current_model: ModelDataTable = None
        self.rows: tuple[int, ...] = None
        self.columns: tuple[int, ...] = None
        self.html_table: str = None
        self.text: str = None
    
    def copy(self, model: ModelDataTable, selection: list[QtCore.QItemSelectionRange]) -> None:
        self.current_model = model
        
        self._create_data(selection)

        clipboard = QtWidgets.QApplication.clipboard()
        mime_data = QtCore.QMimeData()
        mime_data.setHtml(self.html_table)
        mime_data.setText(self.text)
        clipboard.setMimeData(mime_data)

    def _create_data(self, selection: list[QtCore.QItemSelectionRange]) -> None:
        """
        Создание 
        """

        rows = set()
        columns = set()
        for rng in selection:
            numbe_rows, number_column = self.current_model.get_visible_coords(rng.top(), rng.left(), rng.bottom(), rng.right())
            rows.add(numbe_rows)
            columns.add(number_column)
        
        self.rows = sorted([r for row in rows for r in row])
        self.columns = sorted([c for col in columns for c in col])

        lines_html = []
        lines_text = []
        for row in self.rows:
            html_line = []
            text_line = []
            for column in self.columns:
                cell = self.current_model.item_data.data[row][column]
                html_line.append(cell.get_td_html())
                text_line.append(str(cell.value))

            lines_html.append(f'<tr>{"".join(html_line)}</tr>')
            lines_text.append('\t'.join(text_line))
        
        self.html_table = fr'<table cellspacing="0" cellpadding="3" style="border-collapse: collapse;">{"".join(lines_html)}</table>'
        self.text = "\n".join(lines_text)

    def paste(self, target_model: ModelDataTable, row: int, column: int) -> None:
        if self.text == QtWidgets.QApplication.clipboard().text():
            target_model.paste_value_from_model(source_model=self.current_model, source_rows=self.rows, source_columns=self.columns, target_address=(row, column))
        else:
            target_model.paste_value_from_buffer(self.text, row, column)

                
CLIPBOARD = __Clipboard()