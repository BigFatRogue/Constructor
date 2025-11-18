from dataclasses import dataclass
from datetime import datetime
from typing import Any
from sqlite3 import Cursor


@dataclass
class ColumnConfig:
    field: str
    type_data: str
    column_name: str = ''
    mode_column_name: str = ''

    @property
    def sql_definition(self):
        return f"{self.field} {self.type_data}"


class TableConfig:
    def __init__(self, name: str, columns: list[ColumnConfig]):
        self.name = name
        self.columns = columns
        self.data: dict = {}
    
    def get_fileds(self) -> tuple[str]:
        return tuple(tp.field for tp in self.columns if tp.field != 'id')

    def get_columns_name(self) -> tuple[str]:
        return tuple(col.column_name for col in self.columns)

    def create_sql(self, cur: Cursor):
        columns_sql = ", ".join(col.sql_definition for col in self.columns)
        cur.execute(f"CREATE TABLE IF NOT EXISTS {self.name} ({columns_sql})")
    
    def insert_sql(self, cur: Cursor) -> None:
        ...
    
    def select_sql(self, cur: Cursor) -> None:
        ...
    
    def update_sql(self, cur: Cursor) -> None:
        ...


class TableConfigPropertyProject(TableConfig):
    def __init__(self):
        name = 'property_project'

        columns = [
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
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
        ]
        self.data: dict[str, str]
        super().__init__(name, columns)
    
    def insert_sql(self, cur):
        str_values = ', '.join(['?' for _ in range(len(self.data))])
        str_fields = ', '.join([field for field in self.data.keys()])
        cur.execute(f'INSERT INTO {self.name} ({str_fields}) VALUES({str_values})', [v for v in self.data.values()])
    
    def update_sql(self, cur):
        str_values = ', '.join([f'{key} = ?' for key in self.data.keys()])
        cur.execute(f'UPDATE  {self.name} SET {str_values} WHERE id=1', list(self.data.values()))

    def select_sql(self, cur) -> dict[str, str]:
        str_fields = ', '.join(self.get_fileds())
        res = cur.execute(f'SELECT {str_fields} FROM {self.name}').fetchall()
        data = {}
        if res:
            data = {k: v for k, v in zip(self.get_fileds(), res[0])}
        return data


class TableConfigInventor(TableConfig):
    def __init__(self):
        name = self.__set_name()
        columns = [
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            ColumnConfig('articul', 'TEXT', 'Инвентарный номер'),
            ColumnConfig('description', 'TEXT', 'Описание'),
            ColumnConfig('specifications', 'TEXT', 'Технические характеристики'),
            ColumnConfig('quantity', 'REAL', 'КОЛ.'),
            ColumnConfig('unit', 'TEXT', 'Единичная величина'),
            ColumnConfig('material', 'TEXT', 'Материал'),
            ColumnConfig('name', 'TEXT', 'Обозначение'),
            ColumnConfig('groups', 'TEXT', 'Раздел'),
            ColumnConfig('diff', 'REAL', 'Изменение количества')
        ]
        
        super().__init__(name, columns)

        # Индексы для сортировки значений в таблицы и формирования ключей 
        self.index_keys: tuple[int] = (1, 2, 3, 6, 7, 8)
        self.index_values: tuple[int] = (4, 5)
        self.list_ignore_field = ('id', 'diff')
    
    def __set_name(self) -> str:
        now = datetime.now()
        now_str = f'{now.hour}_{now.minute}_{now.day}_{now.month}_{now.year}'
        return f'inv_{now_str}'

    def get_fileds(self, is_ignore=False) -> tuple[str]:
        list_ignore = self.list_ignore_field if is_ignore else tuple()
        return tuple(tp.field for tp in self.columns if tp.field not in list_ignore)

    def update_diff(self, name_table_1) -> str:
        f"""UPDATE {self.name} as t2
            SET diff = quantity - (
            SELECT t1.quantity
            FROM {name_table_1} as t1
            WHERE t1.articul = t2.articul
            AND t1.specifications = t2.specifications
            AND t1.description = t2.description
            AND t1.material = t2.material
            AND t1.name = t2.name)"""


class TableConfigBuy(TableConfig):
    def __init__(self, name, columns):
        name='table_buy', 
        columns = [
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            ColumnConfig('articul', 'TEXT', 'Инвентарный номер'),
            ColumnConfig('description', 'TEXT', 'Описание'),
            ColumnConfig('specifications', 'TEXT',  'Технические характеристики'),
            ColumnConfig('diametr', 'TEXT', 'Номинальный диаметр'),
            ColumnConfig('manufactureretr', 'TEXT', 'Производитель'),
            ColumnConfig('count', 'REAL', 'КОЛ.'),
            ColumnConfig('unit', 'TEXT', 'Единичная величина'),
            ColumnConfig('material', 'TEXT', 'Материал'),
            ColumnConfig('note', 'TEXT', 'Примечание'),
            ColumnConfig('invoice', 'TEXT', 'Счёт ОМТС'),
            ColumnConfig('ikey', 'TEXT')
        ]
        super().__init__(name, columns)


class TableConfigProd(TableConfig):
    def __init__(self, name, columns):
        name='table_prod', 
        columns=[
            ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            ColumnConfig('articul', 'TEXT', 'Инвентарный номер'),
            ColumnConfig('description', 'TEXT', 'Описание'),
            ColumnConfig('specifications', 'TEXT',  'Технические характеристики'),
            ColumnConfig('diametr', 'TEXT', 'Номинальный диаметр'),
            ColumnConfig('manufactureretr', 'TEXT', 'Производитель'),
            ColumnConfig('count', 'REAL', 'КОЛ.'),
            ColumnConfig('unit', 'TEXT', 'Единичная величина'),
            ColumnConfig('material', 'TEXT', 'Материал'),
            ColumnConfig('note', 'TEXT', 'Примечание'),
            ColumnConfig('ikey', 'TEXT')
    ]
        super().__init__(name, columns)


if __name__ == '__main__':
    TableConfigInventor()
    # print(INVENTORY_TABLE.name)