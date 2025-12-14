
from PyQt5 import QtWidgets, QtCore


class HeaderWithOverlayWidgets(QtWidgets.QHeaderView):
    """
    Универсальный заголовок для QTableWidget/QTableView,
    позволяющий добавлять виджеты поверх секций.
    Поддерживает горизонтальные и вертикальные заголовки.
    """
    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2

    def __init__(self, orientation: QtCore.Qt.Orientation, table: QtWidgets.QTableWidget):
        super().__init__(orientation, table)

        self.widgets: list[QtWidgets.QWidget] = [] 
        self.table: QtWidgets.QTableWidget = table
        self.__align_widget = self.ALIGN_RIGHT


        self.current_step = 100
        self.steps_section_size: dict [int, dict[int, int]] = self.__generate_steps_for_zoom_size_section()
        self.original_font_size = self.font().pointSize()
        self.min_font_size = 2
        self.steps_view_font: dict[int, int] = self.__generate_steps_for_zoom_view_font()

        self.setHighlightSections(True)
        self.setSectionsClickable(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.setMinimumHeight(25)

        self.sectionResized.connect(self._update_widgets)
        self.sectionMoved.connect(self._update_widgets)
        self.geometriesChanged.connect(self._update_widgets)        
    
    def set_align(self, align: int):
        self.__align_widget = align 

    def add_widget(self, widget: QtWidgets.QWidget):
        """
        Добавляет виджет поверх секции (колонки или строки).
        widget — уже созданный, parent должен быть = table.
        """
        widget.setVisible(True)
        widget.raise_()

        section_index = len(self.widgets)
        widget.index_section = section_index

        self.widgets.append(widget)
        
        if self.orientation() == QtCore.Qt.Vertical:
            fm = self.fontMetrics()
            row_count = self.table.rowCount()
            text_w = fm.horizontalAdvance(str(row_count))
            widget_w = widget.width()
            self.setMinimumWidth(self.sectionSize(section_index) + text_w + widget_w)
        
        self._update_widget(section_index)

    def _update_widgets(self):
        for i in range(len(self.widgets)):
            self._update_widget(i)
        self.viewport().update()

    def _update_widget(self, section_index: int):
        widget = self.widgets[section_index]

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
            if self.__align_widget == self.ALIGN_LEFT:
                wdg_x = x + 2
            elif self.__align_widget == self.ALIGN_CENTER:
                wdg_x = x + (w - wdg_w) // 2
            else:  
                wdg_x = x + w - (wdg_w + 2)
            wdg_y = (h - wdg_h) // 2
        else:
            wdg_y = y + (h - wdg_h) // 2
            if self.__align_widget == self.ALIGN_LEFT:
                wdg_x = 2
            elif self.__align_widget == self.ALIGN_CENTER:
                wdg_x = (w - wdg_w) // 2
            else:  
                wdg_x = w - (wdg_w + 2)

        header_in_table = self.mapToParent(QtCore.QPoint(0, 0))

        global_x = header_in_table.x() + wdg_x
        global_y = header_in_table.y() + wdg_y

        widget.setGeometry(global_x, global_y, wdg_w, wdg_h)
        widget.show()
    
    def get_widgets(self) -> list[QtWidgets.QWidget]:
        return [item['widget'] for item in self.widgets]
    
    def __generate_steps_for_zoom_size_section(self) -> dict [int, dict[int, int]]:
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
    
    def __generate_steps_for_zoom_view_font(self) -> dict[int, float]:
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
            self.steps_section_size = self.__generate_steps_for_zoom_size_section()
        for sec, dct_sec_size in self.steps_section_size.items():
            self.resizeSection(sec, dct_sec_size[current_zoom_step])
                        
    def mouseReleaseEvent(self, event):
        self.steps_section_size = self.__generate_steps_for_zoom_size_section()
        return super().mouseReleaseEvent(event)
    

