from dataclasses import dataclass


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
    CELL_STYLE = CellStyle
    SECTION_STYLE = SectionStyle