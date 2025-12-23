from PyQt5 import QtWidgets

from projects.specification.config.app_context import ENUMS, SIGNAL_BUS
from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem

from projects.specification.core.data_tables import PropertyProjectData


class ProjectItem(BrowserItem):
    """
    Элемент дерева браузера для свойств проекта
    """
    def __init__(self, tree: QtWidgets.QTreeWidget):
        super().__init__(tree)

        self.type_item = ENUMS.TYPE_TREE_ITEM.PROJET
        self.item_data: PropertyProjectData = PropertyProjectData()

        self.project_name = 'Новый проект'
        self.filepath: str = None
        self.setText(self.project_name)

    def set_project_name(self, text: str) -> None:
        """
        Установка имени проекта (название в браузере)
        
        :param text: имя проекта
        :type text: str
        """
        self.project_name = text
        self.setText(self.project_name)

    def set_filepath(self, filepath: str) -> None:
        """
        Установка полного пути проекта
        
        :param filepath: полный путь проекта
        :type filepath: str
        """
        self.filepath = filepath
    
    def save(self) -> None:
        """
        Сохранения проекта в БД
        
        """
        if self.filepath:
            self.item_data.save(self.filepath)
            self.set_is_init(True)
            self.set_is_save(True)
            SIGNAL_BUS.satus_bar.emit(f'Проект <b>{self.project_name}</b> сохранён')