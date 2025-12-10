from __future__ import annotations
from PyQt5 import QtWidgets

from projects.specification.config.enums import TypeTreeItem
from projects.specification.config.constants import *
from projects.specification.core.data_tables import  GeneralDataItem



class BrowserItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, tree: QtWidgets.QTreeWidget, browser, parent_item=None):
        super().__init__()
        self.tree = tree
        self.browser = browser
        self.type_item: TypeTreeItem = None
        self.parent_item: BrowserItem = parent_item
        self.__is_init: bool = False
        self.__is_save: bool = False
        self.filepath: str = None
        self.table_data: GeneralDataItem = None

        # Для делегата
        self.setData(0, QROLE_LINK_ITEM_WIDGET_TREE, self)

    def setText(self, atext: str, column=0):
        return super().setText(column, atext)

    def text(self, column=0):
        return super().text(column)
    
    @property
    def is_init(self) -> bool:
        return self.__is_init
    
    @property
    def is_save(self) -> bool:
        return self.__is_save

    def set_is_init(self, value: bool) -> None:
        self.__is_init = value
        if self.table_data:
            self.table_data.set_is_init(value)
        self.tree.update()

    def set_is_save(self, value: bool) -> None:
        self.__is_save = value
        if self.table_data:
            self.table_data.set_is_save(value)
        self.tree.update()

    def save(self, *args) -> None:
        ...