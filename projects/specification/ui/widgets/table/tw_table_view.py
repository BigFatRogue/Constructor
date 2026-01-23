from PyQt5 import QtCore, QtGui, QtWidgets
import os
from dataclasses import dataclass
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


class AvgGroupFloatItem:
    def __init__(self, type_value=int):
        self.avg: float = 0
        self.type_value: Type[int] | Type[float] = type_value
        self.values: list[float] = []
        self.count_values: int = 0
        self.last_step: int = None
        self.current_index: int = -1

    def add_value(self, value: float) -> None:
        if self.values:
            self.avg = diff if (diff := value - self.values[-1]) != self.avg else self.avg
        self.values.append(value)
        self.count_values += 1

    def calculate_next_value(self, step: int) -> float:
        if step == 0: return self.values[self.count_values - 1]
        
        direction = step if self.last_step is None else step - self.last_step
        self.last_step = step

        sign = step / abs(step)
        self.values[-1] + self.avg * sign * (self.count_values)
        # if self.current_index <= len(self.values):
        #     # Новое значение уже есть в списке
        #     return self.type_value(self.values[self.current_index + direction])
        # else:
        #     sign = step / abs(step)
        #     next_value = self.values[self.current_index] + self.avg * sign
        #     self.values.append(next_value)
        #     return self.type_value(next_value)


        if direction > 0:
            sign = step / abs(step)
            next_value = self.values[self.current_index] + self.avg * sign
            self.values.append(next_value)
        else:
            if len(self.values) > self.count_values:
                self.values.pop()
        return self.type_value(self.values[-1])


class AvgGroupStringItem:
    def __init__(self):
        self.type_value: Type = str
        self.string_part: str = None
        self.int_parts: list[int] = []
        self.avg: int = 0
        self.values: list[tuple[str, int | None]] = []
        self._cach_value: dict[str, tuple[str, int]] = {}
        self.last_step: int = None

    def add_value(self, value: str) -> None:
        separate_value = self._cach_value.get(value)
        if separate_value is None:
            separate_value = self.separate_int_part(value)
        
        if separate_value[1] is not None and self.values:
            self.avg = diff if (diff := separate_value[1] - self.values[-1][1]) != self.avg else self.avg
        
        self.values.append(separate_value)

        if self.string_part is None:
            self.string_part = separate_value[0]
        self.int_parts.append(separate_value[1])
          
    def separate_int_part(self, value: str) -> tuple[str, int]:
        """
        Отделение от строкового значения цифры в конце строки, если она есть
        """
        if not value or not value[-1].isdigit():
            return (value, None)
        
        list_digit: list[str] = []
        for i, s in enumerate(value[::-1]):
            if s.isdigit():
                list_digit.append(s)
            else:
                break
        digit = int(''.join(list_digit[::-1]))
        
        return (value[0:-i], digit)

    def check_string_part(self, value) -> bool:
        if self.values:
            if type(value) == self.type_value:
                separate_value = self.separate_int_part(value)
                self._cach_value = {value: separate_value}
                if separate_value[0] == self.values[-1][0]:
                    return True
        
        return False

    def calculate_next_value(self, step: int) -> str:
        direction = step if self.last_step is None else step - self.last_step
        self.last_step = step

        # sign = step / abs(step)
        if self.int_parts[-1] is not None:
            next_value_int = int(self.avg + self.int_parts[-1])
            self.int_parts.append(next_value_int)
            return f'{self.string_part}{next_value_int}'
        else:
            return self.string_part


