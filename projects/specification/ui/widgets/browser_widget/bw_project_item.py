from PyQt5 import QtWidgets

from projects.specification.config.app_context.app_context import app_context
from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem

from projects.specification.core.data_tables import PropertyProjectData


context_enums = app_context.context_enums


class ProjectItem(BrowserItem):
    def __init__(self, tree: QtWidgets.QTreeWidget):
        super().__init__(tree)

        self.type_item = context_enums.TYPE_TREE_ITEM.PROJET
        self.table_data: PropertyProjectData = PropertyProjectData()

        self.project_name = 'Новый проект'
        self.filepath: str = None
        self.setText(self.project_name)

    def set_project_name(self, text: str) -> None:
        self.project_name = text
        self.setText(self.project_name)

    def set_filepath(self, filepath: str) -> None:
        self.filepath = filepath
    
    def save(self) -> None:
        if self.filepath:
            self.table_data.save(self.filepath)
            self.set_is_init(True)
            self.set_is_save(True)