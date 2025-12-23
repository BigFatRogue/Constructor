from typing import Union
from PyQt5 import QtCore, QtWidgets

from projects.specification.config.app_context import SETTING, SIGNAL_BUS, ENUMS

from projects.specification.ui.widgets.content_widget.cw_page import PageContent
from projects.specification.ui.widgets.content_widget.cw_empty_page import PageEmpty
from projects.specification.ui.widgets.content_widget.cw_property_project_page import PagePropertyProject
from projects.specification.ui.widgets.content_widget.cw_table_page import PageTable
from projects.specification.ui.widgets.content_widget.cw_init_project_page import PageInitProjectPage


from projects.specification.ui.widgets.browser_widget.bw_project_item import ProjectItem 
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem 
from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem 

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class ContentWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.current_item: ProjectItem | SpecificationItem | TableBrowserItem = None
        self.prev_item: ProjectItem | SpecificationItem | TableBrowserItem = None
        self.prev_page: PageContent = None

        self.init_widgets()

        SIGNAL_BUS.select_item_browser.connect(self.set_item)

    def init_widgets(self) -> None:
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        
        self.stacket = QtWidgets.QStackedWidget(self)
        self.v_layout.addWidget(self.stacket)

        self.page_empty = PageEmpty(self)
        self.index_page_empty = self.stacket.addWidget(self.page_empty)
        
        self.page_property_projcet = PagePropertyProject(self)
        
        self.index_page_property_projcet = self.stacket.addWidget(self.page_property_projcet)

        self.page_create_or_open_project = PageInitProjectPage(self, )
        self.index_page_create_or_open_project = self.stacket.addWidget(self.page_create_or_open_project)

        self.page_table = PageTable(self)
        self.index_page_table = self.stacket.addWidget(self.page_table)

        self.stacket.setCurrentIndex(0)

    def set_item(self, item: ProjectItem | SpecificationItem | TableBrowserItem) -> None:
        self.prev_item = self.current_item
        self.current_item = item

        if self.prev_item != self.current_item:
            current_page: PageContent = self.stacket.currentWidget()
            # current_page.update_data_item()

        tp = item.type_item
        if tp == ENUMS.TYPE_TREE_ITEM.PROJET:
            self.page_property_projcet.populate(item)
            self.stacket.setCurrentIndex(self.index_page_property_projcet)
        elif tp in (ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_INV, ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_BUY, ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_PROD):
            self.page_create_or_open_project.populate(item)
            self.stacket.setCurrentIndex(self.index_page_create_or_open_project)
        elif tp in (ENUMS.TYPE_TREE_ITEM.TABLE_INV, ENUMS.TYPE_TREE_ITEM.TABLE_BUY, ENUMS.TYPE_TREE_ITEM.TABLE_PROD):
            self.page_table.populate(item)
            self.stacket.setCurrentIndex(self.index_page_table)
    
    def view_empty_page(self) -> None:
        self.stacket.setCurrentIndex(self.index_page_empty)

    def save(self) -> None:
        widget: PageContent = self.stacket.currentWidget()
        widget.save()

       