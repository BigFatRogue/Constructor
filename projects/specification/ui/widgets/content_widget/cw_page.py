from PyQt5 import QtWidgets

from projects.specification.ui.widgets.browser_widget.bw_project_item import ProjectItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem
from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem


class PageContent(QtWidgets.QWidget):
    """
    Базовый класс страницы для контента
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.current_item: ProjectItem | SpecificationItem | TableBrowserItem = None
    
    def populate(self, item: ProjectItem | SpecificationItem | TableBrowserItem) -> None:
        """
        Заполнение страницу контентом
        
        :param item: элемент дерева (браузера)
        :type item: ProjectItem | SpecificationItem | TableBrowserItem
        """
        self.current_item = item

    def save(self) -> None:
        ...