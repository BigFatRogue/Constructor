import os
from PyQt5 import QtWidgets, QtCore

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context import SETTING, DATACLASSES, ENUMS

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable
from projects.specification.ui.widgets.table_widget.tw_table_view import TableView
from projects.specification.ui.widgets.table_widget.tw_zoom import ZoomTable
from projects.specification.ui.widgets.table_widget.tw_horizontal_header import HorizontalWithOverlayWidgets
from projects.specification.ui.widgets.table_widget.tw_vertical_header import VerticallWithOverlayWidgets
from projects.specification.ui.widgets.table_widget.tw_control_panel import ControlPanelTable

from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem
from projects.specification.ui.widgets.browser_widget.bw_table_inventor_item import TableInventorItem

from projects.specification.core.data_tables import SpecificationDataItem, InventorSpecificationDataItem, BuySpecificationDataItem, ProdSpecificationDataItem


class TableWidget(QtWidgets.QWidget):
    """
    Виджет для отображения данных проекта (свойства проекта, таблицы)
    """

    signal_change_table = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.range_zoom = (10, 400, 5)
        self.current_item: TableBrowserItem = None

        self.v_layout = QtWidgets.QVBoxLayout(self)

        self.table_view = TableView(self)
        self.table_model: DataTable = None
        
        self.horizontal_header = HorizontalWithOverlayWidgets(self.table_view, self.range_zoom)
        self.horizontal_header.sectionResized.connect(self.table_view.resize_rect)      
        self.horizontal_header.sectionResized.connect(self.signal_change_table.emit)  
        self.horizontal_header.signal_change.connect(self.signal_change_table.emit)
        self.table_view.setHorizontalHeader(self.horizontal_header)
        
        self.vertical_header = VerticallWithOverlayWidgets(self.table_view, self.range_zoom)
        self.vertical_header.sectionResized.connect(self.table_view.resize_rect)
        self.vertical_header.sectionResized.connect(self.signal_change_table.emit)  
        self.vertical_header.signal_change.connect(self.signal_change_table.emit)
        self.table_view.setVerticalHeader(self.vertical_header)
        
        self.control_panel = ControlPanelTable(self, self.table_view)
        self.zoom_table = ZoomTable(parent=self, range_zoom=self.range_zoom)
        self.table_view.signal_change_zoom.connect(self._change_zoom)
        self.zoom_table.signal_change_zoom.connect(self._set_zoom)

        self.v_layout.addWidget(self.control_panel)
        self.v_layout.addWidget(self.table_view)
        self.v_layout.addWidget(self.zoom_table)

    def set_item(self, item_tree: TableBrowserItem) -> None:
        """
        Получение элемента дерева из бразуера, для отображения данных из элемента
        
        :param item_tree: элемент дерева браузера
        :type item_tree: TableBrowserItem
        """
        self.current_item = item_tree
        state_init, state_save = item_tree.is_init, item_tree.is_save

        self.table_view.hide_selection()

        self.table_model = item_tree.table_data
        self.zoom_table.set_table_model(self.table_model)
        self.table_view.setModel(self.table_model)
        self.horizontal_header.set_table_model(self.table_model)
        self.vertical_header.set_table_model(self.table_model)
        
        self.table_model.set_range_step_zoom(self.range_zoom)

        if isinstance(item_tree.item_data, InventorSpecificationDataItem):
            self._set_item_invetor()

        self._set_parameters_table()
        
        item_tree.set_is_init(state_init)
        item_tree.set_is_save(state_save)

    def _set_item_invetor(self) -> None:
        """
        Настройка отображения таблицы Inventor
        """
        self.current_item: TableInventorItem

        self.horizontal_header.set_widget()
        self.vertical_header.set_widget()

        self.control_panel.set_table_model(self.table_model)
        self.control_panel.view_all_block(False)
        self.control_panel.view_font_block(True)
        self.control_panel.view_align_block(True)
        
        self.table_view.signale_change_selection.connect(self.control_panel.view_property)

    def _set_zoom(self, step: int) -> None:
        """
        Применить заданное масштабирование
        
        :param step: масштаб в int (20, 30, ...100, 120...)
        :type step: int
        """
        self.horizontal_header.set_zoom(step)
        self.vertical_header.set_zoom(step)
        self.table_view.resize_rect()
        self.zoom_table.set_value(step)

    def _change_zoom(self, derection: int) -> None:
        """
        TableView посылает сигнал от колеса мыши, что нужно поменять зум

        далее zoom_table поерделяет текущий зум и посылает сигнал в self, чтобы уже он отправил всем команду, что происходит масштабирование и с каким значением
        
        :param derection: derection > 0 - увеличение, derection < 0 уменьшение
        :type derection: int
        """
        if derection > 0:
            self.zoom_table.zoom_in()
        else:
            self.zoom_table.zoom_out()
                
    def _set_parameters_table(self) -> None:
        """
        Применить параметры к таблице из item_data
        """
        if self.table_model.item_data.table_data is None:
            self.table_model.item_data.table_data = DATACLASSES.PARAMETER_TABLE(current_zoom=100, active_range=[0, 0, 0, 0])
        else:
            self._set_zoom(self.table_model.item_data.table_data.current_zoom)
      
    
class __Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        with open(os.path.join(SETTING.RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', SETTING.ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        self.resize(750, 750)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.v_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.widgte_table = TableWidget(self)
        self.v_layout.addWidget(self.widgte_table)
        
        filepath = r'D:\Python\AlfaServis\Constructor\projects\specification\DEBUG\ALS.1642.5.3.05.01.00.000 - Инвентор.xlsx'
        data = get_specifitaction_inventor_from_xlsx(filepath)
        data_item = InventorSpecificationDataItem('')
        data_item.set_data(data)
        self.widgte_table.tmp_set_item(data_item)

        # control_panel = self.widgte_table.set_control_panel()
        # control_panel.add_block(FontStyleBlock)
        # control_panel.add_block(AlignCellBlock)
        # self.v_layout.addWidget(self.widgte_table)
        
        # table_data = InventorSpecificationDataItem(DataBase('a'))
        # filepath = r'D:\Python\AlfaServis\Constructor\projects\specification\DEBUG\ALS.1642.5.3.05.01.00.000 - Инвентор.xlsx'
        # table_data.set_data(get_specifitaction_inventor_from_xlsx(filepath))
        # self.widgte_table.populate(table_data)
                


if __name__ == '__main__':
    import sys
    from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx
    app = QtWidgets.QApplication(sys.argv)
    window = __Window()
    
    window.show()
    sys.exit(app.exec_())
