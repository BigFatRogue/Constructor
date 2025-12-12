import os
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.core.data_tables import ColumnConfig, InventorSpecificationDataItem

from projects.specification.config.app_context.app_context import SETTING, SIGNAL_BUS, ENUMS, CONSTANTS

from projects.specification.ui.widgets.table_widget.tw_table_item import TableItem
from projects.specification.ui.widgets.table_widget.tw_selection_table import SelectionRect
from projects.specification.ui.widgets.table_widget.tw_popup_order_column import PopupOrder


class CheckBoxVerticalHeader(QtWidgets.QCheckBox):
    def __init__(self, parent):
        super().__init__(parent)

        self.data_index: int = None 


class ButtonHorizontalHeader(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__(parent)

        self.column_index: int = None
        self.data_index: int = None
        self.is_checked = False
        self.state_sorted = ENUMS.STATE_SORTED_COLUMN.EMPTY 

        self.resize(22, 22)
        self.setCheckable(True)
        
        self.dict_icon = {}
        for icon_name, state, tool_tip in zip(
            ('filter.png', 'filter_az.png', 'filter_za.png'),
            (ENUMS.STATE_SORTED_COLUMN.EMPTY, ENUMS.STATE_SORTED_COLUMN.SORTED, ENUMS.STATE_SORTED_COLUMN.REVERSE),
            ('Установить фильтр', 'Установлен фильтр от А до Я', 'Установлен фильтр от Я до А')
            ):

            ico = QtGui.QIcon()
            ico.addFile(os.path.join(SETTING.ICO_FOLDER, icon_name))
            self.dict_icon[state] = (ico, tool_tip)
        
    def set_sorted_state(self, state) -> None:
        self.state_sorted = state
        ico, tool_tip = self.dict_icon[state]
        self.setIcon(ico)
        self.setToolTip(tool_tip)
    
    def reset_view_sorted(self) -> None:
        self.set_sorted_state(ENUMS.STATE_SORTED_COLUMN.EMPTY)


class HeaderWithOverlayWidgets(QtWidgets.QHeaderView):
    """
    Универсальный заголовок для QTableWidget/QTableView,
    позволяющий добавлять виджеты поверх секций.
    Поддерживает горизонтальные и вертикальные заголовки.
    """

    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2

    def __init__(self, orientation, parent_table: QtWidgets.QTableWidget):
        super().__init__(orientation, parent_table)

        self.widgets: list[dict[str, ButtonHorizontalHeader | CheckBoxVerticalHeader]] = [] 
        self.table: TableItem = parent_table
        self.current_step = 100
        self.steps_section_size: dict [int, dict[int, int]] = self.__generate_steps_size_section()
        self.original_font_size = self.font().pointSize()
        self.min_font_size = 2
        self.steps_view_font: dict[int, int] = self.__generate_steps_view_font()

        self.setMinimumHeight(25)

        self.sectionResized.connect(self.__updateWidgets)
        self.sectionMoved.connect(self.__updateWidgets)
        self.geometriesChanged.connect(self.__updateWidgets)

        if orientation == QtCore.Qt.Horizontal:
            parent_table.horizontalScrollBar().valueChanged.connect(self.__updateWidgets)
        else:
            parent_table.verticalScrollBar().valueChanged.connect(self.__updateWidgets)

    def addWidget(self, widget: ButtonHorizontalHeader | CheckBoxVerticalHeader, data_index=None, align=ALIGN_RIGHT):
        """
        Добавляет виджет поверх секции (колонки или строки).
        widget — уже созданный, parent должен быть = table.
        """
        widget.setVisible(True)
        widget.raise_()

        section_index = len(self.widgets)

        self.widgets.append({
            "widget": widget,
            "align": align,
        })
        
        widget.data_index = data_index

        if self.orientation() == QtCore.Qt.Vertical:
            fm = self.fontMetrics()
            row_count = self.table.rowCount()
            text_w = fm.horizontalAdvance(str(row_count))
            widget_w = widget.width()
            self.setMinimumWidth(self.sectionSize(section_index) + text_w + widget_w)
        
        self.__updateWidget(section_index)

    def __updateWidgets(self):
        for i in range(len(self.widgets)):
            self.__updateWidget(i)
        self.viewport().update()

    def __updateWidget(self, section_index: int):
        info = self.widgets[section_index]
        widget = info["widget"]
        align = info["align"]

        horizontal = (self.orientation() == QtCore.Qt.Horizontal)

        if horizontal:
            x, y = self.sectionViewportPosition(section_index), 0
            w, h = self.sectionSize(section_index), self.height()
        else:
            x, y  = 0, self.sectionViewportPosition(section_index)
            w, h = self.width(), self.sectionSize(section_index)

        wdg_w = min(24, w - 4)
        wdg_h = min(20, h - 4)

        if horizontal:
            if align == self.ALIGN_LEFT:
                wdg_x = x + 2
            elif align == self.ALIGN_CENTER:
                wdg_x = x + (w - wdg_w) // 2
            else:  
                wdg_x = x + w - (wdg_w + 2)
            wdg_y = (h - wdg_h) // 2
        else:
            wdg_y = y + (h - wdg_h) // 2
            if align == self.ALIGN_LEFT:
                wdg_x = 2
            elif align == self.ALIGN_CENTER:
                wdg_x = (w - wdg_w) // 2
            else:  
                wdg_x = w - (wdg_w + 2)

        header_in_table = self.mapToParent(QtCore.QPoint(0, 0))

        global_x = header_in_table.x() + wdg_x
        global_y = header_in_table.y() + wdg_y

        widget.setGeometry(global_x, global_y, wdg_w, wdg_h)
        widget.show()

    def get_widget(self, index: int) -> ButtonHorizontalHeader | CheckBoxVerticalHeader:
        return self.widgets[index]['widget']
    
    def get_widgets(self) -> list[ButtonHorizontalHeader | CheckBoxVerticalHeader]:
        return [item['widget'] for item in self.widgets]
    
    def __generate_steps_size_section(self) -> dict [int, dict[int, int]]:
        dct: dict [int, dict[int, int]] = {}
        
        for index_sec in range(self.count()):
            size_100 = int(self.sectionSize(index_sec) / (self.current_step / 100))
            dct_section: dict[int, int] = {}
            for step in range(self.table.min_zoom, self.table.max_zoom + self.table.step_zoom, self.table.step_zoom):
                size = int(size_100 * step / 100)
                if size < self.minimumSectionSize():
                    size = self.minimumSectionSize()
                dct_section[step] = size
            dct[index_sec] = dct_section
        return dct
    
    def __generate_steps_view_font(self) -> dict[int, float]:
        dct = {}
        for step in range(self.table.min_zoom, self.table.max_zoom + self.table.step_zoom, self.table.step_zoom):
            font_size = int(self.original_font_size * step / 100)

            if font_size < self.min_font_size:
                font_size = self.min_font_size
            if step == 100:
                font_size = self.original_font_size 
            dct[step] = font_size
        return dct

    def set_zoom(self, current_zoom_step: int) -> None:
        self.current_step = current_zoom_step
        font = self.font()
        font.setPointSize(self.steps_view_font[current_zoom_step])
        self.setFont(font)
        if not self.steps_section_size:
            self.steps_section_size = self.__generate_steps_size_section()
        for sec, dct_sec_size in self.steps_section_size.items():
            self.resizeSection(sec, dct_sec_size[current_zoom_step])
            
            # widget = self.widgets[sec]['widget']
            # x, y, w, h = widget.geometry().getRect()
            # widget.resize(int(w * current_zoom_step / 100), int(h * current_zoom_step / 100))
            
    def mouseReleaseEvent(self, event):
        self.steps_section_size = self.__generate_steps_size_section()
        return super().mouseReleaseEvent(event)


class NoSelectionDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        opt = QtWidgets.QStyleOptionViewItem(option)

        if opt.state & QtWidgets.QStyle.State_Selected:
            opt.state &= ~QtWidgets.QStyle.State_Selected

        super().paint(painter, opt, index)



class Table(QtWidgets.QTableWidget):
    signal_change_table = QtCore.pyqtSignal()  
    signal_select_item = QtCore.pyqtSignal(TableItem)
    signal_sorted_column = QtCore.pyqtSignal(tuple)
    signal_sorted_columns = QtCore.pyqtSignal(list)
    signal_zoom_in = QtCore.pyqtSignal()  
    signal_zoom_out = QtCore.pyqtSignal() 
    signal_resize =  QtCore.pyqtSignal() 

    def __init__(self, parent, min_zoom: int=0, max_zoom: int=450, step_zoom: int=10, has_filter=True, has_vertical_check_box=True):
        super().__init__(parent)
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.step_zoom = step_zoom
        self.has_filter = has_filter
        self.has_vertical_check_box = has_vertical_check_box

        self.selection_rect = SelectionRect(self)
        self.selection_rect.hide()
        self.setItemDelegate(NoSelectionDelegate(self))
        
        self.popup_order = PopupOrder(self)
        self.popup_order.signal_sorted.connect(self.sorted_column)

        self.__init_widgets()

        SIGNAL_BUS.set_align_cell.connect(self.set_align_cell)
        SIGNAL_BUS.font_family.connect(self.set_font_family_cell)
        SIGNAL_BUS.font_size.connect(self.set_font_size_cell)
        SIGNAL_BUS.bold.connect(self.set_bold_cell)
        SIGNAL_BUS.italic.connect(self.set_italic_cell)
        SIGNAL_BUS.underline.connect(self.set_underline_cell)
    
    def __init_widgets(self) -> None:
        self.__setup_horizontal_header()
        self.__setup_vertical_header()

        self.setWordWrap(False)
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        # self.itemClicked.connect(self.item_clicked)
        self.itemSelectionChanged.connect(self.view_selection_rect)
    
    def __setup_horizontal_header(self) -> None:
        if self.has_filter:
            self.custom_h_header = HeaderWithOverlayWidgets(QtCore.Qt.Horizontal, self)
            self.setHorizontalHeader(self.custom_h_header)
            self.custom_h_header.setHighlightSections(True)
            self.custom_h_header.setSectionsClickable(True)
            # header.setSectionsMovable(True)
            # header.setMouseTracking(True)
            self.custom_h_header.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.horizontalHeader().sectionResized.connect(self.view_selection_rect)
        self.horizontalScrollBar().valueChanged.connect(self.view_selection_rect)

    def __setup_vertical_header(self) -> None:
        if self.has_vertical_check_box:
            self.custom_v_header = HeaderWithOverlayWidgets(QtCore.Qt.Vertical, self)
            self.setVerticalHeader(self.custom_v_header)
            self.custom_v_header.setHighlightSections(True)
            self.custom_v_header.setSectionsClickable(True)
            # header.setSectionsMovable(True)
            # header.setMouseTracking(True)
            self.custom_v_header.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.verticalScrollBar().valueChanged.connect(self.view_selection_rect)

        self.verticalHeader().sectionClicked.connect(self.click_vertical_section)
        self.verticalHeader().sectionEntered.connect(self.click_vertical_section)

    def add_button_horizontal_header(self, data_index) -> None:
        btn = ButtonHorizontalHeader(self)
        btn.set_sorted_state(ENUMS.STATE_SORTED_COLUMN.EMPTY)
        btn.clicked.connect(self.click_btn_horizontal_header)
        self.custom_h_header.addWidget(btn, data_index, 2)

    def add_buttons_horizontal_header(self, columns: list[ColumnConfig]) -> None:
        if self.has_filter:
            if not self.custom_h_header.widgets:
                for data_index, col in enumerate(columns):
                    if col.is_view:
                        self.add_button_horizontal_header(data_index)

    def add_check_box_vertical_header(self) -> None:
        if self.has_vertical_check_box:
            for i in range(len(self.custom_v_header.widgets), self.rowCount()):
                check_box = QtWidgets.QCheckBox(self)
                check_box.clicked.connect(self.click_cb_vertical_header)
                self.custom_v_header.addWidget(widget=check_box, data_index=i, align=HeaderWithOverlayWidgets.ALIGN_RIGHT)

    def populate(self, table_data: InventorSpecificationDataItem, is_read_only=True) -> None:
        dataset = table_data.get_data()
        columns: tuple[ColumnConfig] = table_data.config.columns + table_data.unique_config.columns
        columns_name: tuple[str, ...] = tuple(col.column_name for col in columns if col.is_view)
        
        self.setRowCount(len(dataset))
        self.setColumnCount(len(columns_name))
        self.setHorizontalHeaderLabels(columns_name)

        self.add_buttons_horizontal_header(columns)
        self.add_check_box_vertical_header()
        
        data_number_index = table_data.get_index_from_name_filed('number_row')
        for y, row in enumerate(dataset):
            # view_columns = tuple((value, data_x) for data_x, (value, col) in enumerate(zip(row, columns)) if col.is_view)
            # view_columns = tuple(value for col, value in zip(columns, row) if col.is_view)
            
            if data_number_index != -1:
                row[data_number_index] = y
            
            # for x, (value, data_x) in enumerate(view_columns):
            x = 0
            for col, value in zip(columns, row):
                if col.is_view:
                    value = '' if value is None else value
                    qItem = TableItem(str(value), min_zoom=self.min_zoom, max_zoom=self.max_zoom, step_zoom=self.step_zoom)
                    # qItem.set_font_size(12)
                    # qItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    # qItem.setData(CONSTANTS.QROLE_H_TEXT_ALIGN, QtCore.Qt.AlignmentFlag.AlignHCenter)
                    # qItem.setData(CONSTANTS.QROLE_V_TEXT_ALIGN, QtCore.Qt.AlignmentFlag.AlignVCenter)
                    # qItem.setData(CONSTANTS.QROLE_DATA_X, data_x)
                    
                    if is_read_only:
                        qItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    else:
                        qItem.setFlags(qItem.flags())

                    self.setItem(y, x, qItem)
                    x += 1

    def click_btn_horizontal_header(self) -> None:
        self.popup_order.show(self.sender())
    
    def sorted_column(self, state_sorted) -> None:
        if self.popup_order.is_multi_sorted:
            self.signal_sorted_columns.emit(self.custom_h_header.get_widgets())
        else:
            btn: ButtonHorizontalHeader = self.popup_order.current_button_header
            self.signal_sorted_column.emit((btn.data_index, state_sorted))
        self.signal_change_table.emit()

    def choose_row(self, check_box: CheckBoxVerticalHeader) -> None:
        row = check_box.data_index
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                if check_box.checkState():
                    item.setBackground(QtGui.QColor(200, 25, 25))
                else:
                    item.setBackground(QtGui.QColor(255, 255, 255))

    def click_cb_vertical_header(self) -> None:
        check_box: CheckBoxVerticalHeader = self.sender()
        self.choose_row(check_box)

    def click_vertical_section(self, row) -> None:
        if self.has_vertical_check_box:
            check_box: CheckBoxVerticalHeader = self.custom_v_header.get_widget(row)
            check_box.setChecked(not check_box.checkState())
            self.choose_row(check_box)
            
    def item_clicked(self, item: TableItem) -> None:
        # print(item.column(), item.row())
        # self.signal_select_item.emit(item)
        print(item.get_style_dict())
    
    def set_align_cell(self, align: tuple[int, int]) -> None:
        h_align, v_align = align        
        for item in self.selectedItems():
            item: TableItem
            item.set_align(h_align, v_align)
        self.signal_change_table.emit()

    def set_font_family_cell(self, value) -> None:
        ...

    def set_font_size_cell(self, value) -> None:
        ...

    def set_bold_cell(self) -> None:
        for item in self.selectedItems():
            font = item.font()
            font.setBold(not font.bold())
            item.setFont(font)

    def set_italic_cell(self) -> None:
        for item in self.selectedItems():
            font = item.font()
            font.setItalic(not font.italic())
            item.setFont(font)

    def set_underline_cell(self) -> None:
        for item in self.selectedItems():
            font = item.font()
            font.setUnderline(not font.underline())
            item.setFont(font)

    def reset_view_sorted_header(self) -> None:
        for btn in self.custom_h_header.get_widgets():
            btn.reset_view_sorted()

    def view_selection_rect(self) -> None:
        self.selection_rect.set_selection(self.selectedItems())

    def set_property_selection_item(self, item: TableItem) -> None:
        style = item.get_style_dict()
        print(style)

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.signal_zoom_in.emit()
            else:
                self.signal_zoom_out.emit()
            event.accept()
        else:
            super().wheelEvent(event)




