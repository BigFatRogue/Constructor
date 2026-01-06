from __future__ import annotations
import os
from typing import Union, Iterable
from PyQt5 import QtCore, QtWidgets, QtGui


from projects.specification.config.app_context import SETTING, SIGNAL_BUS, ENUMS, DATACLASSES

from projects.specification.core.data_tables import  GeneralDataItem, PropertyProjectData, InventorSpecificationDataItem, BuySpecificationDataItem, ProdSpecificationDataItem
from projects.specification.core.functions import get_now_time
from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx

from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem
from projects.specification.ui.widgets.browser_widget.bw_project_item import ProjectItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem, SpecificationInventorItem
from projects.specification.ui.widgets.browser_widget.bw_table_inventor_item import TableInventorItem
from projects.specification.ui.widgets.browser_widget.bw_table_by_item import TableByItem

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.messege_box_question import MessegeBoxQuestion
from projects.tools.functions.create_action_menu import create_action


class RightDrawDelegate(QtWidgets.QStyledItemDelegate):
    """
    Делегат для отрисовки кружка справа от надписи в QTreeItem
    """
    # TODO 
    # Изменить. Если содержиоме элемента было измененно, то цвет текста становится синими, а возле родительского
    # элемента появляется синий кружок. Соответсвтенно, если новый элемент, но зелёные цвета
    def __init__(self, parent=None):
        super().__init__(parent)
        self.green_color = QtGui.QColor(0, 240, 0)
        self.blue_color = QtGui.QColor(60, 60, 230)
        self.opacity_color = QtGui.QColor(0, 0, 0, 0)
        self.radius = 6
    
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        super().paint(painter, option, index)
        
        item: BrowserItem = index.model().itemData(index).get(ENUMS.CONSTANTS.QROLE_LINK_ITEM_WIDGET_TREE.value)
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
    """
    Стандартная кнопка над QWIdgetTree
    """
    def __init__(self, parent, tool_tip: str, name_ico: str):
        super().__init__(parent)
        
        self.setToolTip(tool_tip)
        self.setFixedSize(20, 20)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(SETTING.ICO_FOLDER, name_ico))
        self.setIcon(icon)


