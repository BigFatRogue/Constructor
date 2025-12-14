
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.ui.widgets.content_widget.cw_page import PageContent
from projects.specification.ui.widgets.table_widget.table_widget import TableWidget
from projects.specification.ui.widgets.table_widget.tw_control_panel import ControlPanelTable
from projects.specification.ui.widgets.table_widget.tw_blocks_control_panel import AlignCellBlock, FontStyleBlock


class PageInventorTable(PageContent):
    signal_status = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        self.init_widgets()

    def init_widgets(self) -> None:
        self.widget_table = TableWidget(self)
        control_panel: ControlPanelTable = self.widget_table.set_control_panel()
        control_panel.add_block(FontStyleBlock)
        control_panel.add_block(AlignCellBlock)

        self.widget_table.signal_change_table.connect(self.change_table)
        self.v_layout.addWidget(self.widget_table)

    def populate(self, item):
        super().populate(item)
        self.widget_table.populate(item)

    def change_table(self) -> None:
        self.current_item.set_is_init(True)
        self.current_item.set_is_save(False)
    
    def save(self) -> None:
        self.widget_table.save()
        self.signal_status.emit(f'Таблица {self.current_item.text(0)} сохранена')