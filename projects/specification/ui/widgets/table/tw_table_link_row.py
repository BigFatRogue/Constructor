import os
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.app_context import SETTING, DATACLASSES
from projects.specification.core.config_table import ColumnConfig, GENERAL_ITEM_CONFIG, INVENTOR_ITEM_CONFIG

from projects.specification.ui.widgets.browser_widget.bw_table_inventor_item import TableInventorItem

from projects.specification.ui.widgets.table.tw_vhow_choose import VerticallWithOverlayWidgetsChoose
from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable

from projects.tools.functions.create_action_menu import create_action


class TitleViewLinkRow(QtWidgets.QFrame):
    signal_toggle_view = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)

        self.icon_hide: QtGui.QIcon = None
        self.icon_show: QtGui.QIcon = None
        self.is_visible = False

        self.setObjectName('TitleViewLinkRow')
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setFixedHeight(20)

        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(5)
        
        self.btn_set_view = QtWidgets.QPushButton(self)
        self.btn_set_view.setObjectName('btn_set_view_link_content')
        self.btn_set_view.setFixedSize(20, 20)
        self.btn_set_view.setIconSize(QtCore.QSize(12, 12))
        self.btn_set_view.clicked.connect(self._toggle_btn)
        self._set_icon_show()
        self.h_layout.addWidget(self.btn_set_view)

        self.label_ico_link = QtWidgets.QLabel(self)
        self.label_ico_link.setFixedSize(20, 20)
        pixmap = QtGui.QPixmap(os.path.join(SETTING.ICO_FOLDER, 'link.png'))
        self.label_ico_link.setPixmap(pixmap.scaled(12, 12))
        self.label_ico_link.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.h_layout.addWidget(self.label_ico_link)

        self.label_number_row = QtWidgets.QLabel(self)
        self.label_number_row.setText('Связь строки:')
        self.label_number_row.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.h_layout.addWidget(self.label_number_row)

        self.label_count_link= QtWidgets.QLabel(self)
        self.label_count_link.setText('Количество связей:')
        self.label_count_link.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.h_layout.addWidget(self.label_count_link)

    def populate(self, number_row: int, count_link: int) -> None:
        self.label_number_row.setText(f'Связь строки: <b>{number_row + 1}</b>')
        self.label_count_link.setText(f'Количество связей: <b>{count_link}</b>')

    def _toggle_btn(self) -> None:
        if self.is_visible:
            self._set_icon_show()
        else:
            self._set_icon_hide()
        self.signal_toggle_view.emit(self.is_visible)
        self.is_visible = not self.is_visible
        
    def _set_icon_hide(self) -> None:
        if self.icon_hide is None:
            self.icon_hide = QtGui.QIcon()
            self.icon_hide.addFile(os.path.join(SETTING.ICO_FOLDER, 'arrow_down_hide.png'))
        self.btn_set_view.setIcon(self.icon_hide)

    def _set_icon_show(self) -> None:
        if self.icon_show is None:
            self.icon_show = QtGui.QIcon()
            self.icon_show.addFile(os.path.join(SETTING.ICO_FOLDER, 'arrow_down_show.png'))
        self.btn_set_view.setIcon(self.icon_show)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        self._toggle_btn()
        return super().mouseReleaseEvent(event)


class ModelTableLink(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        super().__init__(parent)
        self._columns_config: list[ColumnConfig] = GENERAL_ITEM_CONFIG.columns + INVENTOR_ITEM_CONFIG.columns
        self._view_columns = [col for col in self._columns_config if col.is_view]
        self._index_column_view = self._set_index_column_view()
        self._data: list[list[DATACLASSES.DATA_CELL]] = []

    def _set_index_column_view(self) -> dict[int, int]:
        """
        Из указанного в QTableView адреса колонки преобразует в адрес колонки в _data 
        
        :return: Сслыка видимой колонки на колонку в _data
        :rtype: dict[int, int]
        """
        dct = {}
        view_x = 0
        for x, col in enumerate(self._columns_config):
            if col.is_view:
                dct[view_x] = x
                view_x += 1
        return dct

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._view_columns)
    
    def data(self, index: QtCore.QModelIndex, role=QtCore.Qt.ItemDataRole):
        if not index.isValid() and not self._data:
            return
        
        row = index.row()
        column = self._index_column_view[index.column()]

        if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
            return self._data[row][column].value

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._view_columns[section].column_name
            elif orientation == QtCore.Qt.Orientation.Vertical:
                return str(section + 1)

    def flags(self, index):
        return QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsEditable

    def populate(self, data: list[list[DATACLASSES.DATA_CELL]]) -> None:
        self._data = data
        self.layoutChanged.emit()


