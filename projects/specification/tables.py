from dataclasses import dataclass
from datetime import datetime


@dataclass
class ColumnConfig:
    field: str
    type_data: str
    column_name: str = None

    @property
    def sql_definition(self):
        return f"{self.field} {self.type_data}"


class TableConfig:
    def __init__(self, name: str, columns: list[ColumnConfig]):
        self.name = name
        self.columns = columns
    
    def get_fileds(self) -> tuple[str]:
        return tuple(tp.field for tp in self.columns if tp.field != 'id')

    def get_columns_name(self) -> tuple[str]:
        return tuple(col.column_name for col in self.columns)

    def create_sql(self):
        columns_sql = ", ".join(col.sql_definition for col in self.columns)
        return f"CREATE TABLE IF NOT EXISTS {self.name} ({columns_sql})"


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
            ColumnConfig('diff', 'FLOAT', 'Изменение количества')
        ]
        
        super().__init__(name, columns)

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

    def update_diff(self, name_table_1) -> None:
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
        columns  =[
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