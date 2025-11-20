import os
from typing import Union, TypeVar, Iterable
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.settings import *
from projects.specification.config.enums import TypeTreeItem, EnumStatusBar
from projects.specification.config.constants import *
from projects.specification.core.data_tables import PropertyProjectData, InventorSpecificationDataItem
from projects.specification.core.database import DataBase

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.messege_box_question import MessegeBoxQuestion


TTData = TypeVar('T', PropertyProjectData, InventorSpecificationDataItem)


class BrowserItem(QtWidgets.QTreeWidgetItem):
    def __init__(self):
        super().__init__()

        self.type_item: TypeTreeItem = None
        self.project_name: str = None
        self.is_init: bool = False
        self.is_save: bool = False
        self.table_data: TTData = None
        self.database: DataBase = None

        # Для делегата
        self.setData(0, QROLE_LINK_ITEM_WIDGET_TREE, self)

    def setText(self, atext: str, column=0):
        return super().setText(column, atext)

    def text(self, column=0):
        return super().text(column)

    def set_database(self, database: DataBase) -> None:
        self.table_data.database = database


class ProjectItem(BrowserItem):
    def __init__(self, table_data: TTData):
        super().__init__()

        self.type_item = TypeTreeItem.PROJET
        self.table_data = table_data

        self.project_name = 'Новый проект'
        self.setText(self.project_name)

    def set_project_name(self, text: str) -> None:
        self.project_name = text
        self.setText(self.project_name)

    def populate_from_db(self) -> None:
        self.table_data.set_data(self.table_data.select_sql())
        self.set_project_name(self.table_data.get_data().get(self.table_data.columns[1].field))
    

class SpecItem(BrowserItem): 
    def __init__(self, text: str, path_ico: str):
        super().__init__()
        self.is_init = True
        self.is_save = True
        self.setText(text)

        icon = QtGui.QIcon()
        icon.addFile(path_ico)
        self.setIcon(0, icon)


class TableItem(BrowserItem): pass


class RightIconDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.green_color = QtGui.QColor(0, 240, 0)
        self.blue_color = QtGui.QColor(60, 60, 230)
        self.opacity_color = QtGui.QColor(0, 0, 0, 0)
        self.radius = 6
    
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        super().paint(painter, option, index)
        
        item: BrowserItem = index.model().itemData(index).get(QROLE_LINK_ITEM_WIDGET_TREE)
        color = self.blue_color
        rect = option.rect

        if not item.is_init:
            color = self.green_color
        elif not item.is_save:
            color = self.blue_color
        else:
            color = self.opacity_color
        
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        painter.drawEllipse(rect.right() - self.radius, rect.top() + (rect.height() - self.radius) // 2, self.radius, self.radius)
        

class ButtonBrowser(QtWidgets.QPushButton):
    def __init__(self, parent, tool_tip: str, name_ico: str):
        super().__init__(parent)
        
        self.setToolTip(tool_tip)
        self.setFixedSize(20, 20)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, name_ico))
        self.setIcon(icon)
       

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class WidgetBrowser(QtWidgets.QWidget):
    signal_select_item = QtCore.pyqtSignal(QtWidgets.QTreeWidgetItem)
    signal_del_item = QtCore.pyqtSignal()
    signal_open_project = QtCore.pyqtSignal()
    signal_status = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.init_widgets()
        self.create_project()

    def init_widgets(self) -> None:
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)

        self.setLayout(self.grid_layout)
        
        # --------------------------------- Frame Panel ---------------------------------------------- 
        self.frame_panel = QtWidgets.QFrame(self)
        self.h_layout_frame_panel = QtWidgets.QHBoxLayout(self.frame_panel)
        self.h_layout_frame_panel.setContentsMargins(2, 2, 2, 2)
        self.h_layout_frame_panel.setSpacing(2)
        self.frame_panel.setLayout(self.h_layout_frame_panel)
        self.grid_layout.addWidget(self.frame_panel, 0, 0, 1, 1)

        self.btn_open_project = ButtonBrowser(self.frame_panel, 'Открыть новый проект', 'open_folder.png')
        self.btn_open_project.setObjectName('btn_open_project')
        self.btn_open_project.clicked.connect(self.signal_open_project.emit)
        self.h_layout_frame_panel.addWidget(self.btn_open_project)

        self.btn_add_project = ButtonBrowser(self.frame_panel, 'Создать новый проект', 'green_plus.png')
        self.btn_add_project.setObjectName('btn_add_project')
        self.btn_add_project.clicked.connect(self.create_project)
        self.h_layout_frame_panel.addWidget(self.btn_add_project)

        self.btn_del_project = ButtonBrowser(self.frame_panel, 'Удалить проект из списка', 'red_minus.png')
        self.btn_del_project.setObjectName('btn_del_project')
        self.btn_del_project.clicked.connect(self.del_project)
        self.h_layout_frame_panel.addWidget(self.btn_del_project)

        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setPlaceholderText('Поиск')
        self.h_layout_frame_panel.addWidget(self.line_edit)

        # --------------------------------- Tree ---------------------------------------------- 
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setItemDelegate(RightIconDelegate(self))
        self.tree.setHeaderLabel('Проекты')
        self.tree.itemChanged.connect(self.change_tree_item)
        self.tree.itemPressed.connect(self.select_tree_item)
        self.grid_layout.addWidget(self.tree, 1, 0, 1, 1)

    def create_project(self) -> ProjectItem:
        database = DataBase()
        table_data = PropertyProjectData(database)
        project_item = ProjectItem(table_data)  
             
        self.tree.addTopLevelItem(project_item)
        self.tree.setCurrentItem(project_item)
        project_item.setExpanded(True)
        return project_item
    
    def create_main_item_project(self, project_item: QtWidgets.QTreeWidgetItem) -> None:
        spec_inv_item = SpecItem('Спецификация из Inventor', os.path.join(ICO_FOLDER, 'inventor.png'))
        spec_inv_item.project_name = project_item.text()
        spec_inv_item.type_item = TypeTreeItem.SPEC_FOLDER_INV
        project_item.addChild(spec_inv_item)

        spec_buy_item = SpecItem('Закупочная спецификация', os.path.join(ICO_FOLDER, 'dollars.png'))
        spec_buy_item.project_name = project_item.text()
        spec_buy_item.type_item = TypeTreeItem.SPEC_FOLDER_BUY
        project_item.addChild(spec_buy_item)

        spec_prod_item = SpecItem('Спецификация из Inventor', os.path.join(ICO_FOLDER, 'iam_image.png'))
        spec_prod_item.project_name = project_item.text()
        spec_prod_item.type_item = TypeTreeItem.SPEC_FOLDER_PROD
        project_item.addChild(spec_prod_item)

        project_item.setExpanded(True)

    def del_project(self) -> None:
        item: BrowserItem = self.tree.currentItem()

        if item.type_item == TypeTreeItem.PROJET:
            msg = MessegeBoxQuestion(self,
                                 question=f'Удалить проект {item.text(0)}?',
                                 title='Удаление проекта')
            if msg.exec_():
                root = self.tree.invisibleRootItem()
                for item in self.tree.selectedItems():
                    (item.parent() or root).removeChild(item)
                self.signal_del_item.emit()

    def get_filepath_projects(self) -> tuple[str, ...]:
        top_level_item: Iterable[ProjectItem] = (self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount()))
        return tuple(item.table_data.get_filepath() for item in top_level_item)

    def load_project(self, filepath_db: str) -> None:
        if filepath_db not in self.get_filepath_projects():
            project_item = self.create_project()

            table_data: PropertyProjectData = project_item.table_data
            key_project_name = table_data.config.columns[1].field
            table_data.set_filepath_db(filepath_db)
            table_data.set_data(table_data.select_sql())
            project_item.set_project_name(table_data.get_data().get(key_project_name))
            
            project_item.is_init = True
            project_item.is_save = True
            self.create_main_item_project(project_item)

            self.signal_status.emit(f'{EnumStatusBar.PROJECT_LOAD.value}: {project_item.project_name}')
        else:
            self.signal_status.emit(f'{EnumStatusBar.PROJECT_EXIST.value}: {os.path.basename(filepath_db)}')

    def change_tree_item(self, item: BrowserItem) -> None:
        if item.type_item == TypeTreeItem.PROJET:
            project_name = item.text()
            item.project_name = project_name
            self.update_project_name(item, project_name)
                
    def update_project_name(self, parent: BrowserItem, project_name: str) -> None:
        count = parent.childCount()
        if count > 0: 
            for i in range(count):
                child: BrowserItem = parent.child(i)
                child.project_name = project_name
                self.update_project_name(child, project_name)
        
    def select_tree_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        self.signal_select_item.emit(item)
    