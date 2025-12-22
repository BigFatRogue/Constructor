from enum import Enum, auto
from dataclasses import dataclass
from PyQt5 import QtCore


class NameTableSQL(Enum):
    NAME_FIELDS = 'name_fields'
    LINKS = 'links'
    PROJECT_PROPERTY = 'project_property'
    SPECIFICATION = 'specification'
    GENERAL = 'specification_general'
    INVENTOR = 'specification_inventor'
    BUY = 'specification_buy'
    PROD = 'specification_prod'
    STYLE_CELL = 'style_cell'
    STYLE_SECTION = 'style_section'
    STYLE_CELL_LINK = 'style_cell_link'
    STYLE_SPECEFICATION = 'style_specefication'


class TypeTreeItem(Enum):
    PROJET = auto()
    SPEC_FOLDER_INV = auto()
    SPEC_FOLDER_BUY = auto()
    SPEC_FOLDER_PROD = auto()
    TABLE_INV = auto()
    TABLE_BUY = auto()
    TABLE_PROD = auto()


class TypeCreateLoadSpec(Enum):
    LOAD_SPEC_FROM_XLSX = auto()
    LOAD_SPEC_FROM_ACTIVE_INV = auto()
    CREATE_SPEC_BUY_FROM_SPEC_INV = auto()
    CERATE_SPEC_BUY_EMPTY = auto()
    CREATE_SPEC_PROD_FROM_SPEC_BUY = auto()
    CREATE_SPEC_PROD_FROM_SPEC_INV = auto()
    CREATE_SPEC_PROD_EMPTY = auto()


class EnumStatusBar(Enum):
    WAIT = 'Ожидание...'
    PROJECT_LOAD = 'Проект загружен'
    PROJECT_SAVE = 'Проект сохранён'
    PROJECT_EXIST = 'Проект уже добавлен'
    SPECIFICATION_LOAD = 'Спецификация загружена'


class TypeAlignText(Enum):
    H_ALIGN = auto()
    V_ALIGN = auto()


class StateSortedColumn(Enum):
    SORTED = 1
    REVERSE = -1
    EMPTY = 0
    

class TypeBlockPropertyControlPanel(Enum):
    FONT = auto()
    ALIGN = auto()
    MARGIN = auto()


class TypeSignalFromControlPanel(Enum):
    SAVE = auto()
    SET_ALIGN = auto()
    FONT_FAMILY = auto()
    FONT_SIZE = auto()
    FONT_BOLD = auto()
    FONT_ITALIC = auto()
    FONT_UNDERLINE = auto()


class Constants(Enum):
    MY_FORMAT = 'scdata'
    QROLE_LINK_ITEM_WIDGET_TREE = QtCore.Qt.UserRole + 1
    QROLE_DATA_X = QtCore.Qt.UserRole + 2
    QROLE_V_TEXT_ALIGN = QtCore.Qt.UserRole + 3
    QROLE_H_TEXT_ALIGN = QtCore.Qt.UserRole + 4


@dataclass
class AppContextEnums:
    NAME_TABLE_SQL = NameTableSQL
    TYPE_TREE_ITEM = TypeTreeItem
    TYPE_CREATE_LOAD_SPEC = TypeCreateLoadSpec
    STATUS_BAR = EnumStatusBar
    TYPE_ALIGN_TEXT = TypeAlignText
    STATE_SORTED_COLUMN = StateSortedColumn
    TYPE_BLOCK_PROPERTY_CONTROL_PANEL = TypeBlockPropertyControlPanel
    TYPE_SIGNAL_FROM_CONTROL_PANEL = TypeSignalFromControlPanel
    CONSTANTS = Constants
    