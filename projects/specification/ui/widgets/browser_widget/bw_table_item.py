from PyQt5 import QtWidgets

from projects.specification.config.app_context.app_context import DATACLASSES, ENUMS

from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem

from projects.specification.core.data_tables import SpecificationDataItem


class TableBrowserItem(BrowserItem):
    def __init__(self, 
                tree: QtWidgets.QTreeWidget, 
                parent_item: SpecificationItem, 
                name: str, 
                table_data: SpecificationDataItem,
                type_item: ENUMS.TYPE_TREE_ITEM.TABLE_INV):
        
        super().__init__(tree, parent_item)
        self.table_data: SpecificationDataItem = table_data
        self.type_item = type_item
        self.style_cells: DATACLASSES.CELL_STYLE = None
        self.style_section: DATACLASSES.SECTION_STYLE
        self.setText(name)
    

    def save(self):
        self.table_data.save()
        self.set_is_init(True)
        self.set_is_save(True)