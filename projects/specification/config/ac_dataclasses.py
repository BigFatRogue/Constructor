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
    color: tuple[int, int, int, int] = None
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
    def __init__(self, active_range: tuple[int, int, int, int], current_zoom: int):
        self.active_range = active_range
        self.current_zoom = current_zoom

    def get_dict_active_range(self) -> dict[str, int]:
        return {
            'top': self.active_range[0],
            'left': self.active_range[1],
            'bottom': self.active_range[2],
            'rigth': self.active_range[3]
        }

    def __str__(self) -> str:
        return f'{self.active_range=}, {self.current_zoom=}'
    
    def __repr__(self) -> str:
        return self.__str__()

class ParameterHeaders:
    """
    Хранит параметры секции заголовка

    parameter содержит дополнительные уникальные свойства для кастомных заголовков
    """
    def __init__(self, row: int = None, column: int = None, size: int = None, is_view: bool = True, parameters: dict[str, str | int | float | bool] = {}):
        self.row = row
        self.column = column
        self.size = size
        self.is_view = is_view
        self.parameters = parameters

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