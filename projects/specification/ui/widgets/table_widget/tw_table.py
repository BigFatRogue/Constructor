import os
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.app_context.app_context import DATACLASSES

from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem

from projects.specification.core.data_tables import ColumnConfig, InventorSpecificationDataItem, SpecificationDataItem

from projects.specification.ui.widgets.table_widget.tw_table_item import TableItem
from projects.specification.ui.widgets.table_widget.tw_horizontal_header import HorizontalWithOverlayWidgets, ButtonHorizontalHeader
from projects.specification.ui.widgets.table_widget.tw_vertical_header import VerticallWithOverlayWidgets, CheckBoxVerticalHeader



class Table(QtWidgets.QTableWidget):
    signal_sorted_column = QtCore.pyqtSignal(tuple)
    signal_sorted_columns = QtCore.pyqtSignal(list)
    signal_zoom_in = QtCore.pyqtSignal()  
    signal_zoom_out = QtCore.pyqtSignal() 
    signal_resize_header =  QtCore.pyqtSignal() 

    def __init__(self, parent, min_zoom: int=0, max_zoom: int=450, step_zoom: int=10):
        super().__init__(parent)
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.step_zoom = step_zoom

        self.current_item_tree: TableBrowserItem = None 

        self.has_horizontal_filter = True
        self.has_vertical_check_box = True

        self.custom_horizontal_header: None | HorizontalWithOverlayWidgets = None
        self.custom_vertical_header: None | VerticallWithOverlayWidgets = None
        
        self.is_read_only = True

        self.setWordWrap(False)
        
        self.is_populate = False
        self.itemChanged.connect(self.item_change)

    def setRowCount(self, rows):
        super().setRowCount(rows)
        if self.custom_vertical_header is None:
            self.custom_vertical_header = VerticallWithOverlayWidgets(self)
            self.custom_vertical_header.sectionResized.connect(self.signal_resize_header.emit)
            self.setVerticalHeader(self.custom_vertical_header)
        if self.has_vertical_check_box: 
            for i in range(len(self.custom_vertical_header.widgets), rows):
                check_box = CheckBoxVerticalHeader(self)
                self.custom_vertical_header.add_widget(check_box)

    def setColumnCount(self, columns):
        super().setColumnCount(columns)
        
        if self.custom_horizontal_header is None:
            self.custom_horizontal_header = HorizontalWithOverlayWidgets(self)
            self.custom_horizontal_header.sectionResized.connect(self.signal_resize_header.emit)
            self.setHorizontalHeader(self.custom_horizontal_header)
        if self.has_horizontal_filter: 
            for i in range(len(self.custom_horizontal_header.widgets), columns):
                btn = ButtonHorizontalHeader(self)
                self.custom_horizontal_header.add_widget(btn)

    def populate(self, item: SpecificationItem, has_horizontal_filter: bool=True, has_vertical_check_box: bool=True) -> None:
        self.is_populate = True
        self.has_horizontal_filter = has_horizontal_filter
        self.has_vertical_check_box = has_vertical_check_box

        self.current_item_tree = item
        table_data: SpecificationDataItem = item.table_data
        dataset = table_data.get_data()
        columns: tuple[ColumnConfig] = table_data.config.columns + table_data.unique_config.columns
        columns_name: tuple[str, ...] = tuple(col.column_name for col in columns if col.is_view)
        
        self.setRowCount(len(dataset))
        self.setColumnCount(len(columns_name))
        self.setHorizontalHeaderLabels(columns_name)
        
        data_number_index = table_data.get_index_from_name_filed('number_row')

        for y, row in enumerate(dataset):            
            if data_number_index != -1:
                row[data_number_index] = y
            x = 0
            for col, cell in zip(columns, row):
                if col.is_view:
                    qItem = TableItem(self.min_zoom, self.max_zoom, self.step_zoom)
                    qItem.set_cell(cell, is_read_only=False)
                    self.setItem(y, x, qItem)
                    x += 1
        
        self.is_populate = False

    def item_change(self, item: TableItem) -> None:
        if not self.is_populate:
            self.current_item_tree.table_data.set_cell(item.row(), item.column(), item.get_cell())

    # def sorted_column(self, state_sorted) -> None:
    #     if self.popup_order.is_multi_sorted:
    #         self.signal_sorted_columns.emit(self.custom_h_header.get_widgets())
    #     else:
    #         btn: ButtonHorizontalHeader = self.popup_order.current_button_header
    #         self.signal_sorted_column.emit((btn.data_index, state_sorted))
    #     self.signal_change_table.emit()
            
    def reset_view_sorted_header(self) -> None:
        # TODO пренести в Header. Обнуление знакочков сортировки 
        for btn in self.custom_h_header.get_widgets():
            btn.reset_view_sorted()

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.signal_zoom_in.emit()
            else:
                self.signal_zoom_out.emit()
            event.accept()
        else:
            super().wheelEvent(event)


    def get_style_section(self) -> list[DATACLASSES.SECTION_STYLE]:
        style: list[DATACLASSES.SECTION_STYLE] = []
        
        for row in range(self.rowCount()):
            style.append(
                 DATACLASSES.SECTION_STYLE(
                    row=row,
                    column=-1,
                    size=self.verticalHeader().sectionSize(row)
                    )
            )

        for col in range(self.columnCount()):
            h_header = self.horizontalHeader()
            dt = DATACLASSES.SECTION_STYLE(
                row=-1,
                column=col,
                size=h_header.sectionSize(row)
            )

            if isinstance(h_header, HorizontalWithOverlayWidgets):
                widget: ButtonHorizontalHeader = h_header.widgets[col]
                dt.state_sorted = widget.state_sorted.value     

            style.append(dt)

        return style    
            
            

