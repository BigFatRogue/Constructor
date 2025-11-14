import sys
from typing import Optional, Union, Any
from collections import OrderedDict
import os
import ctypes
from enum import Enum, auto

from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.settings import *
from projects.specification.database import DataBase
from projects.specification.tables_config import TableConfigPropertyProject, TableConfigInventor
from projects.specification.data_process import load_data_to_db

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.h_line_separate import QHLineSeparate
from projects.tools.row_counter import RowCounter

class TypeTreeItem(Enum):
    PROJET = auto()
    SPEC_FOLDER_INV = auto()
    SPEC_FOLDER_BUY = auto()
    SPEC_FOLDER_PROD = auto()
    TABLE = auto()


class TypeCreateLoadSpec(Enum):
    LOAD_SPEC_FROM_XLSX = auto()
    LOAD_SPEC_FROM_ACTIVE_INV = auto()
    CREATE_SPEC_BUY_FROM_SPEC_INV = auto()
    CERATE_SPEC_BUY_EMPTY = auto()
    CREATE_SPEC_PROD_FROM_SPEC_BUY = auto()
    CREATE_SPEC_PROD_FROM_SPEC_INV = auto()
    CREATE_SPEC_PROD_EMPTY = auto()


QROLE_TYPE_TREE_ITEM = QtCore.Qt.UserRole                  #TypeTreeItem
QROLE_PROJCET_NAME = QtCore.Qt.UserRole + 1                #str
QROLE_STATUS_TREE_ITEM = QtCore.Qt.UserRole + 2            #bool
QROLE_CHANGE_PROPERTY_PROJECT = QtCore.Qt.UserRole + 3     #dict[str, QLineEdit]
QROLE_DATA_TREE_ITEM = QtCore.Qt.UserRole + 4              #dict[str, Any]


class TableWidget(QtWidgets.QTableWidget): 
    def __init__(self, parent):
        super().__init__(200, 10, parent)

    def fill_label_header(self, table_config: Union[TableConfigInventor]) -> None:
        labels = [col_name for col in table_config.columns if (col_name:=col.column_name)]
        self.setRowCount(len(labels))
        self.setHorizontalHeaderLabels(labels)

    def populate(self, dataset: list[list[Union[int, float, str]]]) -> None:
        for y, row in enumerate(dataset):
            for x, value in enumerate(row):
                qItem = QtWidgets.QTableWidgetItem(str(value))
                self.table.setItem(y, x, qItem)
                qItem.setFlags(QtCore.Qt.ItemIsEnabled)


