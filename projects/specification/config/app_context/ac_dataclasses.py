from dataclasses import dataclass


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

    # def __str__(self):
    #     return str(self.value)

    # def __repr__(self):
    #     return str(self.value)

@dataclass
class CellStyle:
    row: int
    column: int
    font_family: str
    font_size: int
    bold: bool
    italic: bool
    underline: bool
    align_h: int
    align_v: int


@dataclass
class SectionStyle:
    row: int
    column: int
    size: float
    state_sorted: int = 0


@dataclass
class AppContextDataClasses:
    DATA_CELL = DataCell
    CELL_STYLE = CellStyle
    SECTION_STYLE = SectionStyle