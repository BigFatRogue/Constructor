from PyQt5 import QtWidgets

from projects.specification.config.app_context.app_context import app_context
context_enums = app_context.context_enums

from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem

from projects.specification.core.data_tables import InventorSpecificationDataItem



class TableInventorItem(BrowserItem):
    def __init__(self, tree: QtWidgets.QTreeWidget, parent_item: SpecificationItem, name: str, data: list[list]=None):
        super().__init__(tree, parent_item)
        self.table_data = InventorSpecificationDataItem(parent_item.parent_item.table_data.database)
        self.type_item = context_enums.TYPE_TREE_ITEM.TABLE_INV
        self.setText(name)
        if data:
            self.table_data.set_data(data)
    
    def save(self):
        self.table_data.save()
        self.set_is_init(True)
        self.set_is_save(True)