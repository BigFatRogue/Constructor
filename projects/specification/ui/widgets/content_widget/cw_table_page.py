
from PyQt5 import QtCore, QtWidgets
import os

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)

    from projects.specification.ui.widgets.browser_widget.browser_widget import BrowserWidget
    from typing import Iterable, Type

from projects.specification.config.app_context import DATACLASSES, SETTING
from projects.specification.ui.widgets.content_widget.cw_page import PageContent

from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable
from projects.specification.ui.widgets.table.tw_table_view import TableView
from projects.specification.ui.widgets.table.tw_zoom import ZoomTable
from projects.specification.ui.widgets.table.tw_hhow import HorizontalWithOverlayWidgets
from projects.specification.ui.widgets.table.tw_hhow_sorted import HorizontalWithOverlayWidgetsSorded
from projects.specification.ui.widgets.table.tw_vhow import VerticallWithOverlayWidgets
from projects.specification.ui.widgets.table.tw_vhow_choose import VerticallWithOverlayWidgetsChoose
from projects.specification.ui.widgets.table.tw_control_panel import ControlPanelTable
from projects.specification.ui.widgets.table.tw_link_row import LinkRow

from projects.specification.ui.widgets.browser_widget.bw_project_item import ProjectItem
from projects.specification.ui.widgets.browser_widget.bw_specefication_item import SpecificationInventorItem
from projects.specification.ui.widgets.browser_widget.bw_table_item import TableBrowserItem
from projects.specification.ui.widgets.browser_widget.bw_table_inventor_item import TableInventorItem
from projects.specification.ui.widgets.browser_widget.bw_table_by_item import TableByItem


from projects.specification.core.data_tables import SpecificationDataItem, InventorSpecificationDataItem, BuySpecificationDataItem, ProdSpecificationDataItem


