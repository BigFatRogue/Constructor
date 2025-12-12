
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.ui.widgets.content_widget.cw_page import PageContent
from projects.specification.ui.widgets.table_widget.table_widget import TableWidget


class PageTable(PageContent):
    signal_status = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        self.init_widgets()

    def init_widgets(self) -> None:
        self.widget_table = TableWidget(self)
        self.widget_table.signal_has_change_table.connect(self.change_table)
        self.v_layout.addWidget(self.widget_table)

    def populate(self, item):
        super().populate(item)
        self.widget_table.populate(item.table_data)

    def change_table(self) -> None:
        self.current_item.set_is_init(True)
        self.current_item.set_is_save(False)
    
    def save(self) -> None:
        self.signal_status.emit(f'Таблица {self.current_item.text(0)} сохранена')