class BaseTableView(QtWidgets.QTableView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)

    def _stretch_columns_evenly(self):
        header = self.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.resizeColumnsToContents()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)

        total_width = self.viewport().width()
        used_width = sum(header.sectionSize(i) for i in range(header.count()))
        extra = max(0, total_width - used_width)

        if header.count() == 0:
            return

        add = extra // header.count()

        for i in range(header.count()):
            header.resizeSection(i, header.sectionSize(i) + add)
    

class TableViewLink(BaseTableView):
    signal_del_link = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.init_context_menu()
    
    def init_context_menu(self) -> None:
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.context_menu = QtWidgets.QMenu(self)
        
        create_action(menu=self.context_menu, 
            title='Удалить связь',
            triggerd=self.del_link
            )
        
    def show_context_menu(self, position: QtCore.QPoint) -> None:
        self.context_menu.exec_(self.viewport().mapToGlobal(position))
    
    def populate(self, data: list[list[DATACLASSES.DATA_CELL]]) -> None:
        if self.model():
            model: ModelTableLink = self.model()
            model.populate(data)
            
            self._stretch_columns_evenly()
            
            h = self.verticalHeader().count() * self.verticalHeader().sectionSize(0) + self.horizontalHeader().height() + self.horizontalScrollBar().height()
            h = 250 if h > 250 else h
            self.setFixedHeight(int(h))
    
    def del_link(self) -> None:
        self.signal_del_link.emit(self.currentIndex().row())
 

class TableViewResultSearch(BaseTableView):
    signal_choose_row = QtCore.pyqtSignal(list)

    def setModel(self, model):
        super().setModel(model)

        if model:
            self._stretch_columns_evenly()
    
    def show_result_search_row(self, rows: set[int]) -> None:
        if self.model():
            for row in range(self.model().rowCount()):
                self.showRow(row)
            
            for row in range(self.model().rowCount()):
                if row not in rows:
                    self.hideRow(row)
    
    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        index: QtCore.QModelIndex = self.indexAt(event.pos())
        if index:
            model: ModelDataTable = self.model()
            self.signal_choose_row.emit(model.get_copy_row(index.row()))

        return super().mouseDoubleClickEvent(event)