class Tree(QtWidgets.QTreeWidget):
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            event.accept()
            return super().mousePressEvent(event)
    

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class BrowserWidget(QtWidgets.QWidget):
    """
    Браузер для отображения и создания проектов и их таблиц
    """
    def __init__(self, parent):
        super().__init__(parent)
        self._current_item: BrowserItem = None
        self._prev_item: BrowserItem = None

        SIGNAL_BUS.load_specification_from_xlsx.connect(self.load_specification_from_xlsx)
        SIGNAL_BUS.data_by_from_invetor.connect(self.inventor_table_to_by)

        self.init_widgets()
        self.init_context_menu()

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

        self.btn_add_project = ButtonBrowser(self.frame_panel, 'Создать новый проект', 'green_plus.png')
        self.btn_add_project.setObjectName('btn_add_project')
        self.btn_add_project.clicked.connect(self.create_project)
        self.h_layout_frame_panel.addWidget(self.btn_add_project)

        self.btn_open_project = ButtonBrowser(self.frame_panel, 'Открыть новый проект', 'open_folder.png')
        self.btn_open_project.setObjectName('btn_open_project')
        self.btn_open_project.clicked.connect(SIGNAL_BUS.open_project.emit)
        self.h_layout_frame_panel.addWidget(self.btn_open_project)

        # self.btn_del_project = ButtonBrowser(self.frame_panel, 'Удалить проект из списка', 'red_minus.png')
        # self.btn_del_project.setObjectName('btn_del_project')
        # self.btn_del_project.clicked.connect(self.del_project)
        # self.h_layout_frame_panel.addWidget(self.btn_del_project)

        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setPlaceholderText('Поиск')
        self.h_layout_frame_panel.addWidget(self.line_edit)

        # --------------------------------- Tree ---------------------------------------------- 
        self.tree = Tree(self)
        self.tree.setItemDelegate(RightDrawDelegate(self))
        self.tree.setHeaderLabel('Проекты')
        self.tree.itemPressed.connect(self.select_tree_item)
        self.grid_layout.addWidget(self.tree, 1, 0, 1, 1)

    def init_context_menu(self) -> None:
        self.tree.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        self.context_menu = QtWidgets.QMenu(self.tree)
        
        create_action(menu=self.context_menu, 
            title='Открыть проект', 
            filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'open_folder.png'),
            triggerd=SIGNAL_BUS.open_project.emit)
        
        create_action(menu=self.context_menu, 
                title='Создать новый проект', 
                filepath_icon=os.path.join(SETTING.ICO_FOLDER, 'green_plus.png'),
                triggerd=self.create_project)


    def show_context_menu(self, position: QtCore.QPoint) -> None:
        item: BrowserItem = self.tree.itemAt(position)
        if item:
            item.show_context_menu(self.tree.viewport().mapToGlobal(position))
        else:
            self.context_menu.exec_(self.tree.viewport().mapToGlobal(position))

    def create_project(self) -> ProjectItem:
        """
        Создание корневого элемента проекта
        
        :return: коренвой элемент проекта
        :rtype: ProjectItem
        """
        
        project_item = ProjectItem(self.tree)  
        project_item.setExpanded(True)

        self.tree.addTopLevelItem(project_item)
        self.tree.setCurrentItem(project_item)

        self.select_tree_item(project_item)
        
        return project_item
    
    def create_main_item_project(self, project_item: ProjectItem) -> None:
        """
        Создание элементов (папок) в коренвом элементе проекта:\n
        - Спецификации Inventor\n
        - Закупочная спецификация\n
        - Спецификация на производство
        
        :param project_item: корневой элемент проекта
        :type project_item: ProjectItem
        """

        spec_inv_item = SpecificationInventorItem(self.tree, project_item, 'Спецификация из Inventor', os.path.join(SETTING.ICO_FOLDER, 'iam_image.png'))
        spec_inv_item.parent_item = project_item
        spec_inv_item.type_item = ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_INV
        spec_inv_item.filepath = project_item.filepath
        spec_inv_item.set_is_init(True)
        spec_inv_item.set_is_save(True)
        project_item.addChild(spec_inv_item)

        spec_buy_item = SpecificationItem(self.tree, project_item, 'Закупочная спецификация', os.path.join(SETTING.ICO_FOLDER, 'dollars.png'))
        spec_buy_item.parent_item = project_item
        spec_buy_item.type_item = ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_BUY
        spec_buy_item.filepath = project_item.filepath
        spec_buy_item.set_is_init(True)
        spec_buy_item.set_is_save(True)
        project_item.addChild(spec_buy_item)

        spec_prod_item = SpecificationItem(self.tree, project_item, 'Спецификация на производство', os.path.join(SETTING.ICO_FOLDER, 'iam_image.png'))
        spec_prod_item.parent_item = project_item
        spec_prod_item.type_item = ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_PROD
        spec_prod_item.filepath = project_item.filepath
        spec_prod_item.set_is_init(True)
        spec_prod_item.set_is_save(True)
        project_item.addChild(spec_prod_item)

        project_item.setExpanded(True)

    def del_project(self) -> None:
        item: BrowserWidget = self.tree.currentItem()

        if item.type_item == ENUMS.TYPE_TREE_ITEM.PROJET:
            msg = MessegeBoxQuestion(self,
                                 question=f'Удалить проект {item.text(0)}?',
                                 title='Удаление проекта')
            if msg.exec_():
                root = self.tree.invisibleRootItem()
                for item in self.tree.selectedItems():
                    (item.parent() or root).removeChild(item)
                SIGNAL_BUS.delele_item.emit()

    def get_filepath_projects(self) -> tuple[str, ...]:
        """
        Полыный путь к файлу проекта (файл формата <MYFORMAT>)
        """
        top_level_item: Iterable[ProjectItem] = (self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount()))
        return tuple(item.item_data.get_filepath() for item in top_level_item)
    
    def open_project(self, filepath: str) -> None:
        """
        Загрузка свойств проекта и всех таблиц 
        
        :param filepath: полный путь к файлу проекта (файл формата <MYFORMAT>)
        :type filepath: str
        """
        if filepath not in self.get_filepath_projects():
            project_item = self.create_project()
            project_item.set_filepath(filepath)
            self.create_main_item_project(project_item)

            item_data: PropertyProjectData = project_item.item_data
            tables = item_data.load_project(filepath)
            key_project_name = item_data.config.columns[1].field
            project_item.set_project_name(item_data.get_data().get(key_project_name))
            
            if tables:
                self.__load_tables(project_item=project_item, tables=tables)
            self.select_tree_item(project_item)
            
            project_item.set_is_init(True)
            project_item.set_is_save(True)

            SIGNAL_BUS.satus_bar.emit(f'{ENUMS.STATUS_BAR.PROJECT_LOAD.value}: {project_item.project_name}')
        else:
            SIGNAL_BUS.satus_bar.emit(f'{ENUMS.STATUS_BAR.PROJECT_EXIST.value}: {os.path.basename(filepath)}')

    def __load_tables(self, project_item: ProjectItem, tables: dict[str, str | list[list]]) -> None:
        """
        Загрузка таблиц из БД для проекта
        
        :param project_item: корневой элемент проекта
        :type project_item: ProjectItem
        :param tables: словарь с данными по таблицам
        :type tables: dict[str, Union[str, list[list]]]
        """
        dict_type_item_tree: dict[int, SpecificationItem] = {}
        for i in range(project_item.childCount()):
            child: SpecificationItem = project_item.child(i)
            dict_type_item_tree[child.type_item] = child
        
        for table in tables:
            name = table['name_spec']
            tp = table['type_spec']
            create_date = table['datetime']
            data = table['data']
            header_data = table['header_data']
            table_data = table['table_data']
            data_link = table['links']
            sid = table['id']
            
            if tp == ENUMS.NAME_TABLE_SQL.INVENTOR.value:
                parent_item = dict_type_item_tree[ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_INV]
                item = self.create_intentor_table(parent_item=parent_item, name=name, data=data)
                item.item_data.set_header_data(header_data)
                item.item_data.set_table_data(table_data)
                item.item_data.set_sid(sid)
                item.set_is_init(True)
                item.set_is_save(True)
            elif tp == ENUMS.NAME_TABLE_SQL.BUY.value:
                parent_item = dict_type_item_tree[ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_BUY]
                item = self.create_by_table(parent_item=parent_item, name=name, data=data, data_link=data_link)
                item.item_data.set_table_data(table_data)
                item.item_data.set_header_data(header_data)
                item.item_data.set_sid(sid)
                item.set_is_init(True)
                item.set_is_save(True)
            elif tp == ENUMS.NAME_TABLE_SQL.PROD.value:
                ...

    def load_specification_from_xlsx(self, filepath) -> None:
        """
        Загрузка специфифкации Inventor из файла xlxs и добавлении в проект элемента
        
        :param self: полный путь к файлу xlsx
        :param filepath: Описание
        """
        data = get_specifitaction_inventor_from_xlsx(filepath)
        parent_item: SpecificationItem = self.tree.currentItem()
        self.create_intentor_table(parent_item=parent_item, name=f'Cпецификация inventor № {parent_item.childCount() + 1}', data=data)
    
    def inventor_table_to_by(self, value: tuple[TableInventorItem, list[list[DATACLASSES.DATA_CELL]]]) -> None:
        inv_item , data = value
        project_item: ProjectItem = inv_item.parent_item.parent_item
        
        parent_item: SpecificationItem = None
        for i in range(project_item.childCount()):
            child_item: SpecificationItem = project_item.child(i)
            if child_item.type_item == ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_BUY:
                parent_item = child_item
                break
        
        if parent_item:
            self.create_by_table(parent_item=parent_item, name=f'Закупочная спецификация № {parent_item.childCount() + 1}', data=data)
            
    def select_tree_item(self, item: BrowserItem) -> None:
        """
        Выбор элемента в браузере и оправка сигнала. Приниматель сигнала ContentWidget
        
        :param item: элемент браузера
        :type item: BrowserItem
        """
        item.set_is_active(False)

        if self._current_item is None:
            self._current_item = item
            self._prev_item = item
        
        self._prev_item = self._current_item
        self._current_item = item

        self._prev_item.set_is_active(False)
        self._current_item.set_is_active(True)
        
        SIGNAL_BUS.select_item_browser.emit(item)
    
    def save(self) -> None:
        """
        Сохранение данных в БД.Модель данных хранится в элементе дерева браузера 
        
        """
        item: BrowserItem = self.tree.currentItem()
        
        if not item.is_save:
            if isinstance(item, ProjectItem) and not item.is_init and item.filepath:
                self.create_main_item_project(item)
            
            item.save()

    def create_intentor_table(self, parent_item: SpecificationItem, name: str, data: list[list[DATACLASSES]]) -> TableInventorItem:
        intentor_item = TableInventorItem(tree=self.tree, parent_item=parent_item, name=name, data=data)        
        parent_item.addChild(intentor_item)
        parent_item.setExpanded(True)
        SIGNAL_BUS.satus_bar.emit(f'Таблица {intentor_item.text()} загружена')
        return intentor_item

    def create_by_table(self, parent_item: SpecificationItem, name: str, data: list[list[DATACLASSES]], data_link: dict[int, list[list[DATACLASSES.DATA_CELL]]] = None) -> TableByItem:
        by_item = TableByItem(tree=self.tree, parent_item=parent_item, name=name, data=data, data_link=data_link)        
        parent_item.addChild(by_item)
        parent_item.setExpanded(True)
        SIGNAL_BUS.satus_bar.emit(f'Таблица {by_item.text()} загружена')
        return by_item
