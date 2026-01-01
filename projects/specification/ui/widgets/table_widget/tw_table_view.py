from PyQt5 import QtCore, QtGui, QtWidgets


class NoSelectionDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selection_color = QtGui.QColor(128, 128, 128, 35)
        
    def paint(self, painter, option, index):
        alignment = index.data(QtCore.Qt.ItemDataRole.TextAlignmentRole)
        
        option_copy = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(option_copy, index)
        
        option_copy.state &= ~(QtWidgets.QStyle.StateFlag.State_Selected | 
                              QtWidgets.QStyle.StateFlag.State_HasFocus | 
                              QtWidgets.QStyle.StateFlag.State_MouseOver)
        
        if alignment is not None:
            if isinstance(alignment, int):
                alignment = QtCore.Qt.Alignment(alignment)
            option_copy.displayAlignment = alignment
        
        super().paint(painter, option_copy, index)
        
        if option.state & QtWidgets.QStyle.StateFlag.State_Selected:
            painter.save()
            painter.fillRect(option.rect, QtGui.QBrush(self.selection_color))
            painter.restore()
            

class TableView(QtWidgets.QTableView):
    signal_change_zoom = QtCore.pyqtSignal(int)
    signale_change_selection = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)

        self._is_ctrl = False

        self.setWordWrap(False)

        self.setItemDelegate(NoSelectionDelegate(self))
        self.verticalScrollBar().valueChanged.connect(self.resize_rect)
        self.horizontalScrollBar().valueChanged.connect(self.resize_rect)

        self._frame_selection_rect = QtWidgets.QFrame(self)
        self._frame_selection_rect.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self._frame_selection_rect.setStyleSheet('QFrame {background-color: rgba(0, 0, 0, 0); border: 2px solid green}')
        self.grid = QtWidgets.QGridLayout(self._frame_selection_rect)
                
    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        self.resize_rect()
        self.signale_change_selection.emit(self.selectionModel().selection())
    
    def resize_rect(self) -> None:
        ranges = self.selectionModel().selection()
        if ranges and not self._is_ctrl:
            top = min(r.top() for r in ranges)
            left = min(r.left() for r in ranges)
            bottom = max(r.bottom() for r in ranges)
            right = max(r.right() for r in ranges)
            
            self._draw_rect(top, left, bottom, right)
    
    def _draw_rect(self, top: int, left: int, bottom: int, right: int):
        rect_start = self.visualRect(self.model().index(top, left))
        rect_end = self.visualRect(self.model().index(bottom, right))
        
        rect = QtCore.QRect(self.viewport().mapTo(self, rect_start.topLeft()),self.viewport(). mapTo(self, rect_end.bottomRight()) )
        self._frame_selection_rect.setGeometry(rect)
    
    def hide_selection(self) -> None:
        self._frame_selection_rect.hide()

    def set_active_range(self, top: int, left: int, bottom: int, right: int) -> None:
        self._draw_rect(top, left, bottom, right)
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self._is_ctrl = True
                self._frame_selection_rect.hide()
            else:
                self._is_ctrl = False
                self._frame_selection_rect.show()
            return super().mousePressEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self.signal_change_zoom.emit(event.angleDelta().y())
        else:
            return super().wheelEvent(event)