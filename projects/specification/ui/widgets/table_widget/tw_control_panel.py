import os
from dataclasses import fields
from copy import deepcopy
from typing import Any, TypeVar, Callable, Type
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent)
    sys.path.append(test_path)


from projects.specification.config.app_context.app_context import SETTING, ENUMS

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable
from projects.specification.ui.widgets.table_widget.tw_blocks_control_panel import BlockControlPanel, FontStyleBlock, AlignCellBlock
from projects.tools.custom_qwidget.line_separate import QHLineSeparate, QVLineSeparate



class ControlPanelTable(QtWidgets.QFrame):
    """
    Панель управления стилями ячеек
    """
    def __init__(self, parent, table_view: QtWidgets.QTableView):
        super().__init__(parent)

        self.table_view = table_view
        self.table_model: DataTable = None
        self.blocks: list[Type[BlockControlPanel]] = [FontStyleBlock, AlignCellBlock]
        self.blocks_inited: dict[str, dict[str, BlockControlPanel | QVLineSeparate | bool]] = {}
        
        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.addSpacing(2)
        self.h_layout.setContentsMargins(2, 2, 2, 2)
        self.h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.h_layout)
        self.setMinimumHeight(25)
    
    def _init_all_block(self):
        """
        Инициализация всех блоков
        """
        if self.table_model and not self.blocks_inited:
            for block in self.blocks:
                block_init: BlockControlPanel = block(self, self.table_model)
                block_init.hide()
                line = QVLineSeparate(self)
                line.hide()
                self.blocks_inited[block_init.type_block] = {'block': block_init, 'line': line, 'status': False}
        self.view_all_block(True)

    def _view_block(self, type_block: ENUMS.TYPE_BLOCK_PROPERTY_CONTROL_PANEL, value: bool) -> None:
        """
        Включить или выключить заданный блок
        
        :param type_block: тип блока
        :type type_block: ENUMS.TYPE_BLOCK_PROPERTY_CONTROL_PANEL
        :param value: True - отобразить, False - скрыть
        """
        if self.blocks_inited:
            data = self.blocks_inited[type_block]
            block = data['block'] 
            line = data['line']
            status = data['status']
            
            if value:
                if not status:
                    block.show()
                    line.show()
                    self.h_layout.addWidget(block)
                    self.h_layout.addWidget(line)
                    data['status'] = True
            else:
                if status:
                    block.hide()
                    line.hide()
                    self.h_layout.removeWidget(block)
                    self.h_layout.removeWidget(line)
                    data['status'] = False

    def view_all_block(self, value: bool) -> None:
        for type_block in self.blocks_inited.keys():
            self._view_block(type_block, value)

    def view_font_block(self, value: bool) -> None:
        self._view_block(ENUMS.TYPE_BLOCK_PROPERTY_CONTROL_PANEL.FONT, value)
    
    def view_align_block(self, value) -> None:
        self._view_block(ENUMS.TYPE_BLOCK_PROPERTY_CONTROL_PANEL.ALIGN, value)
    
    def set_table_model(self, table_model: DataTable) -> None:
        """
        Установка модели данных, в которой будет производится изменения
        
        :param table_model: модель данных
        :type table_model: DataTable
        """
        self.table_model = table_model

        if not self.blocks_inited:
            self._init_all_block()

        for data in self.blocks_inited.values():
            block: BlockControlPanel = data['block']
            block.set_table_model(table_model)

    def view_property(self, selection: list[QtCore.QItemSelectionRange]) -> None:
        style_ranges = self.table_model.get_style_selection(selection)
        if style_ranges:
            for data in self.blocks_inited.values():
                block: BlockControlPanel = data['block']
                block.view_property(selection, style_ranges)
        

class __Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        with open(os.path.join(SETTING.RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', SETTING.ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        # self.resize(750, 250)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.v_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.widget = ControlPanelTable(self)

        self.v_layout.addWidget(self.widget)
        self.v_layout.addWidget(QHLineSeparate(self))
                

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = __Window()
    
    window.show()
    sys.exit(app.exec_())


