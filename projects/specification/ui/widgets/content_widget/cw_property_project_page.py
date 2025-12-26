from PyQt5 import QtCore, QtWidgets
from transliterate import translit

from projects.specification.config.app_context import ENUMS


from projects.specification.ui.widgets.content_widget.cw_page import PageContent
from projects.specification.ui.widgets.browser_widget.bw_project_item import ProjectItem 
from projects.specification.core.data_tables import ColumnConfig, PROPERTY_PROJECT_CONFIG

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.line_separate import QHLineSeparate
from projects.tools.row_counter import RowCounter
from projects.tools.functions.warning_qlineedit import WarningQEditLine
from projects.tools.custom_qwidget.message_Inforation import MessageInforation


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class PagePropertyProject(PageContent):
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
        data = self.current_item.item_data.get_data()
        self.clear()

        for field, lineedit in self.dict_line_edit.items():
            lineedit.setText(data.get(field))
        if (database := self.current_item.item_data.database):
            self.lineedit_project_filepath.setText(database.filepath)
        self.current_item.set_is_save(True)

    def update_data_item(self):
        data = self.current_item.item_data.get_data()
        for field, lineedit in self.dict_line_edit.items():
            data[field] = lineedit.text()
        self.current_item.item_data.set_data(data)

    def save(self) -> None:
        if self.check_fill_lineedit():
            self.update_data_item()
            if not self.current_item.is_init:
                dlg = QtWidgets.QFileDialog(self)
                project_name_translit = translit(self.lineedti_project_name.text(), 'ru', reversed=True)
                dir_path, _ = dlg.getSaveFileName(self, 'Выберете папку', project_name_translit, filter=f'{ENUMS.CONSTANTS.MY_FORMAT.value.upper()} файл (*.{ENUMS.CONSTANTS.MY_FORMAT.value})')
                if dir_path:
                    dir_path = dir_path.replace('/', '\\')
                    self.lineedit_project_filepath.setText(dir_path)
                    self.current_item.set_filepath(dir_path)
                
            self.current_item.set_project_name(self.lineedti_project_name.text())

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
        self.current_item.set_is_save(False)

    def clear(self) -> None:
        for lineeidt in self.dict_line_edit.values():
            lineeidt.setText('')