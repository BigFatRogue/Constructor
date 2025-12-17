from PyQt5 import QtWidgets

from projects.specification.config.app_context.app_context import DATACLASSES, ENUMS

from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem

from projects.specification.core.data_tables import InventorSpecificationDataItem



class TableInventorItem(TableBrowserItem):
    def __init__(self, 
                tree: QtWidgets.QTreeWidget, 
                parent_item: SpecificationItem,
                name: str,
                table_data: InventorSpecificationDataItem = None
                ):
        
        if table_data is None:
            table_data = InventorSpecificationDataItem(parent_item.parent_item.table_data.database)
        else:
            table_data = table_data
        type_item = ENUMS.TYPE_TREE_ITEM.TABLE_INV

        super().__init__(tree=tree, parent_item=parent_item, name=name, table_data=table_data, type_item=type_item)
    