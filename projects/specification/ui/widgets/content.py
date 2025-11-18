from typing import Callable, Union
from PyQt5 import QtCore, QtWidgets, QtGui
from dataclasses import dataclass

from projects.specification.config.settings import *
from projects.specification.config.enums import TypeTreeItem
from projects.specification.config.constants import *
from projects.specification.config.table_config import TableConfigPropertyProject, TableConfigInventor, ColumnConfig

from projects.specification.ui.widgets.table import Table
from projects.specification.ui.widgets.browser import BrowserItem, ProjectItem, SpecItem, TableItem

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button, decorater_set_object_name
from projects.tools.functions.alarm_border_qlineedit import alarm_border_qlineedit
from projects.tools.custom_qwidget.message_Inforation import MessageInforation
from projects.tools.custom_qwidget.h_line_separate import QHLineSeparate
from projects.tools.row_counter import RowCounter


class PageContent(QtWidgets.QWidget):
    """
    Базовый класс страницы для контента
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.current_item: Union[ProjectItem, SpecItem, TableItem] = None
    
    def populate(self, item: Union[ProjectItem, SpecItem, TableItem]) -> None:
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
    signal_save_project = QtCore.pyqtSignal(QtWidgets.QTreeWidgetItem)

    def __init__(self, parent):
        super().__init__(parent)

        self.columns_config: list[ColumnConfig] = None
        self.init()

    def init(self) -> None:
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.grid_layout)

    def init_widgets(self) -> None:
        row_counter = RowCounter()

        self.label_project_filepath = QtWidgets.QLabel(self)
        self.label_project_filepath.setText('Распложение  файла')
        self.grid_layout.addWidget(self.label_project_filepath, row_counter.value, 0, 1, 1)

        self.lineedit_project_filepath = QtWidgets.QLineEdit(self)
        self.lineedit_project_filepath.setEnabled(False)
        self.grid_layout.addWidget(self.lineedit_project_filepath, row_counter.value, 1, 1, 2)

        self.col_file_name: ColumnConfig = self.columns_config[1]

        self.label_project_name = QtWidgets.QLabel(self)
        self.label_project_name.setText(f'{self.col_file_name.column_name}{self.col_file_name.mode_column_name}')
        self.grid_layout.addWidget(self.label_project_name, row_counter.next(), 0, 1, 2)

        self.lineedti_project_name = QtWidgets.QLineEdit(self)
        self.lineedti_project_name.setObjectName(f'{self.__class__.__name__}_label_{self.col_file_name.field}')
        self.grid_layout.addWidget(self.lineedti_project_name, row_counter.value, 1, 1, 1)

        h_line_separate = QHLineSeparate(self)
        self.grid_layout.addWidget(h_line_separate, row_counter.next(), 0, 1, 4)
        

        self.dict_line_edit: dict[str, QtWidgets.QLineEdit] = {self.col_file_name.field: self.lineedti_project_name}
        for config_col in self.columns_config[2:]:
            label = QtWidgets.QLabel(self)
            label.setText(f'{config_col.column_name}{config_col.mode_column_name}')
            self.grid_layout.addWidget(label, row_counter.next(), 0, 1, 1)

            lineedit = QtWidgets.QLineEdit(self)
            lineedit.setObjectName(f'{self.__class__.__name__}_label_{config_col.field}')
            
            self.grid_layout.addWidget(lineedit, row_counter.value, 1, 1, 1)
            self.dict_line_edit[config_col.field] = lineedit

        for le in self.dict_line_edit.values():
            le.textChanged.connect(self.change_lineedit)

        self.btn_save_property_project = QtWidgets.QPushButton(self)
        self.btn_save_property_project.setText('Сохранить')
        self.btn_save_property_project.clicked.connect(self.click_save)
        self.grid_layout.addWidget(self.btn_save_property_project, row_counter.next(), 0, 1, 4)
    
    def populate(self, item: ProjectItem):
        super().populate(item)
        if self.columns_config is None:
            self.columns_config = item.table_config.columns
            self.init_widgets()

        data_from_db = False
        if self.current_item.is_save:
            data = self.current_item.select_sql()
            if data:
                self.current_item.set_data(data)
                data_from_db = True
        else:
            data = self.current_item.get_data()
        
        self.clear()
        for field, lineedit in self.dict_line_edit.items():
            lineedit.setText(data.get(field))
        self.lineedit_project_filepath.setText(self.current_item.filepath)
        self.current_item.is_save = data_from_db

    def update_data_item(self):
        data = self.current_item.get_data()
        for field, lineedit in self.dict_line_edit.items():
            data[field] = lineedit.text()
        self.current_item.set_data(data)

    def click_save(self) -> None:
        if self.check_fill_lineedit():
            self.update_data_item()
            if not self.current_item.is_init:
                dlg = QtWidgets.QFileDialog(self)
                dir_path, _ = dlg.getSaveFileName(self, 'Выберете папку', filter='SPEC файл (*.spec)')
                if dir_path:
                    dir_path = dir_path.replace('/', '\\')
                    self.current_item.filepath = dir_path
                    self.lineedit_project_filepath.setText(self.current_item.filepath)
                    self.current_item.set_project_name(self.lineedti_project_name.text())
            self.signal_save_project.emit(self.current_item)

    def check_fill_lineedit(self) -> bool:
        for col in self.columns_config:
            if col.mode_column_name:
                lineedit = self.dict_line_edit[col.field]
                if not lineedit.text():
                    msg = MessageInforation(self, 'Данное поле не может быть пустым')
                    msg.exec()
                    alarm_border_qlineedit(lineedit)
                    return False
        return True

    def change_lineedit(self, text: str) -> None:
        self.current_item.is_save = False

    def clear(self) -> None:
        for lineeidt in self.dict_line_edit.values():
            lineeidt.setText('')


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

        tp = item.type_item
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
        self.current_item: Union[ProjectItem, SpecItem, TableItem] = None
        self.prev_item: Union[ProjectItem, SpecItem, TableItem] = None
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

    def set_item(self, item: Union[ProjectItem, SpecItem, TableItem]) -> None:
        self.prev_item = self.current_item
        self.current_item = item

        if self.prev_item != self.current_item:
            current_page: PageContent = self.stacket.currentWidget()
            current_page.update_data_item()

        tp = item.type_item

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
            if not self.current_item.is_init:
                self.current_item.is_init = True
            self.current_item.is_save = True

    def click_btn(self) -> None:
        self.signal_click_btn.emit(self.sender().property('data'))