class AutoFillData:
    def __init__(self):
        self.table_model: ModelDataTable = None

        self._rows_data: list[int] = None
        self._columns_data: list[int] = None
        self._current_data: list[list[dict[str, list[DATACLASSES.DATA_CELL] | int]]] = None

        self.current_group: AvgGroupFloatItem | AvgGroupStringItem = None
        self._avg_groups_rows: list[list[AvgGroupFloatItem | AvgGroupStringItem]] = []
        self._avg_groups_columns: list[list[AvgGroupFloatItem | AvgGroupStringItem]] = []

    def set_model(self, table_model) -> None:
        self.table_model = table_model

    def set_current_data(self, start_index: QtCore.QModelIndex, end_index: QtCore.QModelIndex) -> None:
        self._rows_data, self._columns_data = self.table_model.get_visible_coords(top=start_index.row(), left=start_index.column(), 
                                                                                  bottom=end_index.row(), rigth=end_index.column())
        self._current_data = [[{'cell': self.table_model._data[row][column], 'row_group': None, 'column_group': None} for column in self._columns_data] for row in self._rows_data]

        self._avg_groups_rows = self._set_group_row_or_columns_value_2(self._rows_data, self._columns_data)
        self._avg_groups_columns = self._set_group_row_or_columns_value_2(self._columns_data, self._rows_data)

    def _try_str2float(self, value: str | int | float | None) -> tuple[Type[int] | Type[float], int | float] | None:
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
        return

    def _set_group_row_or_columns_value_2(self, line_1: list[int], line_2: list[int]) -> list[list[AvgGroupFloatItem | AvgGroupStringItem]]:
        groups: list[list[AvgGroupFloatItem | AvgGroupStringItem]] = []
        is_swap = line_1 == self._rows_data
        key_type_group = 'row_group' if is_swap else 'column_group'
        
        for j, index_1 in enumerate(line_1):
            line_group: list[AvgGroupFloatItem | AvgGroupStringItem] = []
            self.current_group: AvgGroupFloatItem | AvgGroupStringItem = None
            for i, index_2 in enumerate(line_2):
                row, column = (index_1, index_2) if is_swap else (index_2, index_1)
                y, x = (j, i) if is_swap else (i, j)
                
                value = self.table_model._data[row][column].value
                
                if (number_value := self._try_str2float(value)):
                    type_value, value = number_value
                    if self.current_group is None or not isinstance(self.current_group, AvgGroupFloatItem):
                        self.current_group = AvgGroupFloatItem(type_value)
                        line_group.append(self.current_group)
                        self.current_group.add_value(value)
                    else:
                        self.current_group.add_value(value)
                    
                else:
                    if self.current_group is None \
                        or not isinstance(self.current_group, AvgGroupStringItem) \
                        or not self.current_group.check_string_part(value):
                        
                        self.current_group = AvgGroupStringItem()
                        line_group.append(self.current_group)
                        self.current_group.add_value(value)
                    else:                      
                        self.current_group.add_value(value)
                
                self._current_data[y][x][key_type_group] = len(line_group)  - 1
            groups.append(line_group)
        return groups                          
    
    def calculate_next_value(self, step: int) -> list[str | float]:
        result = []
        count_current_rows = len(self._current_data)

        if step < 0 and step + count_current_rows <= 0:
            next_row = abs(step + count_current_rows) % count_current_rows
        else:
            next_row = (abs(step) - 1) % count_current_rows
        rows = self._current_data[next_row]
        
        for number_column, cell in enumerate(rows):
            group: AvgGroupFloatItem | AvgGroupStringItem = self._avg_groups_columns[number_column][cell['column_group']]
            next_value = group.calculate_next_value(step)
            print(next_value)

    def _calculate_next_value_columns(self, step: int) -> list[str | float]:
        # TODO записывать сразу в массив, так как шаг не корректно работает, когда несколько групп
        
        result = []
        len_current_row = len(self._current_data)
        len_current_column = len(self._current_data[0])
        columns = [[self._current_data[y][x] for y in range(len_current_row)] for x in range(len_current_column)]
        
        number_column = (abs(step) - 1) % len_current_row
        if 0 <= number_column < len_current_row:
            for real_number_column, column in zip(self.columns, columns):
                cell = column[number_column]
                avg_data = self._avg_groups_columns[real_number_column][cell['column_group']]

                
                if not isinstance(avg_data['data'][-1], tuple):
                    next_value = avg_data['data'][-1] + avg_data['avg'] * step
                    result.append(avg_data['type'](next_value))
                else:
                    last_value = avg_data['data'][-1][-1]
                    if last_value is not None:
                        next_value = avg_data['data'][-1][0] + str(avg_data['data'][-1][-1] + avg_data['avg'][-1] * step)
                    else:
                        next_value = avg_data['data'][-1][0]
                    result.append(next_value)

        return result

    def clear(self) -> None:
        self._current_data = None
        self._rows_data = None
        self._columns_data = None


