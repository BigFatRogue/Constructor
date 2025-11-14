import sys
from typing import Optional, Union
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
from projects.specification.tables_config import TableConfigInventor
from projects.specification.data_process import load_data_to_db

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.h_line_separate import QHLineSeparate

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


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class WidgetContent(QtWidgets.QWidget):
    signal_click_btn = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.init_widgets()

    def init_widgets(self) -> None:
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        
        self.stacket = QtWidgets.QStackedWidget(self)
        self.v_layout.addWidget(self.stacket)

        # --------------------------- Property project ----------------------------
        self.frame_property_project = QtWidgets.QFrame(self)
        self.stacket.addWidget(self.frame_property_project)

        self.grid_layout_frame_property_project = QtWidgets.QGridLayout(self.frame_property_project)
        self.grid_layout_frame_property_project.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.frame_property_project.setLayout(self.grid_layout_frame_property_project)

        property_project = (
            ('Номер проекта', 'Руководитель проекта'),
            ('Пункт договора', 'Инженер-технолог'),
            ('Адрес объекта', 'Инженер-конструктор'),
            ('Обозначение чертежа', 'Модель установки')
            )

        self.label_project_filepath = QtWidgets.QLabel(self.frame_property_project)
        self.label_project_filepath.setText('Распложение  файла')
        self.grid_layout_frame_property_project.addWidget(self.label_project_filepath, 0, 0, 1, 1)

        self.lineedit_project_filepath = QtWidgets.QLineEdit(self.frame_property_project)
        self.lineedit_project_filepath.setEnabled(False)
        self.grid_layout_frame_property_project.addWidget(self.lineedit_project_filepath, 0, 1, 1, 4)

        h_line_separate = QHLineSeparate(self.frame_property_project)
        self.grid_layout_frame_property_project.addWidget(h_line_separate, 1, 0, 1, 4)

        for y, row in enumerate(property_project, 3):
            for x, value in enumerate(row):
                if x == 1:
                    x += 1
                label = QtWidgets.QLabel(self.frame_property_project)
                label.setText(value)
                self.grid_layout_frame_property_project.addWidget(label, y, x, 1, 1)
                lineedit = QtWidgets.QLineEdit(self.frame_property_project)
                self.grid_layout_frame_property_project.addWidget(lineedit, y, x + 1, 1, 1)

        self.btn_save_property_project = QtWidgets.QPushButton(self.frame_property_project)
        self.btn_save_property_project.setText('Сохранить')
        self.grid_layout_frame_property_project.addWidget(self.btn_save_property_project, 3 + len(property_project), 0, 1, 4)

        # --------------------------- Frame Btn CREATE OR LOAD SPEC ----------------------------
        self.frame_btn = QtWidgets.QFrame(self)
        self.stacket.addWidget(self.frame_btn)

        self.v_layout_frame_btn = QtWidgets.QVBoxLayout(self.frame_btn)
        self.v_layout_frame_btn.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.frame_btn.setLayout(self.v_layout_frame_btn)

        # --------------------------- Table ----------------------------
        self.table = Table(self)
        self.stacket.addWidget(self.table)

        self.stacket.setCurrentIndex(0)

    def view_property_project(self, project_name: str) -> None:
        self.stacket.setCurrentIndex(0)
        print(project_name)

    def view_btn(self, data: OrderedDict[str, dict]) -> None:
        self.stacket.setCurrentIndex(1)
        list_exist_btn: list[QtWidgets.QPushButton] = [child for child in self.frame_btn.children() if isinstance(child, QtWidgets.QPushButton)]
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
        self.stacket.setCurrentIndex(2)

    def fill_table(self, data: list[list[Union[str, float]]]) -> None:
        ...

    def click_btn(self) -> None:
        self.signal_click_btn.emit(self.sender().property('data'))


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class WidgetBrowser(QtWidgets.QWidget):
    signal_select_item = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)

        self.role_type_item = QtCore.Qt.UserRole
        self.role_project_name = QtCore.Qt.UserRole + 1

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
        self.tree.setHeaderLabel('Проекты')
        self.tree.itemChanged.connect(self.change_tree_item)
        self.tree.itemPressed.connect(self.select_tree_item)
        self.grid_layout.addWidget(self.tree, 1, 0, 1, 1)
        self.create_project()

    def create_project(self) -> None:
        project_item = QtWidgets.QTreeWidgetItem()
        project_item.setText(0, 'Новый проект')
        project_item.setData(0, self.role_type_item, TypeTreeItem.PROJET)
        project_item.setData(0, self.role_project_name, project_item.text(0))
        project_item.setFlags(project_item.flags() | QtCore.Qt.ItemIsEditable)
        self.tree.addTopLevelItem(project_item)
        project_item.setExpanded(True)
        
        spec_inv_item = QtWidgets.QTreeWidgetItem()
        spec_inv_item.setText(0, 'Спецификация из Inventor')
        spec_inv_item.setData(0, self.role_type_item, TypeTreeItem.SPEC_FOLDER_INV)
        spec_inv_item.setData(0, self.role_project_name, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'inventor.png'))
        spec_inv_item.setIcon(0, icon)
        project_item.addChild(spec_inv_item)

        spec_buy_item = QtWidgets.QTreeWidgetItem()
        spec_buy_item.setText(0, 'Закупочная спецификация')
        spec_buy_item.setData(0, self.role_type_item, TypeTreeItem.SPEC_FOLDER_BUY)
        spec_buy_item.setData(0, self.role_project_name, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'dollars.png'))
        spec_buy_item.setIcon(0, icon)
        project_item.addChild(spec_buy_item)

        spec_prod_item = QtWidgets.QTreeWidgetItem()
        spec_prod_item.setText(0, 'Сборочная спецификация')
        spec_prod_item.setData(0, self.role_type_item, TypeTreeItem.SPEC_FOLDER_PROD)
        spec_prod_item.setData(0, self.role_project_name, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'iam_image.png'))
        spec_prod_item.setIcon(0, icon)
        project_item.addChild(spec_prod_item)

    def del_project(self) -> None:
        item = self.tree.currentItem()
        if item.data(0, self.role_type_item) == TypeTreeItem.PROJET:
            root = self.tree.invisibleRootItem()
            for item in self.tree.selectedItems():
                (item.parent() or root).removeChild(item)

    def change_tree_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        if item.data(0, self.role_type_item) == TypeTreeItem.PROJET:
            item.setData(0, self.role_project_name, item.text(0))
            self.update_project_name(item, item.text(0))
                
    def update_project_name(self, parent: QtWidgets.QTreeWidgetItem, project_name) -> None:
        count = parent.childCount()
        if count > 0: 
            for i in range(count):
                child = parent.child(i)
                child.setData(0, self.role_project_name, project_name)
                self.update_project_name(child, project_name)
        
    def select_tree_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        data = {
            'type': item.data(0, self.role_type_item),
            'text': item.text(0),
            'project_name': item.data(0, self.role_project_name)
            }

        self.signal_select_item.emit(data)
    

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

        with open(os.path.join(PROJECT_ROOT, r'resources\\spec_style.qss')) as style:
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
    
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.browser)
        splitter.addWidget(self.widget_content)
        splitter.setStretchFactor(1, 1)
        self.grid_layout.addWidget(splitter, 0, 0, 1, 1)

    def select_item(self, data: dict) -> None:
        tp = data['type']

        if tp == TypeTreeItem.PROJET:
            self.widget_content.view_property_project(project_name=data['project_name'])
        elif tp == TypeTreeItem.SPEC_FOLDER_INV:
            btn_data = OrderedDict([
                ('Загрузить файл .xlsx', {'type': TypeCreateLoadSpec.LOAD_SPEC_FROM_XLSX, 'project_name': data['project_name']}),
                ('Получить из активного документа Inventor', {'type': TypeCreateLoadSpec.LOAD_SPEC_FROM_ACTIVE_INV, 'project_name': data['project_name']})
            ])
            self.widget_content.view_btn(btn_data)
        elif tp == TypeTreeItem.SPEC_FOLDER_BUY:
            btn_data = OrderedDict([
                ('Сформировать на основе спецификации из Inventor', {'type': TypeCreateLoadSpec.CREATE_SPEC_BUY_FROM_SPEC_INV, 'project_name': data['project_name']}),
                ('Создать пустую', {'type': TypeCreateLoadSpec.CERATE_SPEC_BUY_EMPTY, 'project_name': data['project_name']})
            ])
            self.widget_content.view_btn(btn_data)
        elif tp == TypeTreeItem.SPEC_FOLDER_PROD:
            btn_data = OrderedDict([
                ('Сформировать на основе закупочной спецификации', {'type': TypeCreateLoadSpec.CREATE_SPEC_PROD_FROM_SPEC_BUY, 'project_name': data['project_name']}),
                ('Сформировать на основе спецификации из Inventor', {'type': TypeCreateLoadSpec.CREATE_SPEC_PROD_EMPTY, 'project_name': data['project_name']}),
                ('Создать пустую', {'type': TypeCreateLoadSpec.CREATE_SPEC_PROD_EMPTY, 'project_name': data['project_name']})
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