from enum import Enum, auto


class NameTableSQL(Enum):
    NAME_FIELDS = 'name_fields'
    LINKS = 'links'
    PROJECT_PROPERTY = 'project_property'
    SPECIFICATION = 'specification'
    GENERAL = 'specification_general'
    INVENTOR = 'specification_inventor'
    BUY = 'specification_buy'
    PROD = 'specification_prod'


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
    

class TypeBLockPropertyControlPanel(Enum):
    MAIN = auto()
    ALIGN = auto()
    FONT = auto()
    MARGIN = auto()


class TypeSignalFromControlPanel(Enum):
    SAVE = auto()
    SET_ALIGN = auto()
    FONT_FAMILY = auto()
    FONT_SIZE = auto()
    FONT_BOLD = auto()
    FONT_ITALIC = auto()
    FONT_UNDERLINE = auto()