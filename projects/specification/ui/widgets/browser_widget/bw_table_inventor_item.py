from PyQt5 import QtWidgets

from projects.specification.config.app_context import DATACLASSES, ENUMS
from  projects.specification.core.data_tables import InventorSpecificationDataItem

from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable



class TableInventorItem(TableBrowserItem):
    """
    Элемент дерева бразуера для таблицы Inventor
    """
    def __init__(self, 
                tree: QtWidgets.QTreeWidget, 
                parent_item: SpecificationItem,
                name: str,
                data: list[list[DATACLASSES.DATA_CELL]]
                ):
        
        item_data: InventorSpecificationDataItem = InventorSpecificationDataItem(parent_item.parent_item.item_data.database)
        item_data.set_data(data)
        table_data = DataTable(item_data)
        table_data.signal_change.connect(lambda: self.set_is_save(False))
        type_item = ENUMS.TYPE_TREE_ITEM.TABLE_INV

        super().__init__(tree=tree, parent_item=parent_item, name=name, table_data=table_data, item_data=item_data, type_item=type_item)
        self.item_data: InventorSpecificationDataItem