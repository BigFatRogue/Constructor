import os
from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.config.app_context.app_context import SIGNAL_BUS

from .tw_header import HeaderWithOverlayWidgets


class CheckBoxVerticalHeader(QtWidgets.QCheckBox):
    signal_signle_choose = QtCore.pyqtSignal(tuple)
    signal_multi_choose = QtCore.pyqtSignal(tuple)

    def __init__(self, parent):
        super().__init__(parent)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.index_section: int = 0
        self.is_shift = False
        self.clicked.connect(self.choose_row)

    def choose_row(self) -> None:
        if self.is_shift:
            self.signal_multi_choose.emit((self.index_section, self.checkState()))
        else:
            self.signal_signle_choose.emit((self.index_section, self.checkState()))

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if event.modifiers() & QtCore.Qt.Modifier.SHIFT:
                self.is_shift = True
            else:
                self.is_shift = False
            
        return super().mousePressEvent(event)
    

class VerticallWithOverlayWidgets(HeaderWithOverlayWidgets):
    def __init__(self, table: QtWidgets.QTableWidget):
        super().__init__(QtCore.Qt.Orientation.Vertical, table)
        table.verticalScrollBar().valueChanged.connect(self._update_widgets)

        self.start_row: int = None
        self.end_row: int = None

    def add_widget(self, widget: CheckBoxVerticalHeader):
        super().add_widget(widget)
        widget.signal_signle_choose.connect(self.signle_choose)
        widget.signal_multi_choose.connect(self.signal_multi_choose)
    
    def fill_row(self, row: int, state: bool) -> None:                
        for column in range(self.table.columnCount()):
            item = self.table.item(row, column)
            if item:
                if state:
                    item.setBackground(QtGui.QColor(200, 25, 25))
                else:
                    item.setBackground(QtGui.QColor(255, 255, 255))


    def signle_choose(self, value: tuple[int, bool]) -> None:
        row, state = value
        self.start_row = row
        self.fill_row(row, state)

        if not state:
            self.start_row = None 
            self.end_row = None
        
    def signal_multi_choose(self, value: tuple[int, bool]) -> None:
        print(self.start_row, self.end_row)
        row, state = value

        if self.start_row is None:
            self.start_row = row
        else:
            self.end_row = row
        
        if self.end_row is not None:
            if self.start_row > self.end_row:
                self.start_row, self.end_row = self.end_row, self.start_row

            for i in range(self.start_row, self.end_row + 1):
                check_box: CheckBoxVerticalHeader = self.widgets[i]
                if not check_box.checkState() or i == self.end_row or i == self.start_row:
                    check_box.setChecked(True)
                    self.fill_row(i, True)

 



 