class HandleSelectionTable(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QTableView):
        super().__init__(parent)
        self.table_view = parent
        self._is_press_lbm: bool = False
        
        self._curent_select_index: QtCore.QModelIndex = None
        self._current_start_index: QtCore.QModelIndex | None = None
        self._current_end_index: QtCore.QModelIndex | None = None

        self.auto_fill_data = AutoFillData()

        self.setObjectName("HandleSelectionTable")
        self.setStyleSheet("#HandleSelectionTable {background-color: rgb(0, 128, 0)}")
        self.setFixedSize(7, 7)
        self.setMouseTracking(True)
        self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
        
        self.label_next_value = QtWidgets.QLabel(parent) 
        self.label_next_value.setObjectName("label_next_value")
        self.label_next_value.setStyleSheet("#label_next_value {background-color: white; border: 1px solid rgb(180, 180, 180)}")
        self.label_next_value.hide()

    def set_model(self, table_model) -> None:
        self.auto_fill_data.set_model(table_model)

    def draw(self, rect_selection: QtCore.QRect) -> None:
        self.move(QtCore.QPoint(rect_selection.right() - self.width(), rect_selection.bottom() - self.height()))
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._is_press_lbm = True
            selection = self.table_view.selectionModel().selection()
            if selection.count() == 1:
                first_range = selection.takeFirst()
                self._current_start_index = self.table_view.model().index(first_range.top(), first_range.left())
                self._current_end_index = self.table_view.model().index(first_range.bottom(), first_range.right())
                self.auto_fill_data.set_current_data(start_index=self._current_start_index, end_index=self._current_end_index)
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._is_press_lbm = False
            self._curent_select_index = None
            self._current_start_index = None
            self._current_end_index = None
            self.label_next_value.hide()
            self.auto_fill_data.clear()
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
                    self._set_selection(event.globalPos(), index)
            
                event.accept()
                return
        return super().mouseMoveEvent(event)
    
    def _set_selection(self, pos: QtCore.QPoint, index: QtCore.QModelIndex) -> None:
        row_number, column_number = index.row(), index.column()

        diff_row = row_number - self._current_end_index.row()
        diff_column = column_number - self._current_end_index.column()
        count_rows_current_selection = abs(self._current_end_index.row() - self._current_start_index.row())
        count_columns_current_selection = abs(self._current_end_index.column() - self._current_start_index.column())
        next_value = ''

        if abs(diff_row) >= abs(diff_column):
            if diff_row >= 0 or (diff_row < 0 and abs(diff_row) < count_rows_current_selection):
                end_index = self.table_view.model().index(row_number, self._current_end_index.column())
                selection = QtCore.QItemSelection(self._current_start_index, end_index)
                pos_label_next_value = self.table_view.viewport().mapToParent(self.table_view.visualRect(end_index).bottomRight())
            elif diff_row < 0 and abs(diff_row) > count_rows_current_selection - 1:
                start_index = self.table_view.model().index(self._current_end_index.row(), self._current_start_index.column())
                end_index = self.table_view.model().index(row_number, self._current_end_index.column())
                selection = QtCore.QItemSelection(start_index, end_index)
                pos_label_next_value = self.table_view.viewport().mapToParent(self.table_view.visualRect(end_index).topRight())
            
            self.auto_fill_data.calculate_next_value(diff_row)
        
        else:
            if diff_column > 0 or (diff_column < 0 and abs(diff_column) < count_columns_current_selection):
                end_index = self.table_view.model().index(self._current_end_index.row(), column_number)
                selection = QtCore.QItemSelection(self._current_start_index, end_index)
                pos_label_next_value = self.table_view.viewport().mapToParent(self.table_view.visualRect(end_index).bottomRight())
            elif diff_column < 0 and abs(diff_column) > count_columns_current_selection - 1:
                start_index = self.table_view.model().index(self._current_start_index.row(), self._current_end_index.column())
                end_index = self.table_view.model().index(self._current_end_index.row(), column_number)
                selection = QtCore.QItemSelection(start_index, end_index)
                pos_label_next_value = self.table_view.viewport().mapToParent(self.table_view.visualRect(end_index).bottomLeft())
        
        self.table_view.selectionModel().select(selection, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect)
        
        if next_value:
            self.label_next_value.setText(str(next_value[0]))
            self.label_next_value.setFixedSize(self.label_next_value.sizeHint())
            self.label_next_value.show()
            self.label_next_value.move(pos_label_next_value.x(), pos_label_next_value.y())

    
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
            title='Удалить строку',
            triggerd=self._delete_rows)
        
        create_action(menu=self.context_menu ,
            title='Вставить строку выше',
            triggerd=self._insert_row_up)
        
        create_action(menu=self.context_menu ,
            title='Вставить строку ниже',
            triggerd=self._insert_row_down)

    def setModel(self, model):
        self._handle_rect.set_model(model)
        return super().setModel(model)

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

    def _delete_rows(self) -> None:
        model: ModelDataTable = self.model()

        selection = self.selectionModel().selection()
        set_row: set[int] = set()
        if not selection.isEmpty():
            for rng in self.selectionModel().selection():
                rng: QtCore.QItemSelectionRange
                for row in range(rng.top(), rng.bottom() + 1):
                    set_row.add(row)
        
        if self._active_select_row.row() not in set_row:
            set_row = {self._active_select_row.row()}

        model.delete_rows(rows=set_row)

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