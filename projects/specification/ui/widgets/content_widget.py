from typing import Callable, Union
from PyQt5 import QtCore, QtWidgets, QtGui
from dataclasses import dataclass
from transliterate import translit

from projects.specification.config.settings import *
from projects.specification.config.enums import TypeTreeItem, EnumStatusBar
from projects.specification.config.constants import *
from projects.specification.core.data_tables import ColumnConfig, PROPERTY_PROJECT_CONFIG
from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx

from projects.specification.ui.single_bus import signal_bus

from projects.specification.ui.widgets.table_widget import WidgetTable
from projects.specification.ui.widgets.browser_widget import ProjectItem, SpecificationItemTree, TableItem, BrowserWidget 

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button, decorater_set_object_name
from projects.tools.functions.warning_qlineedit import WarningQEditLine
from projects.tools.custom_qwidget.message_Inforation import MessageInforation
from projects.tools.custom_qwidget.line_separate import QHLineSeparate
from projects.tools.row_counter import RowCounter


class PageContent(QtWidgets.QWidget):
    """
    Базовый класс страницы для контента
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.current_item: Union[ProjectItem, SpecificationItemTree, TableItem] = None
    
    def populate(self, item: Union[ProjectItem, SpecificationItemTree, TableItem]) -> None:
        self.current_item = item

    def update_data_item(self) -> None:
        ...

    def escape_tab(self) -> None:
        ...

    def save(self) -> None:
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
    signal_status = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.columns_config: list[ColumnConfig] = PROPERTY_PROJECT_CONFIG.columns
        self.current_item: ProjectItem = None
        self.__init_widgets()

    def __init_widgets(self) -> None:
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

        # self.btn_save_property_project = QtWidgets.QPushButton(self)
        # self.btn_save_property_project.setText('Сохранить')
        # self.btn_save_property_project.clicked.connect(self.click_save)
        # self.grid_layout.addWidget(self.btn_save_property_project, row_counter.next(), 0, 1, 4)
    
    def populate(self, item: ProjectItem):
        super().populate(item)
        data = self.current_item.table_data.get_data()
        if not data:
            self.clear()

        if data:            
            self.clear()
            for field, lineedit in self.dict_line_edit.items():
                lineedit.setText(data.get(field))
            if (database := self.current_item.table_data.database):
                self.lineedit_project_filepath.setText(database.filepath)
            self.current_item.__is_save = True

    def update_data_item(self):
        data = self.current_item.table_data.get_data()
        for field, lineedit in self.dict_line_edit.items():
            data[field] = lineedit.text()
        self.current_item.table_data.set_data(data)

    def save(self) -> None:
        if self.check_fill_lineedit():
            self.update_data_item()
            if not self.current_item.is_init:
                dlg = QtWidgets.QFileDialog(self)
                project_name_translit = translit(self.lineedti_project_name.text(), 'ru', reversed=True)
                dir_path, _ = dlg.getSaveFileName(self, 'Выберете папку', project_name_translit, filter=f'{MY_FORMAT.upper()} файл (*.{MY_FORMAT})')
                if dir_path:
                    dir_path = dir_path.replace('/', '\\')
                    self.lineedit_project_filepath.setText(dir_path)
                    self.current_item.set_filepath(dir_path)
                
            self.current_item.set_project_name(self.lineedti_project_name.text())
            self.signal_status.emit(f'{EnumStatusBar.PROJECT_SAVE.value}: {self.current_item.project_name}')

    def check_fill_lineedit(self) -> bool:
        for col in self.columns_config:
            if col.mode_column_name:
                lineedit = self.dict_line_edit[col.field]
                if not lineedit.text():
                    msg = MessageInforation(self, 'Данное поле не может быть пустым')
                    WarningQEditLine(lineedit)
                    msg.exec()
                    return False
        return True

    def change_lineedit(self, text: str) -> None:
        self.current_item.__is_save = False

    def clear(self) -> None:
        for lineeidt in self.dict_line_edit.values():
            lineeidt.setText('')


@dataclass
class SetButtonPage:
    text: str
    command: Callable
    
    
class PageCreateOrOpenProject(PageContent):
    signal_load_specification_from_xlsx = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.current_item: SpecificationItemTree
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
        filepath = dlg.getOpenFileName(self, 'Выбрать файл', filter='xlsx файл (*.xlsx)')
        if filepath[0]:
            signal_bus.load_specification_from_xlsx.emit(filepath[0])
    
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
    signal_status = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setSpacing(0)
        self.v_layout.setContentsMargins(0, 0, 0, 0)

        self.init_widgets()

    def init_widgets(self) -> None:
        self.widget_table = WidgetTable(self)
        self.widget_table.signal_has_change_table.connect(self.change_table)
        self.v_layout.addWidget(self.widget_table)

    def populate(self, item):
        super().populate(item)
        self.widget_table.populate(item.table_data)

    def change_table(self) -> None:
        self.current_item.set_is_init(True)
        self.current_item.set_is_save(False)
    
    def save(self) -> None:
        self.signal_status.emit(f'Таблица {self.current_item.text(0)} сохранена')


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class WidgetContent(QtWidgets.QWidget):
    signal_click_btn = QtCore.pyqtSignal(dict)
    signal_status = QtCore.pyqtSignal(str)
    signal_load_specification_from_xlsx = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.current_item: Union[ProjectItem, SpecificationItemTree, TableItem] = None
        self.prev_item: Union[ProjectItem, SpecificationItemTree, TableItem] = None
        self.prev_page: PageContent = None

        self.init_widgets()

        signal_bus.select_item_browser.connect(self.set_item)

    def init_widgets(self) -> None:
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        
        self.stacket = QtWidgets.QStackedWidget(self)
        self.v_layout.addWidget(self.stacket)

        self.page_empty = PageEmpty(self)
        self.index_page_empty = self.stacket.addWidget(self.page_empty)
        
        self.page_property_projcet = PagePropertyProject(self)
        self.page_property_projcet.signal_status.connect(lambda text: self.signal_status.emit(text))
        
        self.index_page_property_projcet = self.stacket.addWidget(self.page_property_projcet)

        self.page_create_or_open_project = PageCreateOrOpenProject(self, )
        self.page_create_or_open_project.signal_load_specification_from_xlsx.connect(self.signal_load_specification_from_xlsx)
        self.index_page_create_or_open_project = self.stacket.addWidget(self.page_create_or_open_project)

        self.page_table = PageTable(self)
        self.page_table.signal_status.connect(lambda text: self.signal_status.emit(text))
        self.index_page_table = self.stacket.addWidget(self.page_table)

        self.stacket.setCurrentIndex(0)

    def set_item(self, item: ProjectItem | SpecificationItemTree | TableItem) -> None:
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
        elif tp in (TypeTreeItem.TABLE_INV, TypeTreeItem.TABLE_BUY, TypeTreeItem.TABLE_PROD):
            self.page_table.populate(item)
            self.stacket.setCurrentIndex(self.index_page_table)
    
    def view_empty_page(self) -> None:
        self.stacket.setCurrentIndex(self.index_page_empty)

    def save(self) -> None:
        widget: PageContent = self.stacket.currentWidget()
        widget.save()

       