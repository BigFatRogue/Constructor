from PyQt5 import QtWidgets
import os

from projects.specification.config.app_context import ENUMS, SIGNAL_BUS, SETTING
from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem
from projects.specification.ui.widgets.browser_widget.bw_table_inventor_item import TableInventorItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationInventorItem

from projects.specification.core.data_tables import PropertyProjectData

from projects.tools.custom_qwidget.messege_box_question import MessegeBoxQuestion


from projects.tools.functions.create_action_menu import create_action


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
    
    def add_action(self):
        super().add_action()

        create_action(menu=self.context_menu ,
            title='Удалить проект из списка',
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'delete.png'), 
            triggerd=self.delete_project_from_list)
    
    def delete_project_from_list(self) -> None:
        msg = MessegeBoxQuestion(self.tree, question='Удалить проект из списка?', title='Удаление')
        if msg.exec():
            root = self.tree.invisibleRootItem()
            for item in self.tree.selectedItems():
                (item.parent() or root).removeChild(item)
            SIGNAL_BUS.delele_item.emit()
    
    def get_inventor_items(self) -> list[TableInventorItem]:
        lst = []
        for i in range(self.childCount()):
            project_child = self.child(i)
            if isinstance(project_child, SpecificationInventorItem):
                for j in range(project_child.childCount()):
                    lst.append(project_child.child(j))
        return lst