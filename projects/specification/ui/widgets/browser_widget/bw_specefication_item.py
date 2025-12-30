from PyQt5 import QtWidgets, QtCore, QtGui
import os

from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem
from projects.specification.config.app_context import SETTING

from projects.tools.functions.create_action_menu import create_action


class SpecificationItem(BrowserItem): 
    """
    Корневой элемент для таблиц соответствующего типа
    """
    def __init__(self, tree: QtWidgets.QTreeWidget, project_item, text: str, path_ico: str):
        super().__init__(tree, project_item)

        self.setText(text)
        self.set_icon(path_ico)

    def set_icon(self, path_ico: str) -> None:
        """
        Установка иконки слева для элемента дерева барузера
        
        :param path_ico: полный путь к иконки
        :type path_ico: str
        """
        icon = QtGui.QIcon()
        icon.addFile(path_ico)
        self.setIcon(0, icon)


class SpecificationInventorItem(SpecificationItem):
    def __init__(self, tree, project_item, text, path_ico):
        super().__init__(tree, project_item, text, path_ico)

    def add_action(self):
        super().add_action()

        create_action(menu=self.context_menu ,
            title='Загрузить файл .xlsx',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'excel.png'), 
            triggerd=self.load_specifecation_file_xlsx)
        
        create_action(menu=self.context_menu ,
            title='Получить из активного документа Inventorx',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'inventor.png'), 
            triggerd=self.get_specifeaction_active_inv_document)

    def load_specifecation_file_xlsx(self) -> None:
        ...

    def get_specifeaction_active_inv_document(self) -> None:
        ...

    