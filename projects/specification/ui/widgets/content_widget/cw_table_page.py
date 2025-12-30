
from PyQt5 import QtCore, QtWidgets

from projects.specification.config.app_context import ENUMS

from projects.specification.ui.widgets.content_widget.cw_page import PageContent
from projects.specification.ui.widgets.table_widget.table_widget import TableWidget
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
        self.widget_table.set_item(item)

    def change_table(self) -> None:
        if self.current_item.is_init:
            self.current_item.set_is_save(False)

    def save(self) -> None:
        self.signal_status.emit(f'Таблица {self.current_item.text(0)} сохранена')