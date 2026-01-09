from PyQt5 import QtCore, QtGui, QtWidgets

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context import DECORATE
from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable
from projects.specification.ui.widgets.table.tw_clipboard import CLIPBOARD 


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
        

class SelectionTable(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QTableView):
        super().__init__(parent)

        self.table_view = parent
        self.start_index: QtCore.QModelIndex = None
        self.end_index: QtCore.QModelIndex = None

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        self.is_activate_copy: bool = False
        self.is_multi_selection: bool = False

        self.color_fill = QtGui.QColor(128, 128, 128, 35)
        self.color_border = QtGui.QColor(0, 128, 0)
        self.color_outline = QtGui.QColor(QtCore.Qt.GlobalColor.white)

        self.dash_offset = 0

        self.animation = QtCore.QVariantAnimation()
        self.animation.setStartValue(0)
        self.animation.setEndValue(40) 
        self.animation.setDuration(2000)
        self.animation.setLoopCount(-1)
        self.animation.valueChanged.connect(self.set_dash_offset)
        self.animation.start()

    def set_indexes(self, start_index: QtCore.QModelIndex, end_index: QtCore.QModelIndex) -> None:
        self.start_index: QtCore.QModelIndex = start_index
        self.end_index: QtCore.QModelIndex = end_index

    def draw(self) -> None:
        rect_start = self.table_view.visualRect(self.start_index)
        rect_end = self.table_view.visualRect(self.end_index)
        
        rect = QtCore.QRect(self.table_view.viewport().mapTo(self.table_view, rect_start.topLeft()),self.table_view.viewport().mapTo(self.table_view, rect_end.bottomRight()))
        self.setGeometry(rect)

    def set_dash_offset(self, offset):
        self.dash_offset = offset
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        rect = self.rect()
        
        if not self.is_multi_selection:
            painter.fillRect(rect, self.color_fill)

            pen = QtGui.QPen(self.color_outline)
            pen.setWidth(1)
            painter.setPen(pen)
            rect_outline = rect.adjusted(2, 2, -2, -2)
            painter.drawRect(rect_outline)

            pen = QtGui.QPen(self.color_border)
            pen.setWidth(3)
            painter.setPen(pen)

            rect = rect.adjusted(0, 0, -1, -1)
            painter.drawRect(rect)
        
        if self.is_activate_copy:
            pen = QtGui.QPen(self.color_outline)
            pen.setWidth(3)
            painter.setPen(pen)
            rect_under_copy = self.rect().adjusted(0, 0, -1, -1)
            painter.fillRect(rect_under_copy, self.color_fill)
            painter.drawRect(rect_under_copy)

            pen = QtGui.QPen(self.color_border)
            pen.setWidth(3)
            pen.setDashPattern([2, 2])
            pen.setDashOffset(self.dash_offset)
            painter.setPen(pen)
            painter.drawRect(rect)


