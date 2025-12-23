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

    def get_dcit_style(self) -> dict[str, int | float| str | bool | tuple[int, ...]]:
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


@dataclass
class SectionStyle:
    row: int
    column: int
    size: float
    state: int = 0


@dataclass
class AppContextDataClasses:
    DATA_CELL = DataCell
    SECTION_STYLE = SectionStyle