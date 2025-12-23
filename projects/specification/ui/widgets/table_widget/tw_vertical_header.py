import os
from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.config.app_context.app_context import SIGNAL_BUS

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable
from projects.specification.ui.widgets.table_widget.tw_header import HeaderWithOverlayWidgets



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
    signal_select_row = QtCore.pyqtSignal(tuple)

    def __init__(self, table_view: QtWidgets.QTableWidget, range_zoom):
        super().__init__(QtCore.Qt.Orientation.Vertical, table_view, range_zoom)
        table_view.verticalScrollBar().valueChanged.connect(self._update_widgets)
        self.widgets: list[CheckBoxVerticalHeader
                           ]
        self._start_row: int = None
        self._end_row: int = None
        self.table_model: DataTable = self.table_view.model()

    def set_widget(self, align: int=2):
        self._align_widget = align
        for i in range(self.count()):
            check_box = CheckBoxVerticalHeader(self.table_view)
            check_box.setVisible(True)
            check_box.raise_()
            check_box.index_section = i
            check_box.signal_signle_choose.connect(self.signle_choose)
            check_box.signal_multi_choose.connect(self.signal_multi_choose)
            self.widgets.append(check_box)

            fm = self.fontMetrics()
            text_w = fm.horizontalAdvance(str(i))
            width = check_box.width()
            self.setMinimumWidth(self.sectionSize(i) + text_w + width)
        
        self._update_widgets()

    def fill_row(self, row: int, state: bool) -> None:   
        self.signal_select_row.emit((row, state))
        

    def signle_choose(self, value: tuple[int, bool]) -> None:
        row, state = value
        self._start_row = row
        self.fill_row(row, state)

        if not state:
            self._start_row = None 
            self._end_row = None
        
    def signal_multi_choose(self, value: tuple[int, bool]) -> None:
        row, state = value

        if self._start_row is None:
            self._start_row = row
        else:
            self._end_row = row
        
        if self._end_row is not None:
            if self._start_row > self._end_row:
                self._start_row, self._end_row = self._end_row, self._start_row

            for i in range(self._start_row, self._end_row + 1):
                check_box: CheckBoxVerticalHeader = self.widgets[i]
                if not check_box.checkState() or i == self._end_row or i == self._start_row:
                    check_box.setChecked(True)
                    self.fill_row(i, True)

 



 