class PageTable(PageContent):
    signal_status = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.range_zoom = (10, 400, 5)
        self.current_item: TableBrowserItem = None
        self._current_horizontal_headres: HorizontalWithOverlayWidgets | HorizontalWithOverlayWidgetsSorded = None
        self._current_vertical_headres: VerticallWithOverlayWidgets | VerticallWithOverlayWidgetsChoose = None

        self.v_layout = QtWidgets.QVBoxLayout(self)

        self.table_view = TableView(self)
        self.table_model: ModelDataTable = None
        
        self.control_panel = ControlPanelTable(self, self.table_view)
        self.zoom_table = ZoomTable(parent=self, range_zoom=self.range_zoom)
        self.table_view.signal_change_zoom.connect(self._change_zoom)
        self.table_view.signale_change_selection.connect(self._show_link)
        self.zoom_table.signal_change_zoom.connect(self._set_zoom)

        self.widget_link_row = LinkRow(self)
        self.widget_link_row.signal_is_show.connect(self._resize_spliter)
        self.widget_link_row.signal_add_row_link.connect(self._add_link_row)
        self.widget_link_row.signal_del_row_link.connect(self._del_link_row)
        
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.splitter.addWidget(self.table_view)
        self.splitter.addWidget(self.widget_link_row)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStyleSheet("""
        QSplitter::handle {background-color: #d0d0d0}
        QSplitter::handle:pressed {background-color: #4060ff;}""")
        
        self.v_layout.addWidget(self.control_panel)
        self.v_layout.addWidget(self.splitter)
        self.v_layout.addWidget(self.zoom_table)

    def _set_property_header(self, header: HorizontalWithOverlayWidgets | VerticallWithOverlayWidgets) -> None:
        # header.sectionResized.connect(self.table_view.resize_rect)      
        header.sectionResized.connect(self.change_table)  
        header.signal_change.connect(self.change_table)

    def _set_current_header(self, orientation: QtCore.Qt.Orientation, header: HorizontalWithOverlayWidgets | HorizontalWithOverlayWidgetsSorded) -> None:
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if self._current_horizontal_headres:
                self._current_horizontal_headres.deleteLater()
            self._current_horizontal_headres = header
            self.table_view.setHorizontalHeader(header)
        else:
            if self._current_vertical_headres:
                self._current_vertical_headres.deleteLater()
            self._current_vertical_headres = header
            self.table_view.setVerticalHeader(header)
        self._set_property_header(header)
        header.set_table_model(self.table_model)
        header.show()

    def populate(self, item_tree: TableBrowserItem) -> None:
        """
        Получение элемента дерева из бразуера, для отображения данных из элемента
        
        :param item_tree: элемент дерева браузера
        :type item_tree: TableBrowserItem
        """
        if item_tree.item_data.data_link is None:
            self.widget_link_row.hide()
        else:
            self.widget_link_row.show()
            project_item: ProjectItem = item_tree.parent_item.parent_item
            self.widget_link_row.set_table_inventor(project_item.get_inventor_items())                        

        if self._current_horizontal_headres and self._current_vertical_headres:
            self._current_horizontal_headres.update_scroll_x()
            self._current_vertical_headres.update_scroll_y()
        
        if item_tree == self.current_item:
            return
        super().populate(item_tree)
        
        state_init, state_save = item_tree.is_init, item_tree.is_save
        
        self.table_model = item_tree.table_data
        self.table_model.set_range_step_zoom(self.range_zoom)
        self.zoom_table.set_table_model(self.table_model)
        self.table_view.setModel(self.table_model)

        if isinstance(item_tree, TableInventorItem):
            self._set_item_invetor()
        elif isinstance(item_tree, TableByItem):
            self._set_item_by()

        self._set_parameters_table()
        
        item_tree.set_is_init(state_init)
        item_tree.set_is_save(state_save)

    def _set_item_invetor(self) -> None:
        """
        Настройка отображения таблицы Inventor
        """
        self.current_item: TableInventorItem

        horizontal_header_sorted = HorizontalWithOverlayWidgetsSorded(self.table_view, self.range_zoom)
        self._set_current_header(QtCore.Qt.Orientation.Horizontal, horizontal_header_sorted)
        
        vertical_header_choose = VerticallWithOverlayWidgetsChoose(self.table_view, self.range_zoom)
        self._set_current_header(QtCore.Qt.Orientation.Vertical, vertical_header_choose)

        horizontal_header_sorted.set_widget()
        vertical_header_choose.set_widget()

        self.control_panel.set_table_model(self.table_model)
        self.control_panel.show_all_block(False)
        self.control_panel.show_font_block(True)
        self.control_panel.show_align_block(True)
        
        self.table_view.signale_change_selection.connect(self.control_panel.view_property)

    def _set_item_by(self) -> None:
        """
        Настройка отображения таблицы Закупки
        """

        self.current_item: TableByItem

        horizontal_header_sorted = HorizontalWithOverlayWidgetsSorded(self.table_view, self.range_zoom)
        self._set_current_header(QtCore.Qt.Orientation.Horizontal, horizontal_header_sorted)
        
        vertical_header = VerticallWithOverlayWidgets (self.table_view, self.range_zoom)
        self._set_current_header(QtCore.Qt.Orientation.Vertical, vertical_header)

        horizontal_header_sorted.set_widget()
        vertical_header.hide_widget()
        vertical_header.set_table_edited(True)

        self.control_panel.set_table_model(self.table_model)
        self.control_panel.show_all_block(False)
        self.control_panel.show_font_block(True)
        self.control_panel.show_align_block(True)
        
        self.table_model.set_edited(True)
        self.table_view.signale_change_selection.connect(self.control_panel.view_property)

    def _set_zoom(self, step: int) -> None:
        """
        Применить заданное масштабирование
        
        :param step: масштаб в int (20, 30, ...100, 120...)
        :type step: int
        """
        self._current_horizontal_headres.set_zoom(step)
        self._current_horizontal_headres.set_zoom(step)
        self.table_view.resize_rect()
        self.zoom_table.set_value(step)
        self.table_model.set_zoom(step)

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

        if self.table_model.item_data.table_parameter is None:
            self.table_model.item_data.table_parameter = DATACLASSES.PARAMETER_TABLE(current_zoom=100, active_range=[0, 0, 0, 0], scroll_x=0, scroll_y=0)

        self._set_zoom(self.table_model.item_data.table_parameter.current_zoom)

        self.table_view.horizontalScrollBar().setValue(self.table_model.item_data.table_parameter.scroll_x)
        self.table_view.verticalScrollBar().setValue(self.table_model.item_data.table_parameter.scroll_y)
        self.table_view.set_selection(*self.table_model.item_data.table_parameter.active_range)

    def _resize_spliter(self, is_show: bool) -> None:
        if is_show:
            sizes = list(self.splitter.sizes())
            sizes[1] = self.widget_link_row.title.height()
            self.splitter.setSizes(sizes)

    def change_table(self) -> None:
        if self.current_item.is_init:
            self.current_item.set_is_save(False)

    def save(self) -> None:
        self.signal_status.emit(f'Таблица {self.current_item.text(0)} сохранена')

    def _show_link(self, selection: list[QtCore.QItemSelectionRange]) -> None:
        number_row = None
        for rng in selection:
            number_row = rng.top()
            break
        
        if number_row is not None and self.table_model.item_data.data_link is not None:
            id_row = self.table_model.item_data.data[number_row][0].value
            if id_row is not None:
                data = self.table_model.item_data.data_link.get(id_row)
                data = data if data else []

                self.widget_link_row.populate(data=data, number_row=number_row)
    
    def _add_link_row(self, data: tuple[int, list[DATACLASSES.DATA_CELL]]) -> None:
        number_row, row_inventor_link = data
        id_row = self.table_model.item_data.data[number_row][0].value
        self.table_model.item_data.add_item_data_link(id_row, row_inventor_link)
        
        self.widget_link_row.populate(data=self.table_model.item_data.data_link.get(id_row), number_row=number_row)
        self.change_table()
        self.table_model.item_data.set_is_update_link(True)

    def _del_link_row(self, data: tuple[int, int]) -> None:
        number_row, row_link = data
        id_row = self.table_model.item_data.data[number_row][0].value
        del self.table_model.item_data.data_link[id_row][row_link]
        
        self.widget_link_row.populate(data=self.table_model.item_data.data_link.get(id_row), number_row=number_row)
        self.change_table()
        self.table_model.item_data.set_is_update_link(True)
    

class __Window(QtWidgets.QMainWindow):
    """
    Для тестов без запуска основго приложения

    + тест таблицы в отедльном окне 
    """
    def __init__(self):
        super().__init__()
        with open(os.path.join(SETTING.RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', SETTING.ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        self.resize(1500, 750)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.v_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)

        browser = BrowserWidget(self)
        browser.hide()
        browser.open_project(r'D:\Python\AlfaServis\Constructor\Proekt 1.scdata')
        item_by_tree = self.get_item_tree_from_name(browser.tree)

        self.page_table = PageTable(self)
        self.v_layout.addWidget(self.page_table)

        self.page_table.populate(item_by_tree)
    
    def get_item_tree_from_name(self, tree) -> TableByItem:
        top_level_item: Iterable[ProjectItem] = (tree.topLevelItem(i) for i in range(tree.topLevelItemCount()))
        for item in top_level_item:
            for i in range(item.childCount()):
                child = item.child(i)
                for j in range(child.childCount()):
                    cchild = child.child(j)
                    if isinstance(cchild, TableByItem):
                        return cchild


if __name__ == '__main__':
    import sys
    from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx
    app = QtWidgets.QApplication(sys.argv)
    window = __Window()
    
    window.show()
    sys.exit(app.exec_())