from PyQt5 import QtCore, QtGui, QtWidgets

from projects.specification.config.app_context.app_context import DATACLASSES
from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable




class NoSelectionDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_color = QtGui.QColor(128, 128, 128, 35)
        
    def paint(self, painter, option, index):
        alignment = index.data(QtCore.Qt.TextAlignmentRole)
        
        option_copy = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(option_copy, index)
        
        option_copy.state &= ~(QtWidgets.QStyle.State_Selected | 
                              QtWidgets.QStyle.State_HasFocus | 
                              QtWidgets.QStyle.State_MouseOver)
        
        if alignment is not None:
            option_copy.displayAlignment = alignment
        
        super().paint(painter, option_copy, index)
        
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.save()
            painter.fillRect(option.rect, QtGui.QBrush(self.selection_color))
            painter.restore()
            

class TableView(QtWidgets.QTableView):
    signal_change_zoom = QtCore.pyqtSignal(int)
    signale_change_selection = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)

        self.setItemDelegate(NoSelectionDelegate(self))
        self.verticalScrollBar().valueChanged.connect(self.resize_rect)
        self.horizontalScrollBar().valueChanged.connect(self.resize_rect)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.frame.setStyleSheet('QFrame {background-color: rgba(0, 0, 0, 0); border: 2px solid green}')
        self.grid = QtWidgets.QGridLayout(self.frame)
                
    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        self.resize_rect()
        self.signale_change_selection.emit(self.selectionModel().selection())
    
    def resize_rect(self) -> None:
        ranges = self.selectionModel().selection()
        if ranges and len(ranges) == 1:
            self._draw_rect(ranges[0])
    
    def _draw_rect(self, rng):
        rect_start = self.visualRect(self.model().index(rng.top(), rng.left()))
        rect_end = self.visualRect(self.model().index(rng.bottom(), rng.right()))

        top_left = self.viewport().mapTo(self, rect_start.topLeft())
        bottom_right = self.viewport().mapTo(self, rect_end.bottomRight())
            
        x0, y0, x1, y1 = top_left.x(), top_left.y(), bottom_right.x(), bottom_right.y()
        self.frame.setGeometry(x0, y0, abs(x0 - x1), abs(y0 - y1))
        self.frame.resize(abs(x0 - x1), abs(y0 - y1))
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self.frame.hide()
            else:
                self.frame.show()
            return super().mousePressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self.signal_change_zoom.emit(event.angleDelta().y())
        else:
            return super().wheelEvent(event)