class Table(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_widgets()
    
    def init_widgets(self) -> None:
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = TableWidget(self)
        self.table.fill_label_header(TableConfigInventor())
        self.grid_layout.addWidget(self.table)


class TabContent(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.current_item: QtWidgets.QTreeWidgetItem = None
    
    def activate(self) -> None:
        ...

    def escape_tab(self) -> None:
        ...


class TabPropertyProject(TabContent):
    def __init__(self, parent):
        super().__init__(parent)

        self.property_project = (
            ('Номер проекта <span style=color:red;>*</span>', 'Руководитель проекта'),
            ('Пункт договора', 'Инженер-технолог'),
            ('Адрес объекта', 'Инженер-конструктор'),
            ('Обозначение чертежа', 'Модель установки')
            )
        self.table_config = TableConfigPropertyProject()
        self.init_widgets()

    def init_widgets(self) -> None:
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.grid_layout)

        row_counter = RowCounter()

        self.label_project_filepath = QtWidgets.QLabel(self)
        self.label_project_filepath.setText('Распложение  файла')
        self.grid_layout.addWidget(self.label_project_filepath, row_counter.value, 0, 1, 1)

        self.lineedit_project_filepath = QtWidgets.QLineEdit(self)
        self.lineedit_project_filepath.setEnabled(False)
        self.grid_layout.addWidget(self.lineedit_project_filepath, row_counter.value, 1, 1, 2)

        h_line_separate = QHLineSeparate(self)
        self.grid_layout.addWidget(h_line_separate, row_counter.next(), 0, 1, 4)

        self.list_line_eidt: list[QtWidgets.QLineEdit] = []
        for config_col in self.table_config.columns[1:]:
            label = QtWidgets.QLabel(self)
            label.setText(config_col.column_name)
            self.grid_layout.addWidget(label, row_counter.next(), 0, 1, 1)

            lineedit = QtWidgets.QLineEdit(self)
            lineedit.textChanged.connect(self.change_lineedit)
            self.grid_layout.addWidget(lineedit, row_counter.value, 1, 1, 1)
            self.list_line_eidt.append(lineedit)

        self.btn_save_property_project = QtWidgets.QPushButton(self)
        self.btn_save_property_project.setText('Сохранить')
        self.btn_save_property_project.clicked.connect(self.click_save)
        self.grid_layout.addWidget(self.btn_save_property_project, row_counter.next(), 0, 1, 4)

    def click_save(self) -> None:
        ...

    def change_lineedit(self, text: str) -> None:
        if self.current_item:
            self.current_item.setData(0, QROLE_STATUS_TREE_ITEM, False)

    def activate(self) -> None:
        data = self.current_item.data(0, QROLE_DATA_TREE_ITEM)
        for db_columns, value in zip(self.table_config.columns[1:], self.list_line_eidt):
            value.setText(data[db_columns.field])

    def escape_tab(self) -> None:
        data = self.current_item.data(0, QROLE_DATA_TREE_ITEM)
        for db_columns, value in zip(self.table_config.columns[1:], self.list_line_eidt):
            data[db_columns.field] = value.text()
        self.current_item.setData(0, QROLE_DATA_TREE_ITEM, data)
        self.clear()

    def clear(self) -> None:
        for w in self.list_line_eidt:
            w.setText('')
        self.stacket.setCurrentIndex(0)


class TabCreateOrOpenProject(TabContent):
    def __init__(self, parent):
        super().__init__(parent)


class TabTable(TabContent):
    def __init__(self, parent):
        super().__init__(parent)


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class WidgetContent(QtWidgets.QWidget):
    signal_click_btn = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.curent_item: QtWidgets.QTreeWidgetItem = None
        self.prev_item: QtWidgets.QTreeWidgetItem = None
        self.prev_tab_widget: TabContent = None
        self.init_widgets()

    def init_widgets(self) -> None:
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        
        self.stacket = QtWidgets.QStackedWidget(self)
        self.stacket.currentChanged.connect(self.change_stacket_index)
        self.v_layout.addWidget(self.stacket)

        self.label_info = QtWidgets.QLabel(self)
        self.label_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_info.setText('Ничего не выбрано')
        self.index_label_info = self.stacket.addWidget(self.label_info)
        
        # --------------------------- Property project ----------------------------
        self.tab_property_projcet = TabPropertyProject(self)
        self.index_frame_property_project = self.stacket.addWidget(self.tab_property_projcet)

        self.frame_btn = QtWidgets.QFrame(self)
        self.index_frame_btn = self.stacket.addWidget(self.frame_btn)

        self.v_layout_frame_btn = QtWidgets.QVBoxLayout(self.frame_btn)
        self.v_layout_frame_btn.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.frame_btn.setLayout(self.v_layout_frame_btn)

        self.table = Table(self)
        self.index_table = self.stacket.addWidget(self.table)

        self.stacket.setCurrentIndex(0)

    def change_stacket_index(self, index: int) -> None:
        widget: TabContent = self.stacket.currentWidget()
        widget.current_item = self.curent_item 

        if self.prev_tab_widget:
            try:
                self.prev_tab_widget.escape_tab()
            except Exception:
                ...

        self.prev_tab_widget = widget
        
    def set_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        widget: TabContent = self.stacket.currentWidget()
        print(widget)
        widget.current_item = self.curent_item 
        
        if self.prev_tab_widget:
            try:
                widget.activate()
                self.prev_tab_widget.escape_tab()
            except Exception:
                ...

    def view_property_project(self) -> None:
        self.stacket.setCurrentIndex(1)

    def view_btn(self, data: OrderedDict[str, dict]) -> None:
        self.stacket.setCurrentIndex(2)
        list_exist_btn: list[QtWidgets.QPushButton] = [child for child in self.tab_property_projcet.children() if isinstance(child, QtWidgets.QPushButton)]
        len_list_exist_btn = len(list_exist_btn)
        
        for i, (text, value) in enumerate(data.items()):
            if i < len_list_exist_btn: 
                btn = list_exist_btn[i]
                if not btn.isVisible():
                    btn.show()
            else:
                btn = QtWidgets.QPushButton(self.frame_btn)
                btn.clicked.connect(self.click_btn)
                self.v_layout_frame_btn.addWidget(btn)
            btn.setText(text)
            btn.setProperty('data', value)

        if len(data) < len_list_exist_btn:
            for btn in list_exist_btn[len(data):]:
                btn.hide()

    def view_table(self) -> None:
        self.stacket.setCurrentIndex(3)

    def fill_table(self, data: list[list[Union[str, float]]]) -> None:
        ...

    def click_save(self) -> None:
        if self.curent_item:
            self.curent_item.setData(0, QROLE_STATUS_TREE_ITEM, True)

    def click_btn(self) -> None:
        self.signal_click_btn.emit(self.sender().property('data'))



class RightIconDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        super().paint(painter, option, index)
        
        status = index.model().itemData(index).get(QROLE_STATUS_TREE_ITEM)

        if status is not None and not status:
            rect = option.rect
            r = 6
            painter.setBrush(QtGui.QBrush(QtGui.QColor(60, 60, 230)))
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
            painter.drawEllipse(rect.right() - 15, rect.top() + (rect.height() - r) // 2, r, r)
        

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class WidgetBrowser(QtWidgets.QWidget):
    signal_select_item = QtCore.pyqtSignal(QtWidgets.QTreeWidgetItem)
    signal_del_item = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.init_widgets()

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

        self.btn_add_project = QtWidgets.QPushButton(self.frame_panel)
        self.btn_add_project.setToolTip('Добавить новый проект')
        self.btn_add_project.setObjectName('btn_add_project')
        self.btn_add_project.setFixedSize(20, 20)
        self.btn_add_project.setStyleSheet('#btn_add_project {border: none;} #btn_add_project:hover {background-color: rgb(209, 235, 255); border: 1px solid #0078d4;}')
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'green_plus.png'))
        self.btn_add_project.setIcon(icon)
        self.btn_add_project.clicked.connect(self.create_project)
        self.h_layout_frame_panel.addWidget(self.btn_add_project)

        self.btn_del_project = QtWidgets.QPushButton(self.frame_panel)
        self.btn_del_project.setToolTip('Удалить проект из списка')
        self.btn_del_project.setObjectName('btn_del_project')
        self.btn_del_project.setStyleSheet('#btn_del_project {border: none;} #btn_del_project:hover {background-color: rgb(209, 235, 255); border: 1px solid #0078d4;}')
        self.btn_del_project.setFixedSize(20, 20)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'red_minus.png'))
        self.btn_del_project.setIcon(icon)
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
        self.create_project()

    def create_project(self) -> None:
        project_item = QtWidgets.QTreeWidgetItem()
        project_item.setText(0, 'Новый проект')
        project_item.setData(0, QROLE_TYPE_TREE_ITEM, TypeTreeItem.PROJET)
        project_item.setData(0, QROLE_PROJCET_NAME, project_item.text(0))
        project_item.setData(0, QROLE_STATUS_TREE_ITEM, True)
        project_item.setData(0, QROLE_DATA_TREE_ITEM, {})
        project_item.setFlags(project_item.flags() | QtCore.Qt.ItemIsEditable)
        self.tree.addTopLevelItem(project_item)
        project_item.setExpanded(True)
        
        spec_inv_item = QtWidgets.QTreeWidgetItem()
        spec_inv_item.setText(0, 'Спецификация из Inventor')
        spec_inv_item.setData(0, QROLE_TYPE_TREE_ITEM, TypeTreeItem.SPEC_FOLDER_INV)
        spec_inv_item.setData(0, QROLE_PROJCET_NAME, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'inventor.png'))
        spec_inv_item.setIcon(0, icon)
        project_item.addChild(spec_inv_item)

        spec_buy_item = QtWidgets.QTreeWidgetItem()
        spec_buy_item.setText(0, 'Закупочная спецификация')
        spec_buy_item.setData(0, QROLE_TYPE_TREE_ITEM, TypeTreeItem.SPEC_FOLDER_BUY)
        spec_buy_item.setData(0, QROLE_PROJCET_NAME, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'dollars.png'))
        spec_buy_item.setIcon(0, icon)
        project_item.addChild(spec_buy_item)

        spec_prod_item = QtWidgets.QTreeWidgetItem()
        spec_prod_item.setText(0, 'Сборочная спецификация')
        spec_prod_item.setData(0, QROLE_TYPE_TREE_ITEM, TypeTreeItem.SPEC_FOLDER_PROD)
        spec_prod_item.setData(0, QROLE_PROJCET_NAME, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'iam_image.png'))
        spec_prod_item.setIcon(0, icon)
        project_item.addChild(spec_prod_item)

        self.tree.setCurrentItem(project_item)

    def del_project(self) -> None:
        item = self.tree.currentItem()
        if item.data(0, QROLE_TYPE_TREE_ITEM) == TypeTreeItem.PROJET:
            root = self.tree.invisibleRootItem()
            for item in self.tree.selectedItems():
                (item.parent() or root).removeChild(item)
        self.signal_del_item.emit()

    def change_tree_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        if item.data(0, QROLE_TYPE_TREE_ITEM) == TypeTreeItem.PROJET:
            item.setData(0, QROLE_PROJCET_NAME, item.text(0))
            self.update_project_name(item, item.text(0))
                
    def update_project_name(self, parent: QtWidgets.QTreeWidgetItem, project_name) -> None:
        count = parent.childCount()
        if count > 0: 
            for i in range(count):
                child = parent.child(i)
                child.setData(0, QROLE_PROJCET_NAME, project_name)
                self.update_project_name(child, project_name)
        
    def select_tree_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        self.signal_select_item.emit(item)
    

