from PyQt5 import QtWidgets, QtCore, QtGui
from typing import Any
from collections import OrderedDict

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)


from projects.specification.config.app_context import DATACLASSES, ENUMS


class TabBase(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

    def get_parameters(self) -> dict[str, Any]:
        return {}


class TabAligment(TabBase):
    """
    Страничка редактиваровния формата выравнвания в ячейки
    """
    def __init__(self, parent):
        super().__init__(parent)


class TabFormatBase(QtWidgets.QWidget):
    """
    Выбор и редактирование текстового общего ячейки
    """

    signal_text_examle = QtCore.pyqtSignal(str)

    def __init__(self, parent, cell: DATACLASSES.DATA_CELL):
        super().__init__(parent)

        self.cell = cell
        self._text_example: str = cell.raw_value
        self._text_description: str = 'Общий числовой формат используется для отображения как текстовых, так и числовых значений произвольного типа.'

        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(5)
        self.grid_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

    def show_text_example(self) -> None:
        self.signal_text_examle.emit(self._text_example)

    def get_text_example(self) -> str:
        return self._text_example

    def get_parameters(self) -> dict[ENUMS.CONSTANTS, int | DATACLASSES.CELL_FORMAT]:
        return {
            ENUMS.CONSTANTS.QROLE_CELL_FORMAT_VALUE: DATACLASSES.CELL_FORMAT.AUTO.value
        }


class TabFormatNumber(TabFormatBase):
    """
    Выбор и редактирование текстового числового ячейки
    """

    def __init__(self, parent, cell: DATACLASSES.DATA_CELL):
        super().__init__(parent, cell)

        self._count_decimals = cell.count_decimals
        self._type_value_example = cell.type_value
        self._text_description: str = 'Числовой формат явялется наиболее общим способом представления чисел. Для ввода денежных значений используется также формам "Денежный" и "Финансовый"'

        self.label = QtWidgets.QLabel(self)
        self.label.setText('Число десятичных занков:')
        self.grid_layout.addWidget(self.label, 0, 0, 1, 1)

        self.spin_number = QtWidgets.QDoubleSpinBox(self)
        self.spin_number.setValue(self._count_decimals)
        self.spin_number.setDecimals(0)
        self.spin_number.setFixedWidth(60)
        self.spin_number.valueChanged.connect(self.change_count_decimals)
        self.grid_layout.addWidget(self.spin_number, 0, 1, 1, 1)

        self.change_count_decimals(self._count_decimals)
        
    def set_count_decimals(self, count):
        self.signal_change_spin_value.emit(int(count))
        self.spin_number.setValue(count)
        return super().set_count_decimals(count)
    
    def change_count_decimals(self, value: float) -> None:
        self._count_decimals = int(value)

        if self._type_value_example == DATACLASSES.TYPE_VALUE_DATA_CELL.NUMBER:
            integer, *fractional = str(self._text_example).split(',')
            fractional = fractional[0] if fractional else '0'
            
            if self._count_decimals:
                len_fractional = len(fractional)
                
                if self._count_decimals > len_fractional:
                    fractional += '0' * (self._count_decimals - len_fractional)
                else:
                    fractional = fractional[0: self._count_decimals]
                text_example = integer + (f',{fractional}' if fractional else '') 
            
            else:
                text_example = self._text_example.split(',')[0]

            self._text_example = text_example
            self.signal_text_examle.emit(text_example)

    def get_parameters(self):
        return {
            ENUMS.CONSTANTS.QROLE_CELL_FORMAT_VALUE: DATACLASSES.CELL_FORMAT.NUMBER.value,
            ENUMS.CONSTANTS.QROLE_CELL_COUNT_DECIMALS: self._count_decimals
        }


class TabFormatText(TabFormatBase):
    """
    Выбор и редактирование текстового формата ячейки
    """
    def __init__(self, parent, cell: DATACLASSES.DATA_CELL):
        super().__init__(parent, cell)

        self._text_description: str = 'Значений в тектовом формате отображаются точно также как вводятся. Они обрабатываются как строки вне зависимости от их содержания'

    def get_parameters(self):
        return {
            ENUMS.CONSTANTS.QROLE_CELL_FORMAT_VALUE: DATACLASSES.CELL_FORMAT.TEXT.value
        }


class TabFormat(TabBase):
    """
    Страничка редактиваровния формата ячейки
    """
    def __init__(self, parent, cell: DATACLASSES.DATA_CELL):
        super().__init__(parent)
        
        self.cell = cell
        self.dict_format: OrderedDict[str, dict[TabFormatBase, DATACLASSES.CELL_FORMAT]] = {}

        self.__init_widget()

    def __init_widget(self) -> None:
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(5)
        
        # ------------------------------ List ----------------------------  
        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.clicked.connect(self.select_list_item)
        self.grid_layout.addWidget(self.list_widget, 0, 0, 2, 1)
        
        self.tab_base_format = TabFormatBase(self, self.cell)
        self.dict_format['Общий'] = {'widget': self.tab_base_format, 'cell_format': DATACLASSES.CELL_FORMAT.AUTO}

        self.tab_number_format = TabFormatNumber(self, self.cell)
        self.dict_format['Числовой'] = {'widget': self.tab_number_format, 'cell_format': DATACLASSES.CELL_FORMAT.NUMBER}

        self.tab_text_format = TabFormatText(self, self.cell)
        self.dict_format['Текстовый'] = {'widget': self.tab_text_format, 'cell_format': DATACLASSES.CELL_FORMAT.TEXT}

        # ------------------------------ QGroupBox ---------------------------- 
        self.group_box = QtWidgets.QGroupBox(self)
        self.group_box.setTitle('Образец')
        self.group_box.setFixedHeight(40)
        self.grid_layout.addWidget(self.group_box, 0, 1, 1, 1)
        
        self.v_layout_group_box = QtWidgets.QVBoxLayout(self.group_box)
        self.v_layout_group_box.setContentsMargins(7, 7, 7, 7)
        self.v_layout_group_box.setSpacing(5)

        self.label_example = QtWidgets.QLabel(self.group_box)
        self.label_example.setWordWrap(True)
        self.label_example.setText(self.cell.raw_value)
        self.v_layout_group_box.addWidget(self.label_example)
        
        # ------------------------------ StackedWidget ---------------------------- 
        self.stacket = QtWidgets.QStackedWidget(self)
        self.grid_layout.addWidget(self.stacket, 1, 1, 1, 1)

        for i, (name, page_param) in enumerate(self.dict_format.items()):
            wiget = page_param['widget']
            cell_format = page_param['cell_format']
            wiget.signal_text_examle.connect(lambda text: self.label_example.setText(text))
            self.list_widget.addItem(name)
            self.stacket.addWidget(wiget)

            if cell_format == self.cell.format_value:
                self.list_widget.setCurrentRow(i)
        
        self.list_widget.setFixedWidth(self.list_widget.sizeHintForColumn(0) + self.list_widget.frameWidth() * 6)
        
        # ------------------------------ Label Description ---------------------------- 
        self.label_description_format = QtWidgets.QLabel(self)
        self.label_description_format.setWordWrap(True)
        self.grid_layout.addWidget(self.label_description_format, 2, 0, 1, 2)

        self.select_list_item()

    def select_list_item(self) -> None:
        item = self.list_widget.currentItem()
        widget = self.dict_format[item.text()]['widget']
        widget.show_text_example()
        
        self.label_description_format.setText(widget._text_description)
        self.label_example.setText(widget.get_text_example())
        self.stacket.setCurrentWidget(widget)
    
    def get_parameters(self) -> dict[str, Any]:
        widget: TabFormatBase = self.stacket.currentWidget()
        return widget.get_parameters()


class PropertyCellTabWiddget(QtWidgets.QTabWidget):
    """
    Многостраничный Tab Виджет для разных параметрво ячейки
    """
    def __init__(self, parent, cell: DATACLASSES.DATA_CELL):
        super().__init__(parent)

        self.dict_tab: dict[str, TabBase] = {
            'Число': TabFormat(self, cell),
            'Выравнивнаие':TabAligment(self)
        }

        for name, tab_widget in self.dict_tab.items():
            self.addTab(tab_widget, name)
        
    def get_parameters(self) -> dict[str, Any]:
        widget: TabBase = self.currentWidget()
        return widget.get_parameters()


class WindowFormatCell(QtWidgets.QDialog):
    """
    Диалоговое окно для выбора форматов ячейки
    """
    def __init__(self, cell: DATACLASSES.DATA_CELL, parent=None):
        super().__init__(parent)

        # self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowTitle('Формат ячеек')
        self.setFixedSize(620, 450)

        self._parameters: dict[str, Any] = {}

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(2, 2, 2, 2)
        self.v_layout.setSpacing(2)

        self.tab_widget = PropertyCellTabWiddget(parent=self, cell=cell)
        self.v_layout.addWidget(self.tab_widget)

        self.btn_box = QtWidgets.QDialogButtonBox(self)
        self.v_layout.addWidget(self.btn_box)

        self.btn_ok = self.btn_box.addButton('ОК', QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        self.btn_ok.clicked.connect(self.click_btn_ok)
        
        self.btn_cancle = self.btn_box.addButton('Отмена', QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        self.btn_cancle.clicked.connect(self.click_btn_reject)

    def get_parameters(self) -> dict[str, Any]:
        return self._parameters

    def click_btn_ok(self) -> None:
        self._parameters = self.tab_widget.get_parameters()
        self.accept()

    def click_btn_reject(self) -> None:
        self.reject()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    cell = DATACLASSES.DATA_CELL(value='123,100', format_value=DATACLASSES.CELL_FORMAT.NUMBER, count_decimals=3)

    window = WindowFormatCell(cell=cell)
    window.show()
    sys.exit(app.exec_())
