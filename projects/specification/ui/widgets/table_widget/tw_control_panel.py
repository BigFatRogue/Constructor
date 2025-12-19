import os
from dataclasses import fields
from copy import deepcopy
from typing import Any, TypeVar, Callable
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.core.data_tables import SpecificationDataItem
from projects.specification.config.app_context.app_context import SETTING, DATACLASSES

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable
from projects.specification.ui.widgets.table_widget.tw_blocks_control_panel import BlockControlPanel, FontStyleBlock, AlignCellBlock
from projects.tools.custom_qwidget.line_separate import QHLineSeparate, QVLineSeparate


T = TypeVar('T')


class ControlPanelTable(QtWidgets.QFrame):
    def __init__(self, parent, table_view: QtWidgets.QTableView):
        super().__init__(parent)

        self.table_view = table_view
        self.table_model: DataTable = None
        self.blocks: list[BlockControlPanel] = [FontStyleBlock, AlignCellBlock]
        self.blocks_inited: list[BlockControlPanel] = []
        
        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.addSpacing(2)
        self.h_layout.setContentsMargins(2, 2, 2, 2)
        self.h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.h_layout)
        self.setMinimumHeight(25)

    def on_all_block(self):
        if self.table_model:
            for block in self.blocks:
                self.on_block(block)

    def on_block(self, block: BlockControlPanel) -> None:
        if self.table_model:
            block_init: BlockControlPanel = block(self, self.table_model)
            self.blocks_inited.append(block_init)
            self.h_layout.addWidget(block_init)

            v_line_separate = QVLineSeparate(self)
            self.h_layout.addWidget(v_line_separate)

    def set_table_model(self, table_model: DataTable) -> None:
        self.table_model = table_model

    def view_property(self, selection: list[QtCore.QItemSelectionRange]) -> None:
        style_ranges = self.table_model.get_style_selection(selection)
        for block in self.blocks_inited:
            block.view_property(selection, style_ranges)
        
    def on_font_block(self) -> None:
        self.on_block(FontStyleBlock)
    
    def on_align_block(self) -> None:
        self.on_block(AlignCellBlock)
       

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