@DECORATE.UNDO_REDO_FOCUSABLE       
class TableView(QtWidgets.QTableView):
    signal_change_zoom = QtCore.pyqtSignal(int)
    signale_change_selection = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('TableSpecification')
        self._is_ctrl = False

        self.setWordWrap(False)

        self.setItemDelegate(NoSelectionDelegate(self))
        self.verticalScrollBar().valueChanged.connect(self.resize_rect)
        self.horizontalScrollBar().valueChanged.connect(self.resize_rect)

        self._selection_rect = SelectionTable(self)
        self._selection_rects: list[SelectionTable] = []
                
    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        self.resize_rect()
        self.signale_change_selection.emit(self.selectionModel().selection())
    
    def resize_rect(self) -> None:
        ranges = self.selectionModel().selection()
        if ranges:
            top = min(r.top() for r in ranges)
            left = min(r.left() for r in ranges)
            bottom = max(r.bottom() for r in ranges)
            right = max(r.right() for r in ranges)
            
            start_index = self.model().index(top, left)
            end_index = self.model().index(bottom, right)
            self._selection_rect.set_indexes(start_index, end_index)
            self._selection_rect.draw()

            for section_rect in self._selection_rects:
                section_rect.draw()
        
    def set_selection(self, top: int, left: int, bottom: int, right: int) -> None:
        """
        Установить выделение ячеек
        
        :param top: столбец верхней левой ячейки
        :type top: int
        :param left: строка верхней левой ячейки
        :type left: int
        :param bottom: столбец нижней правой ячейки
        :type bottom: int
        :param right: строка нижней правой ячейки
        :type right: int
        """
        selection = QtCore.QItemSelection(self.model().index(top, left), self.model().index(bottom, right))
        self.selectionModel().select(selection, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
        self.resize_rect()
    
    def _show_selection_copy(self) -> None:
        self._delete_selection_copy()
        for rng in self.selectionModel().selection():
            rng: QtCore.QItemSelectionRange
            start_index = self.model().index(rng.top(), rng.left())
            end_index = self.model().index(rng.bottom(), rng.right())

            selection_rect = SelectionTable(self)
            selection_rect.is_activate_copy = True
            selection_rect.set_indexes(start_index, end_index)
            selection_rect.draw()
            selection_rect.show()
            self._selection_rects.append(selection_rect)   

    def _delete_selection_copy(self) -> None:
        for selection_rect in self._selection_rects:
            selection_rect.deleteLater()
        self._selection_rects.clear()
        self.viewport().update()

    def _merge_selection_if_rect(self):
        model = self.model()
        sm = self.selectionModel()
        selection = sm.selection()

        if selection.isEmpty():
            return

        rows = []
        cols = []

        for index in selection.indexes():
            rows.append(index.row())
            cols.append(index.column())

        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                if not sm.isSelected(model.index(r, c)):
                    return

        new_selection = QtCore.QItemSelection()
        new_selection.append(
            QtCore.QItemSelectionRange(
                model.index(min_row, min_col),
                model.index(max_row, max_col)
            )
        )

        sm.select(new_selection, QtCore.QItemSelectionModel.ClearAndSelect)

    def _check_copy(self) -> bool:
        selection = self.selectionModel().selection()
        
        if selection.isEmpty():
            return False

        if selection.count() == 1:
            return True
        
        w = {(rng.bottom(), rng.top()) for rng in selection}
        h = {(rng.right(), rng.left()) for rng in selection}

        if len(w) > 1 and len(h) > 1:
            return False
        
        return True
    
    def undo(self) -> None:
        model: ModelDataTable = self.model()
        model.undo_redo.undo()
    
    def redo(self) -> None:
        model: ModelDataTable = self.model()
        model.undo_redo.redo()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                self._is_ctrl = True
                self._selection_rect.is_multi_selection = True
            else:
                self._selection_rect.is_multi_selection = False
                self._is_ctrl = False
                self.viewport().update()
            return super().mousePressEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        model: ModelDataTable = self.model()
        
        if event.key() == QtCore.Qt.Key.Key_Delete:
            model.delete_value_in_range(self.selectionModel().selection())
        
        elif event.key() == QtCore.Qt.Key.Key_C and event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            self._merge_selection_if_rect()
            if self._check_copy():
                self._show_selection_copy()
                CLIPBOARD.copy(model, self.selectionModel().selection())
            event.accept()
        
        elif event.key() == QtCore.Qt.Key.Key_V and event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            CLIPBOARD.paste(model, row=self.currentIndex().row(), column=self.currentIndex().column())
            self._delete_selection_copy()
            event.accept()
        
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self._delete_selection_copy()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            self.signal_change_zoom.emit(event.angleDelta().y())
        else:
            return super().wheelEvent(event)
    

class _Model(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        super().__init__(parent)
        self._data = [['' for __ in range(15)] for _ in range(200)]

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._data[0])
    
    def data(self, index, role = QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return
        
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]


class _Window(QtWidgets.QMainWindow):
    """
    Для тестов без запуска основго приложения

    + тест таблицы в отедльном окне 
    """
    def __init__(self):
        super().__init__()
        self.resize(1500, 750)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.v_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)

        table = TableView(self)
        self.v_layout.addWidget(table)

        model = _Model(self)
        table.setModel(model)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = _Window()
    window.show()
    sys.exit(app.exec_())