class SearchAndAddLink(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self._dict_item_browser_inventor_table: dict[str, TableInventorItem] = {}

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(5)
        self.v_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.frame_search = QtWidgets.QFrame(self)
        self.frame_search.setFixedHeight(22)
        self.v_layout.addWidget(self.frame_search)

        self.h_layout_frame_search = QtWidgets.QHBoxLayout(self.frame_search)
        self.h_layout_frame_search.setContentsMargins(0, 0, 0, 0)
        self.h_layout_frame_search.setSpacing(4)
        self.h_layout_frame_search.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        self.label_cb_select_inventor_spec = QtWidgets.QLabel(self.frame_search)
        self.label_cb_select_inventor_spec.setText('Искать в')
        self.h_layout_frame_search.addWidget(self.label_cb_select_inventor_spec)

        self.cb_select_invetor_spec = QtWidgets.QComboBox(self.frame_search)
        # self.cb_select_invetor_spec.setFixedWidth(150)
        self.h_layout_frame_search.addWidget(self.cb_select_invetor_spec)

        self.le_search = QtWidgets.QLineEdit(self.frame_search)
        self.le_search.setPlaceholderText('Поиск')
        self.le_search.setFixedWidth(400)
        self.le_search.textEdited.connect(self.le_search_text_edited)
        self.h_layout_frame_search.addWidget(self.le_search)

        self.check_box_case_sensetive = QtWidgets.QCheckBox(self.frame_search)
        self.check_box_case_sensetive.setText('С учётом регистра')
        self.h_layout_frame_search.addWidget(self.check_box_case_sensetive)

        self.h_layout_frame_search.addStretch()

        self.label_title = QtWidgets.QLabel(self)
        self.label_title.setText('<b>Результаты поиска</b>')
        self.label_title.hide()
        self.v_layout.addWidget(self.label_title)

        self.table_view_result_serach = TableViewResultSearch(self)
        self.table_view_result_serach.hide()
        self.v_layout.addWidget(self.table_view_result_serach)

    def set_table_inventor(self, items: list[TableInventorItem]) -> None:
        self.cb_select_invetor_spec.clear()
        for item in items:
            self._dict_item_browser_inventor_table[item.item_data.table_name] = item
            self.cb_select_invetor_spec.addItem(item.item_data.table_name)
            self.cb_select_invetor_spec.setCurrentText(item.item_data.table_name)
    
    def le_search_text_edited(self, text: str) -> None:
        if text:
            self._show_result_search(text)
        else:
            self.label_title.hide()
            self.table_view_result_serach.hide()

    def _show_result_search(self, text: str) -> None:
        self.label_title.show()
        self.table_view_result_serach.show()

        key = self.cb_select_invetor_spec.currentText()
        item: TableInventorItem = self._dict_item_browser_inventor_table.get(key)
        if item:
            self.table_view_result_serach.setModel(item.table_data)
            is_case_sensetive = self.check_box_case_sensetive.checkState() == QtCore.Qt.CheckState.Checked
            search_row = item.table_data.filter(text, is_case_sensetive)
            self.table_view_result_serach.show_result_search_row(search_row)
        else:
            self.table_view_result_serach.setModel(None)


class ContentViewLinkRow(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 0, 0, 0)
        self.v_layout.setSpacing(0)

        self.table_view_link = TableViewLink(self)
        self.table_view_link.setModel(ModelTableLink(self))
        self.v_layout.addWidget(self.table_view_link)

        self.widget_serach_and_add_link = SearchAndAddLink(self)
        self.v_layout.addWidget(self.widget_serach_and_add_link)

    def populate(self, data: list[list[DATACLASSES.DATA_CELL]]) -> None:
        self.table_view_link.populate(data)
        

class LinkRow(QtWidgets.QWidget):
    signal_is_show = QtCore.pyqtSignal(bool)
    signal_add_row_link = QtCore.pyqtSignal(tuple)
    signal_del_row_link = QtCore.pyqtSignal(tuple)

    def __init__(self, parent):
        super().__init__(parent)
        
        self._curent_number_row: int = None

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        self.v_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.title = TitleViewLinkRow(self)
        self.title.signal_toggle_view.connect(self.toggle_content)
        self.title.signal_toggle_view.connect(self.signal_is_show)
        self.v_layout.addWidget(self.title)

        self.content = ContentViewLinkRow(self)
        self.content.widget_serach_and_add_link.table_view_result_serach.signal_choose_row.connect(self._add_link_row)
        self.content.table_view_link.signal_del_link.connect(self._del_link_row)
        self.content.hide()
        self.v_layout.addWidget(self.content)

        # self.toggle_content(False)
                
    def toggle_content(self, value) -> None:
        if value:
            self.content.hide()
        else:
            self.content.show()
    
    def populate(self, number_row: int, data: list[list[DATACLASSES.DATA_CELL]]=None) -> None:
        self._curent_number_row = number_row
        self.title.populate(number_row=number_row, count_link=len(data))
        self.content.populate(data)

    def set_table_inventor(self, items: list[TableInventorItem]) -> None:
        self.content.widget_serach_and_add_link.set_table_inventor(items)
    
    def _add_link_row(self, row: list[DATACLASSES.DATA_CELL]) -> None:
        self.signal_add_row_link.emit((self._curent_number_row, row))
    
    def _del_link_row(self, row_link: int) -> None:
        self.signal_del_row_link.emit((self._curent_number_row, row_link))
