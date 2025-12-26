from PyQt5 import QtWidgets

from projects.specification.config.app_context import DATACLASSES, ENUMS, SIGNAL_BUS
from  projects.specification.core.data_tables import InventorSpecificationDataItem

from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable

from projects.tools.custom_qwidget.messege_box_question import MessegeBoxQuestion



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

        self.init_context_menu()
    
    def init_context_menu(self):
        self.context_menu = QtWidgets.QMenu(self.tree)

        self.action_open_new_window = QtWidgets.QAction(self.context_menu)
        self.action_open_new_window.setText('Открыть в новом окне')
        self.context_menu.addAction(self.action_open_new_window)

        self.action_delete = QtWidgets.QAction(self.context_menu)
        self.action_delete.setText('Удалить')
        self.action_delete.triggered.connect(self.delete_table)
        self.context_menu.addAction(self.action_delete)
    
    def show_context_menu(self, position):
        self.context_menu.exec_(position)
    
    def delete_table(self) -> None:
        msg = MessegeBoxQuestion(self.tree, question='Удалить таблицу?', title='Удаление')
        if msg.exec():
            self.table_data.item_data.delete()
            self.parent_item.removeChild(self)
            SIGNAL_BUS.delele_item.emit()