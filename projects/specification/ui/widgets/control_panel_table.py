from typing import Any, TypeVar, Callable
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent)
    sys.path.append(test_path)


from projects.specification.config.settings import *
from projects.specification.config.enums import TypeAlignText, TypeBLockPropertyControlPanel, TypeSignalFromControlPanel
from projects.specification.config.constants import *

from projects.specification.ui.widgets.table import TableWithZoom
from projects.specification.ui.widgets.blocks_control_panel import BlockControlPanel, MainBlock, FontStyleBlock, AlignCellBlock
from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.line_separate import QHLineSeparate, QVLineSeparate


T = TypeVar('T')


# @decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class ControlPanelTable(QtWidgets.QFrame):
    def __init__(self, parent, table: TableWithZoom):
        super().__init__(parent)

        self.table: TableWithZoom = table

        self.blocks: dict[TypeBLockPropertyControlPanel, BlockControlPanel] = {
            TypeBLockPropertyControlPanel.MAIN: MainBlock,
            TypeBLockPropertyControlPanel.FONT: FontStyleBlock,
            TypeBLockPropertyControlPanel.ALIGN:  AlignCellBlock
            }
        
        self.signals: dict[TypeSignalFromControlPanel, QtCore.pyqtSignal] = {}

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

            self.signals.update(b.signals)

    def connect_signal(self, type_signal: TypeSignalFromControlPanel, func: Callable) -> None:
        signal = self.signals.get(type_signal)
        if signal:
            signal.connect(func)

    def view_property(self, type_block: TypeBLockPropertyControlPanel,  prop: T) -> None:
        self.blocks[type_block].view_property(prop)


class __Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        with open(os.path.join(RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', ICO_FOLDER.replace('\\', '/')) 
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


