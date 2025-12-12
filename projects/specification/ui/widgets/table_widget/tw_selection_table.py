
from PyQt5 import QtWidgets, QtCore

from projects.specification.config.app_context.app_context import SIGNAL_BUS

from projects.specification.ui.widgets.table_widget.tw_table_item import TableItem


class SelectionRect(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QTableWidget):
        super().__init__(parent)
        self.table = parent

        self.__set_x = set()
        self.__set_y = set()

        self.__is_set_font = True
        self.style_dict: dict[str, int | float | str] = {}

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet('QFrame {background-color: rgba(0, 0, 0, 0); border: 2px solid green}')
        self.raise_()
        self.resize(200, 200)

        self.frame = QtWidgets.QFrame(self)
        self.grid = QtWidgets.QGridLayout(self.frame)

    def set_selection(self, list_items: list[TableItem]) -> None:
        if list_items:
            self.show()

            for item in list_items:
                self.__accumulate_coords(item)
                if self.__is_set_font:
                    self.__is_set_font = self.__set_style(item)
            self.__resize_rect()
            SIGNAL_BUS.view_style_cell.emit(self.style_dict)

    def __accumulate_coords(self, item: TableItem) -> None:
        """
        Наколпение координат ячеек в множествах
        
        :param item: Ячейка таблицы
        :type item: TableItem
        """
        rect = self.table.visualRect(self.table.indexFromItem(item))
        top_left_in_table = self.table.viewport().mapTo(self.table, rect.topLeft())
        
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
    
    def __set_style(self, item: TableItem) -> bool:
        style_item = item.get_style_dict()
        if not self.style_dict:
            self.style_dict = style_item
        else:
            for (style_name, style_value) in style_item.items():
                if self.style_dict[style_name] != style_value:
                    self.style_dict = {}
                    return False
        return True
