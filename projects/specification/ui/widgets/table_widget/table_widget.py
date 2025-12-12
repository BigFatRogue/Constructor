import os
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context.app_context import SETTING, SIGNAL_BUS, ENUMS, CONSTANTS


from projects.specification.core.database import DataBase
from projects.specification.core.data_tables import InventorSpecificationDataItem

from projects.specification.ui.widgets.table_widget.tw_table import Table, ButtonHorizontalHeader, CheckBoxVerticalHeader, TableItem
from projects.specification.ui.widgets.table_widget.tw_control_panel import ControlPanelTable
from projects.specification.ui.widgets.table_widget.tw_zoom import ZoomTable

from projects.tools.custom_qwidget.line_separate import QHLineSeparate


class TableWidget(QtWidgets.QWidget):
    signal_has_change_table = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.table_data = None
        self.init_widgets()

    def init_widgets(self) -> None:
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setSpacing(5)

        self.table = Table(self)
        self.table.signal_sorted_column.connect(self.sorted_column)
        self.table.signal_sorted_columns.connect(self.sorted_columns)
        self.table.signal_change_table.connect(self.change_table)

        self.control_panel = ControlPanelTable(self, self.table)
        
        self.table_zoom = ZoomTable(self, self.table)
        self.table_zoom.signal_change_zoom.connect(self.table.view_selection_rect)
        self.table.signal_zoom_in.connect(self.table_zoom.zoom_in)
        self.table.signal_zoom_out.connect(self.table_zoom.zoom_out)

        self.v_layout.addWidget(self.control_panel)
        self.v_layout.addWidget(QHLineSeparate(self))
        self.v_layout.addWidget(self.table)
        self.v_layout.addWidget(self.table_zoom)
        
    def populate(self, table_data: InventorSpecificationDataItem, is_read_only=True) -> None:
        self.table_data = table_data
        self.table.populate(table_data=table_data, is_read_only=is_read_only)
    
    def sorted_column(self, data: tuple) -> None:
        index_data, state_sorted = data
        self.table_data.data.sort(key=lambda row: [str(i) for i in row][index_data], reverse=state_sorted == ENUMS.STATE_SORTED_COLUMN.SORTED)
        self.populate(table_data=self.table_data)
        self.table.reset_view_sorted_header()

    def sorted_columns(self, buttons: list[ButtonHorizontalHeader]) -> None:  
        for btn in buttons[::-1]:
            if (state := btn.state_sorted) != ENUMS.STATE_SORTED_COLUMN.EMPTY:
                self.table_data.data.sort(key=lambda x: x[btn.data_index], reverse=state == ENUMS.STATE_SORTED_COLUMN.SORTED)
        self.populate(table_data=self.table_data)
        
    def select_cell_item(self, table_item: TableItem) -> None:
        self.control_panel.view_property(ENUMS.TYPE_BLOCK_PROPERTY_CONTROL_PANEL.ALIGN, table_item)
        self.control_panel.view_property(ENUMS.TYPE_BLOCK_PROPERTY_CONTROL_PANEL.FONT, table_item)

    def hide_popup_order(self) -> None:
        if self.table.popup_order.isVisible():
            self.table.popup_order.hide()

    def change_table(self) -> None:
        self.signal_has_change_table.emit()

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() == QtCore.Qt.Key_Escape:
            self.hide_popup_order()
        return super().keyPressEvent(e)


class __Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        with open(os.path.join(SETTING.RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', SETTING.ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        self.resize(750, 750)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.v_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.widgte_table = TableWidget(self)
        self.v_layout.addWidget(self.widgte_table)
        
        # dataset = [[f'({row} {cell})' for cell in range(9)] for row in range(120)]
        table_data = InventorSpecificationDataItem(DataBase('a'))
        filepath = r'C:\Users\p.golubev\Desktop\python\AfaLServis\Constructor\projects\specification\DEBUG\ALS.1642.5.3.01Из инвентора.xlsx'
        table_data.set_data(get_specifitaction_inventor_from_xlsx(filepath))
        self.widgte_table.populate(table_data)
                


if __name__ == '__main__':
    from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx
    app = QtWidgets.QApplication(sys.argv)
    window = __Window()
    
    window.show()
    sys.exit(app.exec_())