import os
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context.app_context import SETTING, ENUMS, DATACLASSES


from projects.specification.core.database import DataBase
from projects.specification.core.data_tables import InventorSpecificationDataItem

from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem

from projects.specification.ui.widgets.table_widget.tw_table import Table
from projects.specification.ui.widgets.table_widget.tw_control_panel import ControlPanelTable
from projects.specification.ui.widgets.table_widget.tw_blocks_control_panel import AlignCellBlock, FontStyleBlock
from projects.specification.ui.widgets.table_widget.tw_selection_table import SelectionRect
from projects.specification.ui.widgets.table_widget.tw_zoom import ZoomTable


from projects.tools.custom_qwidget.line_separate import QHLineSeparate


class TableWidget(QtWidgets.QWidget):
    signal_change_table = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.current_tree_item: TableBrowserItem = None
        self.control_panel: ControlPanelTable = None
        self.table_data = None

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setSpacing(5)

        self.table = Table(self)

        # self.table.signal_sorted_column.connect(self.sorted_column)
        # self.table.signal_sorted_columns.connect(self.sorted_columns)
        # self.table.signal_change_table.connect(self.change_table)
        self.v_layout.addWidget(self.table)

        self.selection_rect = SelectionRect(self.table)
        self.table_zoom = ZoomTable(self, self.table)
        self.v_layout.addWidget(self.table_zoom)

        self.table_zoom.signal_change_zoom.connect(self.selection_rect.resize_rect)
        self.table.signal_resize_header.connect(self.selection_rect.resize_rect)
        self.table.signal_zoom_in.connect(self.table_zoom.zoom_in)
        self.table.signal_zoom_out.connect(self.table_zoom.zoom_out)

        self.table_zoom.signal_change_zoom.connect(self.signal_change_table.emit)
        self.table.signal_resize_header.connect(self.signal_change_table.emit)
        self.table.itemChanged.connect(self.signal_change_table.emit)

    def set_control_panel(self) -> ControlPanelTable:
        self.control_panel = ControlPanelTable(self, self.table)
        self.selection_rect.signal_view_style_cell.connect(self.control_panel.view_property)
        self.v_layout.insertWidget(0, self.control_panel)
        self.v_layout.addWidget(QHLineSeparate(self))
        return self.control_panel

    def populate(self, item: TableBrowserItem, is_read_only=True, has_horizontal_filter=True, has_vertical_check_box=True) -> None:
        self.current_tree_item = item
        is_init, is_save = self.current_tree_item.is_init, self.current_tree_item.is_save

        self.table_data: InventorSpecificationDataItem = item.table_data
        self.table.populate(item=item,
                            has_horizontal_filter=has_horizontal_filter,
                            has_vertical_check_box=has_vertical_check_box)
        
        self.current_tree_item.set_is_init(is_init)
        self.current_tree_item.set_is_save(is_save)
            
    # def sorted_column(self, data: tuple) -> None:
    #     index_data, state_sorted = data
    #     self.table_data.data.sort(key=lambda row: [str(i) for i in row][index_data], reverse=state_sorted == ENUMS.STATE_SORTED_COLUMN.SORTED)
    #     self.populate(table_data=self.table_data)
    #     self.table.reset_view_sorted_header()

    # def sorted_columns(self, buttons: list[ButtonHorizontalHeader]) -> None:  
    #     for btn in buttons[::-1]:
    #         if (state := btn.state_sorted) != ENUMS.STATE_SORTED_COLUMN.EMPTY:
    #             self.table_data.data.sort(key=lambda x: x[btn.data_index], reverse=state == ENUMS.STATE_SORTED_COLUMN.SORTED)
    #     self.populate(table_data=self.table_data)
    
    # def save(self) -> None:
    #     """
    #     Передаёт стили из таблицы в активный элемент барузера
    #     """
    #     self.current_tree_item.set_style(self.table.get_style_cells(), self.table.get_style_section())

    def change_table(self) -> None:
        self.signal_change_table.emit()



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
        control_panel = self.widgte_table.set_control_panel()
        control_panel.add_block(FontStyleBlock)
        control_panel.add_block(AlignCellBlock)
        self.v_layout.addWidget(self.widgte_table)
        
        table_data = InventorSpecificationDataItem(DataBase('a'))
        filepath = r'D:\Python\AlfaServis\Constructor\projects\specification\DEBUG\ALS.1642.5.3.05.01.00.000 - Инвентор.xlsx'
        table_data.set_data(get_specifitaction_inventor_from_xlsx(filepath))
        self.widgte_table.populate(table_data)
                


if __name__ == '__main__':
    from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx
    app = QtWidgets.QApplication(sys.argv)
    window = __Window()
    
    window.show()
    sys.exit(app.exec_())