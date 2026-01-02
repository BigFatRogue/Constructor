from dataclasses import dataclass
from enum import Enum

@dataclass
class DataCell:
    value: int | float | str | None = None
    align_h: int = 4
    align_v: int = 128
    font_family: str = 'Arial'
    font_size: int = 12
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: tuple[int, int, int, int] = (0, 0, 0, 255)
    background: tuple[int, int, int, int] = None
    span: tuple[int, int] = (1, 1)

    def get_dict_style(self) -> dict[str, int | float| str | bool | tuple[int, ...]]:
        return {
            'align_h': self.align_h,
            'align_v': self.align_v,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'bold': self.bold,
            'italic': self.italic,
            'underline': self.underline,
            'color': self.color,
            'background': self.background,
            'span': self.span,
        }


class ParameterTable:
    def __init__(self, active_range: tuple[int, int, int, int], current_zoom: int, scroll_x: int, scroll_y: int):
        self.active_range = active_range
        self.current_zoom = current_zoom
        self.scroll_x = scroll_x
        self.scroll_y = scroll_y

    def get_dict_data(self) -> dict[str, int | tuple[int, int, int, int]]:
        return {
            'active_range': self.active_range,
            'current_zoom': self.current_zoom,
            'scroll_x': self.scroll_x,
            'scroll_y': self.scroll_y
        }

    def __str__(self) -> str:
        return f'{self.get_dict_data()=}'
    
    def __repr__(self) -> str:
        return self.__str__()

class ParameterHeaders:
    """
    Хранит параметры секции заголовка

    parameter содержит дополнительные уникальные свойства для кастомных заголовков
    """
    def __init__(self, row: int = None, column: int = None, size: int = None, is_view: bool = True, parameters: dict[str, str | int | float | bool] = None):
        self.row = row
        self.column = column
        self.size = size
        self.is_view = is_view
        self.parameters = {} if parameters is None else parameters

    def get_dict_data(self) -> list[str | int | float | bool]:
        parameters = {}
        for key, value in self.parameters.items():
            if isinstance(value, Enum):
                value = value.value
            parameters[key] = value
        return {'row': self.row, 'column': self.column, 'size': self.size, 'is_view': self.is_view, 'parameters': parameters}

    def __str__(self):
        return f'{self.row=}, {self.column=}, {self.size=}, {self.is_view=}, {self.parameters=}'
    
    def __repr__(self):
        return self.__str__()

@dataclass
class AppContextDataClasses:
    DATA_CELL = DataCell
    DATA_HEADERS = ParameterHeaders
    PARAMETER_TABLE = ParameterTable