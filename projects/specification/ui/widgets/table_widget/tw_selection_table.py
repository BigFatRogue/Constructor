
from dataclasses import fields
from PyQt5 import QtWidgets, QtCore

from projects.specification.config.app_context.app_context import DATACLASSES

from projects.specification.ui.widgets.table_widget.tw_table_item import TableItem


class NoSelectionDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        opt = QtWidgets.QStyleOptionViewItem(option)

        if opt.state & QtWidgets.QStyle.State_Selected:
            opt.state &= ~QtWidgets.QStyle.State_Selected

        super().paint(painter, opt, index)


class SelectionRect(QtWidgets.QWidget):
    signal_view_style_cell = QtCore.pyqtSignal(object)

    def __init__(self, parent: QtWidgets.QTableView):
        super().__init__(parent)
        self.table_view = parent
        self.table_modificate()

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet('QFrame {background-color: rgba(0, 0, 0, 0); border: 2px solid green}')
        self.raise_()
        self.resize(200, 200)

        self.frame = QtWidgets.QFrame(self)
        self.grid = QtWidgets.QGridLayout(self.frame)
        
        self.__set_x: set[float] = set()
        self.__set_y: set[float] = set()

        self.__range_style: DATACLASSES.CELL_STYLE = None

        self.hide()

    def table_modificate(self) -> None:
        self.table_view.setItemDelegate(NoSelectionDelegate(self.table_view))
        
        self.table_view.selectionChanged = self.selectionChanged

        self.table_view.horizontalHeader().sectionResized.connect(self.resize_rect)
        self.table_view.horizontalScrollBar().valueChanged.connect(self.resize_rect)

        self.table_view.verticalHeader().sectionClicked.connect(self.resize_rect)
        self.table_view.verticalHeader().sectionEntered.connect(self.resize_rect)

    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
        if not selected.isEmpty():
            self.show()
            for index in self.table_view.selectedIndexes():
                self.__accumulate_coords(index)
            self.__resize_rect()

    def set_selection(self) -> None:
        list_items: list[TableItem] = self.table_view.selectedItems() 
        if list_items:
            self.show()
            
            self.__range_style = list_items[0].get_style()

            for item in list_items:
                self.__accumulate_coords(item)
                # self.__set_style(item)
            self.__resize_rect()
            self.signal_view_style_cell.emit(self.__range_style)

    def resize_rect(self) -> None:
        list_items: list[TableItem] = self.table_view.selectedItems() 
        if list_items:
            self.show()
            
            for item in list_items:
                self.__accumulate_coords(item)
            self.__resize_rect()

    def __accumulate_coords(self, index: QtCore.QModelIndex) -> None:
        """
        Наколпение координат ячеек в множествах
        
        :param item: Ячейка таблицы
        :type item: TableItem
        """
        rect = self.table_view.visualRect(index)
        top_left_in_table = self.table_view.viewport().mapTo(self.table_view, rect.topLeft())
        
        self.__set_x.add(top_left_in_table.x())
        self.__set_x.add(top_left_in_table.x() + rect.width())
        self.__set_y.add(top_left_in_table.y())
        self.__set_y.add(top_left_in_table.y() + rect.height())
    
    def __resize_rect(self) -> None:
        """
        Изменение размеров прямоугольника, чтобы он описывал переданные ячейки
        """
        x0, y0 = min(self.__set_x), min(self.__set_y)
        x1, y1 = max(self.__set_x), max(self.__set_y)
            
        self.setGeometry(x0, y0, abs(x0 - x1), abs(y0 - y1))
        self.frame.resize(abs(x0 - x1), abs(y0 - y1))

        self.__set_x = set()
        self.__set_y = set()
    
    def __set_style(self, item: TableItem) -> None:
        cell_style: DATACLASSES.CELL_STYLE = item.get_style()
        
        if self.__range_style == cell_style:
            return
        
        for cell_field in fields(cell_style):
            value_cell = getattr(cell_style, cell_field.name)
            value_range = getattr(self.__range_style, cell_field.name)

            if value_cell != value_range:
                setattr(self.__range_style, cell_field.name, None)