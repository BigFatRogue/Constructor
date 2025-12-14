from PyQt5 import QtWidgets, QtCore

from projects.specification.config.app_context.app_context import DATACLASSES


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

        font = self.font()
        font.setFamily('Arial')
        self.setFont(font)
        self.set_font_size(12)

    def get_style(self) -> DATACLASSES.CELL_STYLE:
        """
        Получение стилей ячейки в виде словаря
        
        :return: словарь стилей ячейки 
        :rtype: dict[str, DATACLASSES.CELL_STYLE]
        """
        font = self.font()
        return DATACLASSES.CELL_STYLE(
            row=self.row(),
            column=self.column(),
            font_family = font.family(),
            font_size=self.font_size(),
            bold=font.bold(),
            italic=font.italic(),
            underline=font.underline(),
            align_h = self.textAlignment() & QtCore.Qt.AlignmentFlag.AlignHorizontal_Mask,
            align_v = self.textAlignment() & QtCore.Qt.AlignmentFlag.AlignVertical_Mask)

    def font_size(self) -> int:
        return self.original_font_size
    
    def set_font_size(self, size: int) -> None:
        self.original_font_size = size
        self.steps_view_font = self.__generate_steps_view_font()
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

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