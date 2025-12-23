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
        if self.current_item is None or self.current_item != item:
            self.current_item = item
        else:
            return

    def update_data_item(self) -> None:
        ...

    def escape_tab(self) -> None:
        ...

    def save(self) -> None:
        ...