
from PyQt5 import QtWidgets, QtCore
from projects.specification.config.app_context import DATACLASSES

from projects.specification.ui.widgets.table.tw_model_data_table import ModelDataTable


class HeaderWithOverlayWidgets(QtWidgets.QHeaderView):
    """
    Универсальный заголовок для QTableWidget/QTableView,
    позволяющий добавлять виджеты поверх секций.
    Поддерживает горизонтальные и вертикальные заголовки.
    """
    signal_resize_section = QtCore.pyqtSignal()

    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2

    def __init__(self, orientation: QtCore.Qt.Orientation, table_view: QtWidgets.QTableView, range_zoom: tuple[int, int, int]):
        super().__init__(orientation, table_view)
        self.setObjectName('HeaderWithOverlayWidgets')
        self.widgets: list[QtWidgets.QWidget] = [] 
        self.table_view = table_view
        self._table_model: ModelDataTable = None
        self.min_zoom, self.max_zoom, self.step_zoom = range_zoom
        self._align_widget = self.ALIGN_RIGHT

        self._current_step = 100
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
    
    @property
    def table_model(self) -> ModelDataTable:
        return self._table_model

    def set_table_model(self, table_model: ModelDataTable) -> None:
        self._table_model = table_model

    def _set_size_section(self) -> None:
        """
        Установка размеров секций
        
        Переопределяемый метод
        """
    
    def set_widget(self, align: int = 2) -> None:
        """
        Установка виджета в секцию заголовка

        :param align: выравнивание (0 -лево, 1- середина, 2 -право)
        :type align: int
        """

    def _set_parameters_widget(self) -> None:
        """
        Установка параметров виджетов
        
        Переопределяемый метод
        """ 

    def hide_widget(self) -> None:
        for widget in self.widgets:
            widget.hide()

    def _update_widgets(self) -> None:
        for i in range(len(self.widgets)):
            self._update_widget(i) 
        self.viewport().update()

    def _update_widget(self, section_index: int) -> None:
        widget = self.widgets[section_index]
        if not widget.isVisible():
            return

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
            if self._align_widget == self.ALIGN_LEFT:
                wdg_x = x + 2
            elif self._align_widget == self.ALIGN_CENTER:
                wdg_x = x + (w - wdg_w) // 2
            else:  
                wdg_x = x + w - (wdg_w + 2)
            wdg_y = (h - wdg_h) // 2
        else:
            wdg_y = y + (h - wdg_h) // 2
            if self._align_widget == self.ALIGN_LEFT:
                wdg_x = 2
            elif self._align_widget == self.ALIGN_CENTER:
                wdg_x = (w - wdg_w) // 2
            else:  
                wdg_x = w - (wdg_w + 2)

        header_in_table = self.mapToParent(QtCore.QPoint(0, 0))

        global_x = header_in_table.x() + wdg_x
        global_y = header_in_table.y() + wdg_y

        widget.setGeometry(global_x, global_y, wdg_w, wdg_h)
        widget.show()
        
    def __generate_steps_for_zoom_size_section(self) -> dict [int, dict[int, int]]:
        dct: dict [int, dict[int, int]] = {}
        
        for index_sec in range(self.count()):
            size_100 = int(self.sectionSize(index_sec) / (self._current_step / 100))
            dct_section: dict[int, int] = {}
            for step in range(self.min_zoom, self.max_zoom + self.step_zoom, self.step_zoom):
                size = int(size_100 * step / 100)
                if size < self.minimumSectionSize():
                    size = self.minimumSectionSize()
                dct_section[step] = size
            dct[index_sec] = dct_section
        return dct
    
    def __generate_steps_for_zoom_view_font(self) -> dict[int, float]:
        dct = {}
        for step in range(self.min_zoom, self.max_zoom + self.step_zoom, self.step_zoom):
            font_size = int(self.original_font_size * step / 100)

            if font_size < self.min_font_size:
                font_size = self.min_font_size
            if step == 100:
                font_size = self.original_font_size 
            dct[step] = font_size
        return dct

    def set_zoom(self, step: int) -> None:
        if self._current_step == step:
            return
        
        self._current_step = step
        font = self.font()
        font.setPointSize(self.steps_view_font[step])
        self.setFont(font)
        if not self.steps_section_size:
            self.steps_section_size = self.__generate_steps_for_zoom_size_section()
        for sec, dct_sec_size in self.steps_section_size.items():
            self.resizeSection(sec, dct_sec_size[step])

    def get_section_size(self) -> tuple[int, ...]:
        return tuple(self.sectionSize(i) for i in range(self.count()))

    def mouseReleaseEvent(self, event):
        self.steps_section_size = self.__generate_steps_for_zoom_size_section()
        self.signal_resize_section.emit()
        self._set_current_header_size_item_data()
        return super().mouseReleaseEvent(event)
    
    def _set_current_header_size_item_data(self):
        """
        Установка текущих значений в размеров заголвков в header_data 
        """
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            data = self._table_model.item_data.horizontal_header_parameter
        else:
            data = self._table_model.item_data.vertical_header_parameter
        for size, header in zip(self.get_section_size(), data):
            header.size = size
    
    def deleteLater(self):
        for widget in self.widgets:
            widget.deleteLater()
        return super().deleteLater()

