from PyQt5 import QtCore, QtGui, QtWidgets
import os
from typing import Type

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context import DECORATE, DATACLASSES
from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable
from projects.specification.ui.widgets.table.tw_clipboard import CLIPBOARD, TypeItemClipboard 

from projects.tools.functions.create_action_menu import create_action


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


        self._init_animation_copy()

    def _init_animation_copy(self) -> None:
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

    def draw(self) -> QtCore.QRect:
        rect_start = self.table_view.visualRect(self.start_index)
        rect_end = self.table_view.visualRect(self.end_index)
        
        rect = QtCore.QRect(self.table_view.viewport().mapTo(self.table_view, rect_start.topLeft()),self.table_view.viewport().mapTo(self.table_view, rect_end.bottomRight()))
        self.setGeometry(rect)

        return rect

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


class HandleSelectionTable(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QTableView):
        super().__init__(parent)
        self.table_view = parent
        self._is_press_lbm: bool = False

        self._curent_select_index: QtCore.QModelIndex = None
        self._current_start_index: QtCore.QModelIndex | None = None
        self._current_end_index: QtCore.QModelIndex | None = None
        self._current_data: list[list[DATACLASSES.DATA_CELL]] = None
        self._avg_value_rows: list[tuple[Type, float | str]] = []
        self._avg_value_columns: list[tuple[Type, float | tuple[str | int]]] = []

        self.rows: list[int] = None
        self.columns: list[int] = None
        self.list_next: list[str | int | float] = []
        
        self.setObjectName("HandleSelectionTable")
        self.setStyleSheet("#HandleSelectionTable {background-color: rgb(0, 128, 0)}")
        self.setFixedSize(7, 7)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)

    def draw(self, rect_selection: QtCore.QRect) -> None:
        self.move(QtCore.QPoint(rect_selection.right() - self.width(), rect_selection.bottom() - self.height()))
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._is_press_lbm = True
            first_range = self.table_view.selectionModel().selection().takeFirst()
            self._current_start_index = self.table_view.model().index(first_range.top(), first_range.left())
            self._current_end_index = self.table_view.model().index(first_range.bottom(), first_range.right())
            self.calculate_avg_value()
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._is_press_lbm = False
            self._curent_select_index = None
            self._current_start_index = None
            self._current_end_index = None
            self._current_data = None
            self.rows = None
            self.columns = None
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._is_press_lbm:
            viewport = self.table_view.viewport()
            pos = viewport.mapFromGlobal(event.globalPos())
            index = self.table_view.indexAt(pos)
            
            if index.isValid(): 
                if self._curent_select_index is None:
                    self._curent_select_index = index
                    return

                if index != self._curent_select_index:
                    self._curent_select_index = index
                    self._set_selection(index)
            
                event.accept()
                return
        return super().mouseMoveEvent(event)
    
    def calculate_avg_value(self) -> None:
        model: ModelDataTable = self.table_view.model()
        self.rows, self.columns = model.get_visible_coords(top=self._current_start_index.row(), left=self._current_start_index.column(), 
                                                 bottom=self._current_end_index.row(), rigth=self._current_end_index.column ())
        self._current_data = [[model._data[row][column] for column in self.columns] for row in self.rows]
        
        row_groups = self._set_group_row_or_columns_value(self.rows, self.columns)
        columns_groups = self._set_group_row_or_columns_value(self.columns, self.rows)
        print(f'{row_groups=}')
        print(f'{columns_groups=}')

    def _set_group_row_or_columns_value(self, line_1: list[int], line_2: list[int]) -> dict[int, dict[(tuple[int, type], float | tuple[str, int])]]:
        model: ModelDataTable = self.table_view.model()
        groups: dict[int, dict[(tuple[int, type], float | tuple[str, int])]] = {}
        is_swap = line_1 != self.rows
        
        for index_1 in line_1:
            group: dict[int, list[int | str | float]] = {}
            current_group: int = 0
            for i, index_2 in enumerate(line_2):
                index_1, index_2 = (index_1, index_2) if is_swap else (index_2, index_1)
                
                value = model._data[index_1][index_2].value
                
                type_value, value = self._preprocess_value(value)
                type_value = str if type_value == tuple else type_value

                if not group:
                    group[(type_value, current_group)] = [value]
                    continue

                if (type_value, current_group) in group:
                    if type_value in (float, int):
                        group[(type_value, current_group)].append(value)
                    elif type_value == str:
                        last_value_group = group[(type_value, current_group)][-1]
                        if value[0] == last_value_group[0]:
                            group[(type_value, current_group)].append(value)
                        else:
                            current_group = i
                            group[(type_value, current_group)] = [value]
                else:
                    current_group = i
                    group[(type_value, current_group)] = [value]
            
            groups[index_1] = group
        
        return groups

    def _set_selection(self, index: QtCore.QModelIndex) -> None:
        row_index, column_index = index.row(), index.column()
        self._current_start_index = self.table_view.model().index(self._current_start_index.row(), self._current_start_index.column())

        if abs(row_index - self._current_end_index.row()) > abs(column_index - self._current_end_index.column()):
            end_index = self.table_view.model().index(row_index, self._current_end_index.column())
            selection = QtCore.QItemSelection(self._current_start_index, end_index)
            self.table_view.selectionModel().select(selection, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
            # -1 так как нужно расчитать среднее для выделенного диапазона, а index относится уже к выделенной ячейки 
            # self.auto_fill_value(self._current_start_index.row(), self._current_start_index.column(), row_index - 1, column_index)
        else:
            end_index = self.table_view.model().index(self._current_end_index.row(), column_index)
            selection = QtCore.QItemSelection(self._current_start_index, end_index)
            self.table_view.selectionModel().select(selection, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
            # -1 так как нужно расчитать среднее для выделенного диапазона, а index относится уже к выделенной ячейки 
            # self.auto_fill_value(self._current_start_index.row(), self._current_start_index.column(), row_index, column_index - 1)
        
    def auto_fill_value(self, top: int, left: int, bottom: int, rigth: int):
        model: ModelDataTable = self.table_view.model()
        
        if self.rows is None or self.columns is None:
            self.rows, self.columns = model.get_visible_coords(top=top, left=left, bottom=bottom, rigth=rigth)

        columns_group: dict[int, dict[(tuple[int, type], float | tuple[str, int])]] = {}
        for row in self.rows:
            column_gorup: dict[int, list[int | str | float]] = {}
            current_group: int = 0
            for i, col in enumerate(self.columns):
                value = model._data[row][col].value
                
                type_value, value = self._preprocess_value(value)
                type_value = str if type_value == tuple else type_value

                if not column_gorup:
                    column_gorup[(type_value, current_group)] = [value]
                    continue

                if (type_value, current_group) in column_gorup:
                    if type_value in (float, int):
                        column_gorup[(type_value, current_group)].append(value)
                    elif type_value == str:
                        last_value_group = column_gorup[(type_value, current_group)][-1]
                        if value[0] == last_value_group[0]:
                            column_gorup[(type_value, current_group)].append(value)
                        else:
                            current_group = i
                            column_gorup[(type_value, current_group)] = [value]
                else:
                    current_group = i
                    column_gorup[(type_value, current_group)] = [value]
            
            columns_group[row] = column_gorup

        avg_columns_group: dict[int, dict[int, float | tuple[str, int]]] = {}
        for number_row, groups in columns_group.items():
            for (tp, number_group), value in groups.items():
                avg_value = []
                if tp in (float, int):
                    avg_value = {(tp, number_group): self.calculate_avg_float(value)}
                elif tp == str:
                    avg_value = {(tp, number_group): self.calculate_avg_str(value)}
                
                if not number_row in avg_columns_group:
                    avg_columns_group[number_row] = [avg_value]
                else:
                    avg_columns_group[number_row].append(avg_value)

        print(avg_columns_group)
    
    def create_list_avg_for_rows_columns(self, line1: list[int], line2: list[int]) -> dict[int, dict[int, float | tuple[str, int]]]:
        
        model: ModelDataTable = self.table_view.model()

        line_group: dict[int, dict[(tuple[int, type], float | tuple[str, int])]] = {}
        for row in line1:
            column_gorup: dict[int, list[int | str | float]] = {}
            current_group: int = 0
            for i, col in enumerate(line2):
                value = model._data[row][col].value
                
                type_value, value = self._preprocess_value(value)
                type_value = str if type_value == tuple else type_value

                if not column_gorup:
                    column_gorup[(type_value, current_group)] = [value]
                    continue

                if (type_value, current_group) in column_gorup:
                    if type_value in (float, int):
                        column_gorup[(type_value, current_group)].append(value)
                    elif type_value == str:
                        last_value_group = column_gorup[(type_value, current_group)][-1]
                        if value[0] == last_value_group[0]:
                            column_gorup[(type_value, current_group)].append(value)
                        else:
                            current_group = i
                            column_gorup[(type_value, current_group)] = [value]
                else:
                    current_group = i
                    column_gorup[(type_value, current_group)] = [value]
            
            line_group[row] = column_gorup

        avg_columns_group: dict[int, dict[int, float | tuple[str, int]]] = {}
        for number_row, groups in line_group.items():
            for (tp, number_group), value in groups.items():
                avg_value = []
                if tp in (float, int):
                    avg_value = {(tp, number_group): self.calculate_avg_float(value)}
                elif tp == str:
                    avg_value = {(tp, number_group): self.calculate_avg_str(value)}
                
                if not number_row in avg_columns_group:
                    avg_columns_group[number_row] = [avg_value]
                else:
                    avg_columns_group[number_row].append(avg_value)

    def _preprocess_value(self, value: str | int | float | None) -> tuple[type, str | float | None]:
        """
        Первоначальня проверка данных и попытка преобразовать значнеие во float
        """
        if isinstance(value, int):
            return int, float(value)
        if isinstance(value, float):
            return float, value
        
        if isinstance(value, str):
            if value.isdigit():
                return int, float(value)
            else:
                value = value.replace(',', '.')
                try:
                    return float, float(value)
                except Exception:
                    ...

            return tuple, self._separating_number_to_str(value)
        
        return (None, value)

    def _separating_number_to_str(self, value: str) -> None | tuple[str, int]:
        """
        Отделение от строкового значения цифры в конце строки, если она есть
        """
        if not value or not value[-1].isdigit():
            return (value, 0)
        
        list_digit: list[str] = []
        for i, s in enumerate(value[::-1]):
            if s.isdigit():
                list_digit.append(s)
            else:
                break
        digit = int(''.join(list_digit[::-1]))
        
        return (value[0:-i], digit)

    def calculate_avg_float(self, values: list[float]) -> float:
        """
        Расчёт СЛЕДУЮЩЕГО значения для списка значений чисел
        """
        len_values = len(values)
        if len_values == 1:
            return values[0]
        
        set_division = {values[i + 1] - values[i] for i in range(len_values - 1)}
        if len(set_division) == 1:
            return values[-1] + set_division.pop()
        else:
            return sum(values) / len(values)

    def calculate_avg_str(self, values: tuple[str, int]) -> str:
        """
        Расчёт СЛЕДУЮЩЕГО значения для списка значений строк
        """
        
        digit_values = [v[1] for v in values]
        avg = self.calculate_avg_float(digit_values)
        
        return (values[0][0], avg)


class ContextMenu(QtWidgets.QMenu):
    def __init__(self, parent):
        super().__init__(parent)
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            action = self.actionAt(event.pos())
            if action and action.menu():
                action.trigger()
                self.hide()
                event.accept()
                return

        return super().mousePressEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key.Key_Return:
            action = self.activeAction()
            if action and action.menu():
                action.trigger()
                self.hide()
                event.accept()
                return
        return super().keyPressEvent(event)


@DECORATE.UNDO_REDO_FOCUSABLE       
class TableView(QtWidgets.QTableView):
    signal_change_zoom = QtCore.pyqtSignal(int)
    signale_change_selection = QtCore.pyqtSignal(object)
    signal_copy_link = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('TableSpecification')
        self._is_ctrl = False
        self._is_edited = True

        self.setWordWrap(False)

        self.setItemDelegate(NoSelectionDelegate(self))
        self.verticalScrollBar().valueChanged.connect(self.resize_rect)
        self.horizontalScrollBar().valueChanged.connect(self.resize_rect)

        self._selection_rect = SelectionTable(self)
        self._selection_rects: list[SelectionTable] = []
        self._handle_rect = HandleSelectionTable(self)

        self.init_contex_menu()

    def init_contex_menu(self) -> None:
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.context_menu = ContextMenu(self)

        # ----------------------- Копирование ----------------------------
        action_copy = create_action(menu=self.context_menu ,
            title='Копировать')
        
        menu_copy = QtWidgets.QMenu(self)
        action_copy.setMenu(menu_copy)
        
        create_action(menu=menu_copy ,
            title='Копировать связи',
            triggerd=self._copy_link)
        
        create_action(menu=menu_copy ,
            title='Копировать значение')
        
        create_action(menu=menu_copy ,
            title='Копировать ячейку(и)')
        
        # ----------------------- Вставка ----------------------------
        action_paste = create_action(menu=self.context_menu,
            title='Вставить',
            triggerd=self._paste)
        
        menu_paste = QtWidgets.QMenu(self)
        action_paste.setMenu(menu_paste)

        create_action(menu=menu_paste ,
            title='Вставить значение')
        
        create_action(menu=menu_paste ,
            title='Вставить ячейку(и)')

        self.context_menu.addSeparator()
        # ----------------------- Работа строк ----------------------------
        create_action(menu=self.context_menu ,
            title='Удалить строку')
        
        create_action(menu=self.context_menu ,
            title='Вставить строку выше',
            triggerd=self._insert_row_up)
        
        create_action(menu=self.context_menu ,
            title='Вставить строку ниже',
            triggerd=self._insert_row_down)

    def show_context_menu(self, position: QtCore.QPoint) -> None:
        if self._is_edited:
            self._active_select_row = self.indexAt(position)
            if self._active_select_row != -1:
                self.context_menu.exec_(self.viewport().mapToGlobal(position))

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
            rect = self._selection_rect.draw()
            self._handle_rect.draw(rect)

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
    
    def _copy_cells(self) -> None:
        CLIPBOARD.copy(self.model(), self.selectionModel().selection())

    def _copy_link(self) -> None:
        CLIPBOARD.copy(self.model(), self.selectionModel().selection(), TypeItemClipboard.LINK)

    def _paste(self) -> None:
        CLIPBOARD.paste(self.model(), row=self.currentIndex().row(), column=self.currentIndex().column())

    def _insert_row_up(self) -> None:
        model: ModelDataTable = self.model()
        model.insert_row(row=self.currentIndex().row() - 1)

    def _insert_row_down(self) -> None:
        model: ModelDataTable = self.model()
        model.insert_row(row=self.currentIndex().row() + 1)

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
                self._copy_cells()
            event.accept()
        
        elif event.key() == QtCore.Qt.Key.Key_V and event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            self._paste()
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
        self._data = [['' for __ in range(15)] for _ in range(10)]


    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._data[0])
    
    def data(self, index, role = QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return
        
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def setData(self, index: QtCore.QModelIndex, value, role=QtCore.Qt.ItemDataRole.EditRole):
        row = index.row()
        column = index.column()
        self._data[row][column] = value
        
        self.dataChanged.emit(index, index, [role])

        return True

    def flags(self, index):
        return QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsEditable


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