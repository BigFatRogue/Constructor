from PyQt5 import QtWidgets, QtCore
import os

from projects.specification.config.app_context import DATACLASSES, ENUMS, SIGNAL_BUS, SETTING
from  projects.specification.core.data_tables import InventorSpecificationDataItem

from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem

from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable

from projects.tools.functions.create_action_menu import create_action


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
        
        item_data: InventorSpecificationDataItem = InventorSpecificationDataItem(parent_item.parent_item.item_data.database, table_name=name)
        item_data.set_data(data)
        table_data = ModelDataTable(item_data)
        table_data.signal_change.connect(lambda: self.set_is_save(False))
        type_item = ENUMS.TYPE_TREE_ITEM.TABLE_INV

        super().__init__(tree=tree, parent_item=parent_item, name=name, table_data=table_data, item_data=item_data, type_item=type_item)
        self.item_data: InventorSpecificationDataItem
    
    def add_action(self):
        super().add_action()

        create_action(menu=self.context_menu ,
            title='Сформировать закупочную спецификацию',
            triggerd=self.intentor_to_by)

        create_action(menu=self.context_menu ,
            title='Сформировать спецификацию на производство',
            triggerd=self.inventor_to_prod)

    def intentor_to_by(self) -> None:
        if not self.is_save:
            self.save()
        SIGNAL_BUS.data_by_from_invetor.emit((self, self.item_data.data_to_by()))

    def inventor_to_prod(self) -> None:
        ...