from typing import TypeVar, Sequence, Union, Optional
from dataclasses import dataclass
from sqlite3 import Cursor

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)

    sys.path.append(test_path)

from projects.specification.core.database import DataBase


TDataTable = TypeVar('T', dict, tuple, list)


@dataclass
class ColumnConfig:
    field: str
    type_data: str
    column_name: str = ''
    mode_column_name: str = ''
    is_view: bool = True
    is_link: bool = False
    is_id: bool = False
    is_foreign_key: bool = False
    is_calc: bool = False
    
    @property
    def sql_definition(self) -> str:
        return f"{'' if self.is_foreign_key else self.field} {self.type_data}"


TColumns = Union[Sequence[ColumnConfig]]


class TableConfig():
    def __init__(self, name: str, columns: TColumns, database: DataBase, parent_config=None):
        self.name = name
        self.columns = columns
        self.database = database
        self.parent_config = parent_config
    
    def get_fileds(self) -> tuple[str]:
        '''Получение полений таблицы без или с id'''
        return tuple(col.field for col in self.columns)

    def get_columns_name(self) -> tuple[str]:
        return tuple(col.column_name for col in self.columns)

class LinkItemConfig(TableConfig):
    def __init__(self, database: DataBase):
        name = 'links'
        columns = (
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            ColumnConfig('element_1', 'INTEGER'),
            ColumnConfig('element_2', 'INTEGER'),
        )
        super().__init__(name, columns, database)


class PropertyProjectConfig(TableConfig):
    def __init__(self, database: DataBase):
        name = 'project_property'
        columns = (
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_view=False),
            ColumnConfig('file_name', 'TEXT', 'Название файла', ' <span style=color:red;>*</span>'),
            ColumnConfig('project_name', 'TEXT', 'Обозначение проекта'),
            ColumnConfig('project_number', 'TEXT', 'Номер проекта', ' <span style=color:red;>*</span>'),
            ColumnConfig('number_contract', 'TEXT', 'Пункт договора'),
            ColumnConfig('address', 'TEXT', 'Адрес объекта'),
            ColumnConfig('manager', 'TEXT', 'Руководитель проекта'),
            ColumnConfig('technologist', 'TEXT', 'Инженер-технолог'),
            ColumnConfig('constructor', 'TEXT', 'Инженер-конструктор'),
            ColumnConfig('name_model', 'TEXT', 'Модель установки'),
            ColumnConfig('name_drawing', 'TEXT', 'Обозначение чертежа'),
        )

        super().__init__(name, columns, database)
    

class SpecificationConfig(TableConfig):
    def __init__(self, database: DataBase):
        name = 'specification'
        columns = (
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
            ColumnConfig('type_spec', 'TEXT'),
            ColumnConfig('name_spec', 'TEXT'),
            ColumnConfig('datetime', 'TEXT'),
        )
        super().__init__(name, columns, database)


class GeneralItemConfig(TableConfig):
    def __init__(self, database: DataBase, parent_config: Optional[TableConfig]=None):
        name = 'general_specification'
        columns = (
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
            ColumnConfig('number_row', 'INTEGER', is_view=False),
            ColumnConfig('articul', 'TEXT', 'Инвентарный номер'),
            ColumnConfig('description', 'TEXT', 'Описание'),
            ColumnConfig('specifications', 'TEXT', 'Технические характеристики'),
            ColumnConfig('quantity', 'REAL', 'КОЛ.'),
            ColumnConfig('unit', 'TEXT', 'Единичная величина'),
            ColumnConfig('material', 'TEXT', 'Материал'),
            ColumnConfig('parent_id', 'INTEGER', is_calc=True, is_view=True),
            ColumnConfig('parent_id', f'FOREIGN KEY (parent_id) REFERENCES {parent_config.name} ON UPDATE CASCADE ON DELETE CASCADE', is_foreign_key=True),
        )
        super().__init__(name, columns, database, parent_config)


class InventorItemConfig(TableConfig):
    def __init__(self, database: DataBase, parent_config: Optional[TableConfig]=None):
        name = 'inv_specification'
        columns = (
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
            ColumnConfig('name', 'TEXT', 'Обозначение'),
            ColumnConfig('groups', 'TEXT', 'Раздел'),
            ColumnConfig('diff', 'REAL', 'Изменение количества'),
            ColumnConfig('parent_id', 'INTEGER', is_calc=True, is_view=False),
            ColumnConfig('parent_id', f'FOREIGN KEY (parent_id) REFERENCES {parent_config.name} ON UPDATE CASCADE ON DELETE CASCADE', is_foreign_key=True),
        )
        super().__init__(name, columns, database, parent_config)



class BuyItemConfig(TableConfig):
    def __init__(self, database: DataBase, parent_config: Optional[TableConfig]=None):
        name = 'buy_specification'
        columns = (
            ColumnConfig('diametr', 'TEXT', 'Номинальный диаметр'),
            ColumnConfig('manufactureretr', 'TEXT', 'Производитель'),
            ColumnConfig('note', 'TEXT', 'Примечание'),
            ColumnConfig('invoice', 'TEXT', 'Счёт ОМТС'),
            ColumnConfig('link', 'BOOLEAN', 'Связь', is_link=True),
            ColumnConfig('parent_id', 'INTEGER', is_calc=True, is_view=False),
            ColumnConfig('parent_id', f'FOREIGN KEY (parent_id) REFERENCES {parent_config.name} ON UPDATE CASCADE ON DELETE CASCADE', is_foreign_key=True),
        )
        super().__init__(name, columns, database, parent_config)


class ProdItemConfig(TableConfig):
    def __init__(self, database: DataBase, parent_config: Optional[TableConfig]=None):
        name = 'prod_specification'
        columns = (
            ColumnConfig('number_prod', 'INTEGER', '№'),
            ColumnConfig('diametr', 'TEXT', 'Номинальный диаметр'),
            ColumnConfig('manufactureretr', 'TEXT', 'Производитель'),
            ColumnConfig('note', 'TEXT', 'Примечание'),
            ColumnConfig('invoice', 'TEXT', 'Счёт ОМТС'),
            ColumnConfig('link', 'BOOLEAN', 'Связь', is_link=True),
            ColumnConfig('parent_id', 'INTEGER',is_view=False),
            ColumnConfig('parent_id', f'FOREIGN KEY (parent_id) REFERENCES {parent_config.name} ON UPDATE CASCADE ON DELETE CASCADE', is_foreign_key=True),
        )
        super().__init__(name, columns, database, parent_config)
