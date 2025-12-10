import os
from typing import Any, TypeVar, Callable
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context.app_context import SETTING, SIGNAL_BUS, ENUMS, CONSTANTS

from projects.specification.ui.widgets.table_widget.tw_table import Table
from projects.specification.ui.widgets.table_widget.tw_blocks_control_panel import BlockControlPanel, FontStyleBlock, AlignCellBlock
from projects.tools.custom_qwidget.line_separate import QHLineSeparate, QVLineSeparate


T = TypeVar('T')


class ControlPanelTable(QtWidgets.QFrame):
    def __init__(self, parent, table: Table):
        super().__init__(parent)

        self.table: Table = table

        self.blocks = {
            ENUMS.TYPE_BLOCK_PROPERTY_CONTROL_PANEL.FONT: FontStyleBlock,
            ENUMS.TYPE_BLOCK_PROPERTY_CONTROL_PANEL.ALIGN:  AlignCellBlock
            }
        
        self.setMinimumHeight(25)
        self.init_widgets()
    
    def init_widgets(self) -> None:
        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.addSpacing(2)
        self.h_layout.setContentsMargins(2, 2, 2, 2)
        self.h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.h_layout)

        self.setup_block()
            
    def setup_block(self) -> None:
        for type_block, block in self.blocks.items():
            b: BlockControlPanel = block(self)
            self.h_layout.addWidget(b)
            self.blocks[type_block] = b
            v_line_separate = QVLineSeparate(self)
            self.h_layout.addWidget(v_line_separate)

    def view_property(self, type_block,  prop: T) -> None:
        self.blocks[type_block].view_property(prop)


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


