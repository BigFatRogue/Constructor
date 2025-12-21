
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.app_context.app_context import ENUMS

from projects.specification.ui.widgets.content_widget.cw_page import PageContent
from projects.specification.ui.widgets.table_widget.table_widget import TableWidget
from projects.specification.ui.widgets.table_widget.tw_control_panel import ControlPanelTable
from projects.specification.ui.widgets.table_widget.tw_blocks_control_panel import AlignCellBlock, FontStyleBlock
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem


class PageTable(PageContent):
    signal_status = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        self.widget_table = TableWidget(self)
        self.widget_table.signal_change_table.connect(self.change_table)
        self.v_layout.addWidget(self.widget_table)

    def populate(self, item: SpecificationItem):
        super().populate(item)
        if item.type_item == ENUMS.TYPE_TREE_ITEM.TABLE_INV:
            self.widget_table.set_item(item)
        elif item.type_item == ENUMS.TYPE_TREE_ITEM.TABLE_BUY:
            ...
        elif item.type_item == ENUMS.TYPE_TREE_ITEM.TABLE_PROD:
            ...

    def change_table(self) -> None:
        self.current_item.set_is_init(True)
        self.current_item.set_is_save(False)
    
    def save(self) -> None:
        # self.widget_table.save()
        self.signal_status.emit(f'Таблица {self.current_item.text(0)} сохранена')