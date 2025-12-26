from PyQt5 import QtWidgets

from projects.specification.config.app_context import SIGNAL_BUS, ENUMS

from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem
from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable



class TableBrowserItem(BrowserItem):
    """
    Базовый элемент дерева браузера для таблиц
    """
    def __init__(self, 
                tree: QtWidgets.QTreeWidget, 
                parent_item: SpecificationItem, 
                name: str, 
                table_data: DataTable,
                item_data: SpecificationItem,
                type_item: ENUMS.TYPE_TREE_ITEM.TABLE_INV):
        
        super().__init__(tree, parent_item)
        self.table_data = table_data
        self.item_data = item_data
        self.type_item = type_item
        self.setText(name)

    def save(self):
        """
        Сохранение данных в БД из item_data и установка визуального статуса элемента 
        
        :param self: Описание
        """
        self.item_data.save()
        self.set_is_init(True)
        self.set_is_save(True)
        SIGNAL_BUS.satus_bar.emit(f'Таблица {self.text()} сохранена')
    