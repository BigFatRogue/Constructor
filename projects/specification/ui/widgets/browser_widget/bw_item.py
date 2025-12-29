from __future__ import annotations
from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Callable

from projects.specification.config.app_context import ENUMS

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable
from projects.specification.core.data_tables import GeneralDataItem



class BrowserItem(QtWidgets.QTreeWidgetItem):
    """
    Базовй элемент дерева браузера
    """
    def __init__(self, tree: QtWidgets.QTreeWidget, parent_item=None):
        super().__init__()
        self.tree = tree
        self._is_active: bool = False
        
        self.type_item: ENUMS.TYPE_TREE_ITEM = None
        self.parent_item: BrowserItem = parent_item
        self.__is_init: bool = False
        self.__is_save: bool = False
        self.filepath: str = None
        self.table_data: DataTable = None
        self.item_data: GeneralDataItem = None 

        # Для делегата
        self.setData(0, ENUMS.CONSTANTS.QROLE_LINK_ITEM_WIDGET_TREE.value, self)
        
        self.init_context_menu()
        self.add_action()

    def setText(self, atext: str, column=0):
        return super().setText(column, atext)

    def text(self, column=0):
        return super().text(column)
    
    @property
    def is_init(self) -> bool:
        """
        - False - если элемент был создан и не сохранён в БД
        - True - сохранён в БД
        """
        return self.__is_init
    
    @property
    def is_save(self) -> bool:
        """
        - False - элемент не сохранён
        - True - элемент сохранён
        """
        return self.__is_save

    def set_is_init(self, value: bool) -> None:
        """
        Установка статуса инициализирования в БД

        :param value: 
        - True - сохранён в БД
        - False - создан но не сохранён в БД
        """
        self.__is_init = value
        if self.item_data:
            self.item_data.set_is_init(value)
        self.tree.update()

    def set_is_save(self, value: bool) -> None:
        """
        Установка статуса сохранения изменений элемента

        :param value: 
        - True - изменения сохранены
        - False - изменения не сохранены
        """
        self.__is_save = value
        if self.item_data:
            self.item_data.set_is_save(value)
        self.tree.viewport().update()

    @property
    def is_active(self) -> bool:
        return self._is_active

    def set_is_active(self, value: bool) -> None:
        self._is_active = value

    def save(self, *args) -> None:
        """
        Переопределяемый метод в потомках, для сохранения
        """
        ...
    
    def init_context_menu(self) -> None:
        """
        Создание контекстного меню и добавления
        
        :param self: Описание
        """
        self.context_menu = QtWidgets.QMenu(self.tree)

    def show_context_menu(self, position: QtCore.QPoint) -> None:
        self.context_menu.exec_(position)
    
    def add_action(self) -> None:
        """
        Уникальные пункты для меню
        
        :param self: Описание
        """