class WindowSpecification(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.databases: dict[str, DataBase] = {}
        self.path_project: str = None

        self.init_widnow()
        self.init_menubar()
        self.init_widgets()

    def init_widnow(self) -> None:
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ICO_FOLDER, 'Specification.png')))

        with open(os.path.join(RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        self.resize(1000, 400)
        self.setWindowTitle('КО спецификация')

        self.central_widget = QtWidgets.QWidget(self)
        self.central_widget.setObjectName("central_widget")

        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(2)

        self.setCentralWidget(self.central_widget)

    def init_menubar(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu('&Файл')

        open_action = QtWidgets.QAction('&Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

    def init_widgets(self) -> None:
        self.browser = WidgetBrowser(self)
        self.browser.setObjectName('browser')
        self.browser.signal_select_item.connect(self.select_item)
        
        self.widget_content = WidgetContent(self)
        self.widget_content.signal_click_btn.connect(self.load_content)
        # self.browser.signal_del_item.connect(self.widget_content.clear)
    
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.browser)
        splitter.addWidget(self.widget_content)
        splitter.setStretchFactor(1, 1)
        self.grid_layout.addWidget(splitter, 0, 0, 1, 1)

    def select_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        tp = item.data(0, QROLE_TYPE_TREE_ITEM)
        project_name = item.data(0, QROLE_PROJCET_NAME)
        self.widget_content.set_item(item)
        
        if tp == TypeTreeItem.PROJET:
            self.widget_content.view_property_project()
        elif tp == TypeTreeItem.SPEC_FOLDER_INV:
            btn_data = OrderedDict([
                ('Загрузить файл .xlsx', {'type': TypeCreateLoadSpec.LOAD_SPEC_FROM_XLSX, 'project_name': project_name}),
                ('Получить из активного документа Inventor', {'type': TypeCreateLoadSpec.LOAD_SPEC_FROM_ACTIVE_INV, 'project_name': project_name})
            ])
            self.widget_content.view_btn(btn_data)
        elif tp == TypeTreeItem.SPEC_FOLDER_BUY:
            btn_data = OrderedDict([
                ('Сформировать на основе спецификации из Inventor', {'type': TypeCreateLoadSpec.CREATE_SPEC_BUY_FROM_SPEC_INV, 'project_name': project_name}),
                ('Создать пустую', {'type': TypeCreateLoadSpec.CERATE_SPEC_BUY_EMPTY, 'project_name': project_name})
            ])
            self.widget_content.view_btn(btn_data)
        elif tp == TypeTreeItem.SPEC_FOLDER_PROD:
            btn_data = OrderedDict([
                ('Сформировать на основе закупочной спецификации', {'type': TypeCreateLoadSpec.CREATE_SPEC_PROD_FROM_SPEC_BUY, 'project_name': project_name}),
                ('Сформировать на основе спецификации из Inventor', {'type': TypeCreateLoadSpec.CREATE_SPEC_PROD_EMPTY, 'project_name': project_name}),
                ('Создать пустую', {'type': TypeCreateLoadSpec.CREATE_SPEC_PROD_EMPTY, 'project_name': project_name})
            ])
            self.widget_content.view_btn(btn_data)
        elif tp == TypeTreeItem.TABLE:
            ...

    def load_content(self, data: dict[str, str]):
        tp = data['type']
        project_name = data['project_name']

        if tp == TypeCreateLoadSpec.LOAD_SPEC_FROM_XLSX:
            self.load_spec_from_xlsx(project_name)
        elif tp == TypeCreateLoadSpec.LOAD_SPEC_FROM_XLSX:
            ...
        elif tp == TypeCreateLoadSpec.LOAD_SPEC_FROM_ACTIVE_INV:
            ...
        elif tp == TypeCreateLoadSpec.CREATE_SPEC_BUY_FROM_SPEC_INV:
            ...
        elif tp == TypeCreateLoadSpec.CERATE_SPEC_BUY_EMPTY:
            ...
        elif tp == TypeCreateLoadSpec.CREATE_SPEC_PROD_FROM_SPEC_BUY:
            ...
        elif tp == TypeCreateLoadSpec.CREATE_SPEC_PROD_FROM_SPEC_INV:
            ...
        elif tp == TypeCreateLoadSpec.CREATE_SPEC_PROD_EMPTY:
            ...

    def create_project(self) -> None:
        ...

    def load_spec_from_xlsx(self, project_name: str) -> None:
        print(project_name)
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getOpenFileName(self, 'Выбрать файл', filter='xlsx файл (*.xlsx)')
        if filename[0]:
            ...

    def open_project(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getOpenFileName(self, 'Выбрать файл', filter='SPEC файл (*.spec)')
        if filename[0]:
            self.path_project = filename[0]
            self.browser.populate_from_db()

    def closeEvent(self, event):
        for db in self.databases.values():
            db.close()

        return super().closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = WindowSpecification()
    
    window.show()
    sys.exit(app.exec_())