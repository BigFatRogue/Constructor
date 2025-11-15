from typing import Callable
from PyQt5 import QtCore, QtWidgets, QtGui
from dataclasses import dataclass

from projects.specification.config.settings import *
from projects.specification.config.enums import TypeTreeItem
from projects.specification.config.constants import *
from projects.specification.config.table_config import TableConfigPropertyProject, TableConfigInventor

from projects.specification.ui.widgets.table import Table

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.h_line_separate import QHLineSeparate
from projects.tools.row_counter import RowCounter


class PageContent(QtWidgets.QWidget):
    """
    Базовый класс страницы для контента
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.current_item: QtWidgets.QTreeWidgetItem = None
    
    def populate(self, item: QtWidgets.QTreeWidgetItem) -> None:
        self.current_item = item

    def update_data_item(self) -> None:
        ...

    def escape_tab(self) -> None:
        ...


class PageEmpty(PageContent):
    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.v_layout)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setText('Ничего не выбрано')
        self.v_layout.addWidget(self.label)


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class PagePropertyProject(PageContent):
    def __init__(self, parent):
        super().__init__(parent)

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
            label.setText(f'{config_col.column_name}{config_col.mode_column_name}')
            self.grid_layout.addWidget(label, row_counter.next(), 0, 1, 1)

            lineedit = QtWidgets.QLineEdit(self)
            lineedit.textChanged.connect(self.change_lineedit)
            self.grid_layout.addWidget(lineedit, row_counter.value, 1, 1, 1)
            self.list_line_eidt.append(lineedit)

        self.btn_save_property_project = QtWidgets.QPushButton(self)
        self.btn_save_property_project.setText('Сохранить')
        self.btn_save_property_project.clicked.connect(self.click_save)
        self.grid_layout.addWidget(self.btn_save_property_project, row_counter.next(), 0, 1, 4)
    
    def populate(self, item):
        super().populate(item)

        if not self.current_item.data(0, QROLE_STATUS_TREE_ITEM):
            data = self.current_item.data(0, QROLE_DATA_TREE_ITEM)
            if data:
                for db_columns, value in zip(self.table_config.columns[1:], self.list_line_eidt):
                    value.setText(data[db_columns.field])
        else:
            self.get_data_from_db()

    def update_data_item(self):
        data = self.current_item.data(0, QROLE_DATA_TREE_ITEM)
        for db_columns, value in zip(self.table_config.columns[1:], self.list_line_eidt):
            data[db_columns.field] = value.text()
        self.current_item.setData(0, QROLE_DATA_TREE_ITEM, data)

    def get_data_from_db(self) -> None:
        self.clear()

    def click_save(self) -> None:
        self.update_data_item()
        self.current_item.setData(0, QROLE_STATUS_TREE_ITEM, True)

    def change_lineedit(self, text: str) -> None:
        if self.current_item:
            self.current_item.setData(0, QROLE_STATUS_TREE_ITEM, False)

    def clear(self) -> None:
        for w in self.list_line_eidt:
            w.setText('')
        self.current_item.setData(0, QROLE_STATUS_TREE_ITEM, True)


@dataclass
class SetButtonPage:
    text: str
    command: Callable
    
    
class PageCreateOrOpenProject(PageContent):
    def __init__(self, parent):
        super().__init__(parent)

        self.list_btn: list[QtWidgets.QPushButton] = []
        
        self.dict_buttons: dict[TypeTreeItem, tuple[SetButtonPage, ...]] = {
            TypeTreeItem.SPEC_FOLDER_INV: (
                SetButtonPage('Загрузить файл .xlsx', self.load_spec_from_xlsx),
                SetButtonPage('Получить из активного документа Inventor', self.load_spec_from_active_inv)
            ),
            TypeTreeItem.SPEC_FOLDER_BUY: (
                SetButtonPage('Cформировать на основе спецификации из Inventor', self.create_spec_buy_from_spec_inv),
                SetButtonPage('Создать пустую спецификацию', self.cerate_spec_buy_empty)
            ),
            TypeTreeItem.SPEC_FOLDER_PROD: (
                SetButtonPage('Сформировать на основе закупочной спецификации', self.create_spec_prod_from_spec_buy),
                SetButtonPage('Сформировать на основе спецификации из Inventor', self.create_spec_prod_from_spec_inv),
                SetButtonPage('Создать пустую спецификацию', self.create_spec_prod_empty)
            )
        }

        self.init_widgets()

    def init_widgets(self) -> None:
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(self.v_layout)

    def populate(self, item):
        super().populate(item)

        tp = item.data(0, QROLE_TYPE_TREE_ITEM)
        len_list_btn = len(self.list_btn)
        buttons = self.dict_buttons[tp]

        for i, set_button in enumerate(buttons):
            if i < len_list_btn: 
                btn = self.list_btn[i]
                if not btn.isVisible():
                    btn.show()
            else:
                btn = QtWidgets.QPushButton(self)
                btn.clicked.connect(lambda: ...)
                btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.v_layout.addWidget(btn)
                self.list_btn.append(btn)
            btn.setText(set_button.text)
                        
            btn.clicked.disconnect()
            btn.clicked.connect(set_button.command)
        
        if len(buttons) < len_list_btn:
            for btn in self.list_btn[len(buttons):]:
                btn.hide()

    def load_spec_from_xlsx(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getOpenFileName(self, 'Выбрать файл', filter='xlsx файл (*.xlsx)')
        if filename[0]:
            ...
    def load_spec_from_active_inv(self) -> None:
        ...
    def create_spec_buy_from_spec_inv(self) -> None:
        ...
    def cerate_spec_buy_empty(self) -> None:
        ...
    def create_spec_prod_from_spec_buy(self) -> None:
        ...
    def create_spec_prod_from_spec_inv(self) -> None:
        ...
    def create_spec_prod_empty(self) -> None:
        ...


class PageTable(PageContent):
    def __init__(self, parent):
        super().__init__(parent)
    
    def populate(self, item):
        super().populate(item)


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class WidgetContent(QtWidgets.QWidget):
    signal_click_btn = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.current_item: QtWidgets.QTreeWidgetItem = None
        self.prev_item: QtWidgets.QTreeWidgetItem = None
        self.prev_page: PageContent = None

        self.init_widgets()

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

        self.page_create_or_open_project = PageCreateOrOpenProject(self)
        self.index_page_create_or_open_project = self.stacket.addWidget(self.page_create_or_open_project)

        self.page_table = PageTable(self)
        self.index_table = self.stacket.addWidget(self.page_table)

        self.stacket.setCurrentIndex(0)

    def set_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        self.prev_item = self.current_item
        self.current_item = item

        if self.prev_item != self.current_item:
            current_page: PageContent = self.stacket.currentWidget()
            current_page.update_data_item()

        tp = item.data(0, QROLE_TYPE_TREE_ITEM)

        if tp == TypeTreeItem.PROJET:
            self.page_property_projcet.populate(item)
            self.stacket.setCurrentIndex(self.index_page_property_projcet)
        elif tp in (TypeTreeItem.SPEC_FOLDER_INV, TypeTreeItem.SPEC_FOLDER_BUY, TypeTreeItem.SPEC_FOLDER_PROD):
            self.page_create_or_open_project.populate(item)
            self.stacket.setCurrentIndex(self.index_page_create_or_open_project)
        elif tp == TypeTreeItem.TABLE:
            self.page_table.populate(item)
            self.stacket.setCurrentIndex(self.index_table)
    
    def view_empty_page(self) -> None:
        self.stacket.setCurrentIndex(self.index_page_empty)

    def click_save(self) -> None:
        if self.current_item:
            self.current_item.setData(0, QROLE_STATUS_TREE_ITEM, True)

    def click_btn(self) -> None:
        self.signal_click_btn.emit(self.sender().property('data'))