from PyQt5 import QtWidgets
import os

from projects.specification.config.app_context import SIGNAL_BUS, ENUMS, SETTING

from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem
from projects.specification.ui.widgets.table.tw_data_table import ModelDataTable

from projects.specification.core.data_tables import SpecificationDataItem

from projects.tools.custom_qwidget.messege_box_question import MessegeBoxQuestion
from projects.tools.functions.create_action_menu import create_action


class TableBrowserItem(BrowserItem):
    """
    Базовый элемент дерева браузера для таблиц
    """
    def __init__(self, 
                tree: QtWidgets.QTreeWidget, 
                parent_item: SpecificationItem, 
                name: str, 
                table_data: ModelDataTable,
                item_data: SpecificationDataItem,
                type_item: ENUMS.TYPE_TREE_ITEM.TABLE_INV):
        
        super().__init__(tree, parent_item)
        self.table_data = table_data
        self.item_data: SpecificationDataItem = item_data
        self.type_item = type_item
        self.setText(name)

    def add_action(self) -> None:
        create_action(menu=self.context_menu ,
            title='Открыть в новом окне',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'open_new_window.png'),
            triggerd=self.open_new_window)
        
        create_action(menu=self.context_menu ,
            title='Сохранить',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'save.png'),
            triggerd=self.save)

        create_action(menu=self.context_menu ,
            title='Удалить',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'delete.png'),
            triggerd=self.delete_table)
        
        self.context_menu.addSeparator()

    def save(self):
        """
        Сохранение данных в БД из item_data и установка визуального статуса элемента 
        
        :param self: Описание
        """
        self.item_data.save()
        self.set_is_init(True)
        self.set_is_save(True)
        SIGNAL_BUS.satus_bar.emit(f'Таблица {self.text()} сохранена')
    
    def open_new_window(self) -> None:
        ...

    def delete_table(self) -> None:
        msg = MessegeBoxQuestion(self.tree, question='Удалить таблицу?', title='Удаление')
        if msg.exec():
            self.table_data.item_data.delete()
            self.parent_item.removeChild(self)
            SIGNAL_BUS.delele_item.emit()