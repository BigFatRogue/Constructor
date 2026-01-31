from PyQt5 import QtCore
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Self
from projects.specification.config.ac_enums import AppContextEnums


_DICT_QT2CSS_ALIGN: dict[QtCore.Qt.AlignmentFlag] = {
    QtCore.Qt.AlignmentFlag.AlignHCenter: 'center',
    QtCore.Qt.AlignmentFlag.AlignLeft: 'left',
    QtCore.Qt.AlignmentFlag.AlignRight: 'rigth',
    QtCore.Qt.AlignmentFlag.AlignTop: 'top',
    QtCore.Qt.AlignmentFlag.AlignVCenter: 'middle',
    QtCore.Qt.AlignmentFlag.AlignBottom: 'bottom'
}


class TypeValueCell(Enum):
    AUTO: str = 'auto'
    NUMBER: str = 'number' 
    TEXT: str = 'text'


class CellFormat(Enum):
    AUTO: str = 'auto'
    NUMBER: str = 'number'
    TEXT: str = 'text'


@dataclass
class DataCell:
    value: int | float | str = ''
    raw_value: str = ''
    type_value: TypeValueCell = TypeValueCell.AUTO 
    
    format_value: CellFormat = CellFormat.AUTO
    count_decimals: int | None = 2
    
    align_h: int = 4
    align_v: int = 128
    font_family: str = 'Arial'
    font_size: int = 12
    bold: bool = False
    italic: bool = False
    underline: bool = False
    color: tuple[int, int, int, int] = (0, 0, 0, 255)
    background: tuple[int, int, int, int] = (255, 255, 255, 255)
    span: tuple[int, int] = (1, 1)

    def __post_init__(self):
        self._validate_value(value=self.value)
        self._set_raw_value(value=self.value)
        
    def _validate_value(self, value: int | float | str):
        """
        Привидение к типу данных. Значения value прихзодящие из таблицы от пользователя
        """

        if isinstance(value, (int, float)):                          
            self.value = value
            self.type_value = TypeValueCell.NUMBER
                        
        elif isinstance(value, str):
            sign = 1
            if value and value[0] == '-':
                sign = -1
                value = value[1:]

            if value.isdigit():
                self.value = int(value) * sign
                self.type_value = TypeValueCell.NUMBER
            else:
                if ',' in value: 
                    try:
                        self.value = float(value.replace(',', '.')) * sign
                        self.type_value = TypeValueCell.NUMBER
                    except Exception:
                        self.value = '-' if sign == -1 else '' + value
                        self.type_value = TypeValueCell.TEXT
                else:
                    self.value = '-' if sign == -1 else '' + value
                    self.type_value = TypeValueCell.TEXT


    def _set_raw_value(self, value: int | float | str) -> None:
        """
        Привидение значения, которое отображается в ячейки таблицы к заданному формату
        """

        if self.format_value == CellFormat.AUTO:
            if self.type_value == TypeValueCell.NUMBER:
                digit = str(self.value)
                if '.' in str(self.value):
                    integer, fractional = str(self.value).split('.')
                    fractional = fractional.rstrip('0')
                    self.raw_value = integer + (f',{fractional}' if fractional else '')
                else:
                     self.raw_value = digit
            else:
                self.raw_value = value

        elif self.format_value == CellFormat.TEXT:
            if isinstance(value, float):
                value = str(value).replace('.', ',')
            self.raw_value = str(value)

        elif self.format_value == CellFormat.NUMBER:
            if self.type_value == TypeValueCell.NUMBER and self.count_decimals is not None:
                self.raw_value = f'{self.value:.{self.count_decimals}f}'.replace('.', ',')
            else:
                self.raw_value = str(self.value)
        else:
            self.raw_value = str(self.value)

    def set_value(self, value: int | float | str) -> None:
        """
        Установка значения value
        """
        self._validate_value(value)
        self._set_raw_value(value)

    def set_format(self, format: CellFormat) -> None:
        """
        Установка значения format
        """
        self.format_value = format
        self._set_raw_value()

    def set_property_from_cell(self, cell: Self) -> None:
        for prop_name, value in cell.__dict__.items():
            self.__dict__[prop_name] = value

    def get_dict_style(self) -> dict[str, int | float| str | bool | tuple[int, ...]]:
        return {
            'type_value': self.type_value.value,
            'format_value': self.format_value.value,
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

    def set_style_from_dict(self, name: str, value: int | float | str | bool | tuple[int, ...]) -> None:
        try:
            if name == 'type_value':
                self.type_value = TypeValueCell(value)
            elif name == 'format_value':
                self.format_value = CellFormat(value)
            else:
                setattr(self, name, value)
        except Exception:
            print('class: DataCell', 'метод: set_style_from_dict')
            print(f'Попытка присвоить: {name}: {value}')
            print()

    def get_td_html(self) -> str:
        """
        Преобразует свойства объекта в тэг td со стилями
        
        :param self: Описание
        :return: Описание
        :rtype: str
        """

        style: dict[str, int | float| str | bool | tuple[int, ...]] = {
            'font-family': self.font_family,
            'font-size': self.font_size,
            'font-weight': 'bold' if self.bold else None,
            'font-style': 'italic' if self.italic else None,
            'text-decoration': 'underline' if self.underline else None,
            'color': self._tuple_color2hex(self.color),
            'background-color': self._tuple_color2hex(self.background),
            'text-align': _DICT_QT2CSS_ALIGN.get(self.align_h),
            'vertical-align': _DICT_QT2CSS_ALIGN.get(self.align_v),
        }
        
        str_style = ''
        for name, prop in style.items():
            if prop is not None:
                str_style += f'{name}: {prop};\n'

        return f'<td style="{str_style}" colspan={self.span[0]} rowspan={self.span[1]}>{self.value}</td>'

    def _tuple_color2hex(self, color: tuple[int, int, int, int]) -> str:
        if color is None or color == (255, 255, 255, 255):
            return 'none'
        return "#{:02X}{:02X}{:02X}".format(*color)

    def get_dict_role_value(self) -> dict[tuple[QtCore.Qt.ItemDataRole, AppContextEnums.PARAMETR_FONT | None] | int | float | str | tuple]:
        return {
            (QtCore.Qt.ItemDataRole.FontRole, AppContextEnums.PARAMETR_FONT.FONT_PARAM_FAMILY): self.font_family,
            (QtCore.Qt.ItemDataRole.FontRole, AppContextEnums.PARAMETR_FONT.FONT_PARAM_SIZE): self.font_size,
            (QtCore.Qt.ItemDataRole.FontRole, AppContextEnums.PARAMETR_FONT.FONT_PARAM_BOLD): self.bold,
            (QtCore.Qt.ItemDataRole.FontRole, AppContextEnums.PARAMETR_FONT.FONT_PARAM_ITALIC): self.italic,
            (QtCore.Qt.ItemDataRole.FontRole, AppContextEnums.PARAMETR_FONT.FONT_PARAM_UNDERLINE): self.underline,
            (QtCore.Qt.ItemDataRole.TextAlignmentRole, None): self.align_h | self.align_v,
            (QtCore.Qt.ItemDataRole.BackgroundColorRole, None): self.background,
            (QtCore.Qt.ItemDataRole.ForegroundRole, None): self.color,
            (QtCore.Qt.ItemDataRole.EditRole, None): self.value
            }

    def get_value_from_role(self, role: QtCore.Qt.ItemDataRole, font_param: AppContextEnums.PARAMETR_FONT = None) -> int | float | str | tuple:
        return self.get_dict_role_value()[(role, font_param)] 

    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return self.__str__()

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


@dataclass
class AppContextDataClasses:
    DATA_CELL = DataCell
    TYPE_VALUE_DATA_CELL = TypeValueCell
    CELL_FORMAT = CellFormat
    DATA_HEADERS = ParameterHeaders
    PARAMETER_TABLE = ParameterTable