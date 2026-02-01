from PyQt5 import QtWidgets, QtCore

from projects.specification.config.app_context import DATACLASSES, ENUMS, SIGNAL_BUS
from  projects.specification.core.data_tables import ProdSpecificationDataItem

from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem

from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable

from projects.tools.functions.create_action_menu import create_action



class TableProdItem(TableBrowserItem):
    """
    Элемент дерева бразуера для таблицы на производство
    """

    def __init__(self, 
                tree: QtWidgets.QTreeWidget, 
                parent_item: SpecificationItem,
                name: str,
                data: list[list[DATACLASSES.DATA_CELL]],
                data_link: dict[int, list[list[DATACLASSES.DATA_CELL]]] = None
                ):
        
        item_data: ProdSpecificationDataItem = ProdSpecificationDataItem(parent_item.parent_item.item_data.database, table_name=name)
        if data_link is not None:
            item_data.set_data_link(data_link)
        item_data.set_data(data)
        item_data.set_is_update_link(True)
        table_data = ModelDataTable(item_data)
        table_data.set_editable(True)
        table_data.signal_change.connect(lambda: self.set_is_save(False))
        type_item = ENUMS.TYPE_TREE_ITEM.TABLE_PROD

        super().__init__(tree=tree, parent_item=parent_item, name=name, table_data=table_data, item_data=item_data, type_item=type_item)
        self.item_data: ProdSpecificationDataItem
    
    def set_link_from_data_inventor(self, data_inventor: list[list[DATACLASSES.DATA_CELL]]) -> None:
        self.item_data.set_link_from_data_inventor(data_inventor)
    