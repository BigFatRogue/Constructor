from PyQt5 import QtWidgets, QtCore


class TableItem(QtWidgets.QTableWidgetItem):
    """
    Элемент таблицы
    """
    def __init__(self, text, min_zoom: int=0, max_zoom: int=200, step_zoom: int=10):
        super().__init__(text)
        self.original_font_size = self.font().pointSizeF()
        self.min_font_size = 2
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.step_zoom = step_zoom
        self.steps_view_font: dict[int, int] = self.__generate_steps_view_font()
        self.h_align = QtCore.Qt.AlignmentFlag.AlignHCenter
        self.v_align = QtCore.Qt.AlignmentFlag.AlignVCenter
        self.setTextAlignment(self.h_align | self.v_align)
        self.set_font_size(12)

    def set_align(self, h_align: int, v_align: int) -> None:
        self.setTextAlignment(h_align, v_align)

    def get_style_dict(self) -> dict[str, int | float | str]:
        """
        Получение стилей ячейки в виде словаря
        
        :return: словарь стилей ячейки 
        :rtype: dict[str, int | float | str]
        """
        font = self.font()
        return {'family': font.family(), 
                'size': self.font_size(),
                'h_align': self.h_align,
                'v_align': self.v_align,
                'bold': font.bold(),
                'italic': font.italic(),
                'underline': font.underline()}

    def font_size(self) -> int:
        return self.original_font_size
    
    def set_font_size(self, size: int) -> None:
        self.original_font_size = size
        self.steps_view_font = self.__generate_steps_view_font()
        self.font().setPointSize(size)

    def __generate_steps_view_font(self) -> dict[int, int]:
        dct = {}
        for step in range(self.min_zoom, self.max_zoom + self.step_zoom, self.step_zoom):
            font_size = int(self.original_font_size * step / 100)

            if font_size < self.min_font_size:
                font_size = self.min_font_size
            if step == 100:
                font_size = self.original_font_size 
            dct[step] = font_size
        return dct

    def set_zoom(self, current_zoom_step: int) -> None:
        view_size = self.steps_view_font[current_zoom_step]
        font = self.font()
        font.setPointSizeF(view_size)
        self.setFont(font)