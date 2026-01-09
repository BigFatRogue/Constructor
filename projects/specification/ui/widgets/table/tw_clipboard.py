
from PyQt5 import QtWidgets, QtCore

from projects.specification.core.data_tables import SpecificationDataItem
from projects.specification.config.app_context import DATACLASSES
from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable


class __Clipboard:
    def __init__(self):
        self.current_model: ModelDataTable = None
        self.top: int = None
        self.left: int = None
        self.bottom: int = None
        self.rigth: int = None
        self.html_table: str = None
        self.text: str = None
    
    def copy(self, model: ModelDataTable, top: int, left: int, bottom: int, rigth: int) -> None:
        self.current_model = model
        self.top = top
        self.left = left
        self.bottom = bottom
        self.rigth = rigth
        
        self._create_data()

        clipboard = QtWidgets.QApplication.clipboard()
        mime_data = QtCore.QMimeData()
        mime_data.setHtml(self.html_table)
        mime_data.setText(self.text)
        clipboard.setMimeData(mime_data)

    def _create_data(self) -> None:
        """
        Создание 
        """
        lines_html = []
        lines_text = []
        for row in range(self.top, self.bottom + 1):
            html_line = []
            text_line = []
            for column in range(self.left, self.rigth + 1):
                cell = self.current_model.item_data.data[row][column]
                html_line.append(cell.get_td_html())
                text_line.append(cell.value)

            lines_html.append(f'<tr>{"".join(html_line)}</tr>')
            lines_text.append('\t'.join(lines_text))
        
        self.html_table = fr'<table cellspacing="0" cellpadding="3" style="border-collapse: collapse;">{"".join(lines_html)}</table>'
        self.text = "\n".join(lines_text)

    def paste(self, target_model: ModelDataTable, row: int, column: int) -> list[list[DATACLASSES.DATA_CELL]]:
        if self.text == QtWidgets.QApplication.clipboard().text():
            target_model.paste_value_from_model(source_model=self.current_model, source_coords=(self.top, self.left, self.bottom, self.rigth), target_top_left=(row, column))
        else:
            target_model.paste_value_from_buffer(self.text, row, column)
            # for target_row, source_row in zip(range(row, row + self.bottom - self.top + 1), range(self.top, self.bottom + 1)):
            #     for target_column, source_column in zip(range(column, column + self.rigth - self.left + 1), range(self.left, self.rigth + 1)):
            #         target_cell = target_model.item_data.data[target_row][target_column]
            #         source_cell = self.current_model.item_data.data[source_row][source_column]
            #         target_cell.set_property_from_cell(source_cell)
                
CLIPBOARD = __Clipboard()