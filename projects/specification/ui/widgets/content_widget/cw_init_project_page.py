from PyQt5 import QtCore, QtWidgets, QtGui
from dataclasses import dataclass
from typing import Callable

from projects.specification.config.app_context.app_context import app_context
SETTING = app_context.context_setting
SIGNAL_BUS = app_context.single_bus
ENUMS = app_context.context_enums
CONSTANTS = app_context.constants

from projects.specification.ui.widgets.content_widget.cw_page import PageContent
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationItem 

@dataclass
class SetButtonPage:
    text: str
    command: Callable
    


class PageInitProjectPage(PageContent):
    signal_load_specification_from_xlsx = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.current_item: SpecificationItem
        self.list_btn: list[QtWidgets.QPushButton] = []
        
        self.dict_buttons = {
            ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_INV: (
                SetButtonPage('Загрузить файл .xlsx', self.load_spec_from_xlsx),
                SetButtonPage('Получить из активного документа Inventor', self.load_spec_from_active_inv)
            ),
            ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_BUY: (
                SetButtonPage('Cформировать на основе спецификации из Inventor', self.create_spec_buy_from_spec_inv),
                SetButtonPage('Создать пустую спецификацию', self.cerate_spec_buy_empty)
            ),
            ENUMS.TYPE_TREE_ITEM.SPEC_FOLDER_PROD: (
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
            SIGNAL_BUS.load_specification_from_xlsx.emit(filepath[0])
    
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