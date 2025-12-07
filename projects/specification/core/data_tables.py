from typing import TypeVar, Sequence, Union, Optional
from datetime import datetime
from sqlite3 import Cursor

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)

    sys.path.append(test_path)

from projects.specification.config.enums import NameTableSQL
from projects.specification.core.database import DataBase
from projects.specification.core.config_table import (
    ColumnConfig,
    TableConfig,
    FIELDS_CONFIG,
    LINK_ITEM_CONFIG,
    PROPERTY_PROJECT_CONFIG,
    SPECIFICATION_CONFIG,
    GENERAL_ITEM_CONFIG,
    INVENTOR_ITEM_CONFIG,
    BUY_ITEM_CONFIG,
    PROD_ITEM_CONFG
)
from projects.specification.core.functions import get_now_time

TDataTable = TypeVar('T', dict, list)
TData = Union[int, float, str, None]


class GeneralDataItem:
    def __init__(self, database: DataBase):
        self.database = database
        if self.database.conn:
            self._filepath_db: str = self.database.filepath
        else:
            self._filepath_db: str = None
        
        self.data: TDataTable = None
        self.config: TableConfig = None

    def get_data(self) -> TDataTable:
        return self.data
    
    def set_data(self, data: TDataTable):
        self.data = data
    
    def check_connect(self) -> bool:
        if self.database:
            if self.database.conn is None:
                if self._filepath_db:
                    self.database.connect(self._filepath_db)
                else:
                    return False
            return True
        return False
    
    def set_filepath_db(self, filepath: str) -> None:
        self._filepath_db = filepath

    def get_filepath(self) -> str:
        return self._filepath_db

    def execute_sql(self, query: str, *args, **kwargs) -> Cursor:
        if self.database:
            return self.database.cur.execute(query, *args, **kwargs)

    def create_sql(self) -> None:
        if not self.check_connect():
            return
    
    def insert_sql(self) -> None:
        if not self.check_connect():
            return 
    
    def update_sql(self) -> None:
        if not self.check_connect():
            return 

    def select_sql(self) -> Optional[TDataTable]:
        if not self.check_connect():
            return 
    
    def commit_sql(self) -> None:
        if self.database:
            self.database.commit()

    def close_sql(self) -> None:
        if self.database:
            self.database.close()
    

class PropertyProjectData(GeneralDataItem):
    def __init__(self):
        database = DataBase()
        super().__init__(database)
        self.config: TableConfig = PROPERTY_PROJECT_CONFIG
        self.data: dict[str, str] = {}

    def create_sql(self):
        super().create_sql()
        columns_sql = ", ".join(col.sql_definition for col in self.config.columns)
        self.execute_sql(f"CREATE TABLE IF NOT EXISTS {self.config.name} ({columns_sql})")
        self.commit_sql()

    def insert_sql(self):
        super().insert_sql()
        str_values = ', '.join(['?' for _ in range(len(self.data))])
        str_fields = ', '.join([field for field in self.data.keys()])
        self.execute_sql(f'INSERT INTO {self.config.name} ({str_fields}) VALUES({str_values})', [v for v in self.data.values()])
        self.commit_sql()

    def update_sql(self):
        super().update_sql()        
        str_values = ', '.join([f'{key} = ?' for key in self.data.keys()])
        self.execute_sql(f'UPDATE {self.config.name} SET {str_values} WHERE id=1', list(self.data.values()))
        self.commit_sql()

    def select_sql(self):
        super().select_sql()
        view_fields = self.config.get_view_fields()
        str_fields = ', '.join(view_fields)
        res = self.execute_sql(f'SELECT {str_fields} FROM {self.config.name}').fetchall()
        data = {}
        if res:
            data = {k: v for k, v in zip(view_fields, res[0])}
        return data

    def get_all_specification_data(self) -> list[dict[str, Union[str, list[list[TData]]]]]:
        if not self.check_connect():
            return 
    
        if SPECIFICATION_CONFIG.name not in self.database.get_exist_tables():
            return
        
        columns = SPECIFICATION_CONFIG.columns
        query = f"SELECT * FROM {SPECIFICATION_CONFIG.name}"
        eixst_table_sql = self.execute_sql(query).fetchall()

        tables = []
        for row in eixst_table_sql:
            table: dict[str, Union[str, list[list[TData]]]] = {}
            for col, value in zip(columns, row):
                table[col.field] = value
            
            query = f"""
            SELECT * 
            FROM {NameTableSQL.GENERAL.value} 
            LEFT JOIN {table['type_spec']} ON {table['type_spec']}.parent_id = {NameTableSQL.GENERAL.value}.id 
            WHERE {NameTableSQL.GENERAL.value}.parent_id = {table['id']}
            ORDER BY number_row
            """

            data = [list(row) for row in self.execute_sql(query).fetchall()]
            table['data'] = data
            tables.append(table)
        return tables


class SpecificationDataItem(GeneralDataItem):
    def __init__(self, database):
        super().__init__(database)
        self.specification_config: TableConfig = SPECIFICATION_CONFIG
        self.config: TableConfig = GENERAL_ITEM_CONFIG
        self.unique_config: TableConfig = None
        self.fields_config: TableConfig = FIELDS_CONFIG
        self.data: list[list[TData]] = None
        self.type_spec: NameTableSQL = None
        self.sid: int = None

    def __insert_in_sql_filed(self) -> None:
        if not self.check_connect():
            return

        columns_sql = ", ".join(col.sql_definition for col in self.fields_config.columns)
        self.execute_sql(f"CREATE TABLE IF NOT EXISTS {self.fields_config.name} ({columns_sql})")
        
        fields = tuple(col.field for col in self.fields_config.columns if not col.is_id)
        str_fields = ', '.join(fields)

        for config in (self.config, self.unique_config):
            for column in config.columns:
                if not column.is_id:
                    values = tuple(getattr(column,  field) for field in fields if hasattr(column, field))
                    count_values = ', '.join(['?'] * len(values))
                    self.execute_sql(f"INSERT INTO {self.fields_config.name} ({str_fields}) VALUES({count_values})", values)

    def create_sql(self) -> None:
        super().create_sql()

        for config in (self.specification_config, self.config, self.unique_config):
            if config:
                columns_sql = ", ".join(col.sql_definition for col in config.columns + config.columns_property)
                self.execute_sql(f"CREATE TABLE IF NOT EXISTS {config.name} ({columns_sql})")
        
        self.__insert_specification_sql(self.type_spec)
        self.__insert_in_sql_filed()
        self.commit_sql()
        
    def __insert_specification_sql(self, type_spec: NameTableSQL) -> None:
        field_sql = tuple(col.field for col in self.specification_config.columns if not col.is_id)
        field_str = ', '.join(field_sql)
        values_str = ', '.join(['?'] * len(field_sql))
        
        now_str = get_now_time()

        self.execute_sql(f"INSERT INTO {self.specification_config.name} ({field_str}) VALUES({values_str})", (type_spec.value, now_str, now_str))
        self.sid = self.execute_sql('SELECT last_insert_rowid();').fetchall()[0][0]
    
    def insert_sql(self) -> None:
        super().insert_sql()

        for row in self.data:
            start = 0
            for config in (self.config, self.unique_config):
                if config:
                    len_config_without_foreign_key = len(config.columns)
                    part_row = row[start: start + len_config_without_foreign_key]
                    start = len_config_without_foreign_key

                    fields = tuple(col.field for col in config.columns if not col.is_id)
                    str_fields = ', '.join(fields)
                    str_values = ', '.join(['?'] * len(fields))

                    part_data_row = [data for data, col in zip(part_row, config.columns) if not col.is_id]
                    
                    self.execute_sql(f'INSERT INTO {config.name} ({str_fields}) VALUES({str_values})', part_data_row)
                    if config.parent_config:
                        last_id = self.execute_sql('SELECT last_insert_rowid();').fetchall()[0][0]
                        parent_id = self.sid if config == self.config else last_id
                        self.__set_foreign_key(config, last_id=last_id, parent_id=parent_id)
        
        self.commit_sql()

    def __set_foreign_key(self, config: TableConfig, last_id:int, parent_id: int) -> None:
        field_foreign_key = config.get_foreign_field()
        
        if field_foreign_key:       
            self.execute_sql(f"UPDATE {config.name} SET {field_foreign_key} = '{parent_id}' WHERE id={last_id}")

    def update_sql(self):
        super().update_sql()
        str_values = [', '.join([f'{col.field} = ?' for col in config.columns]) for config in (self.config, self.unique_config)]
        
        index_config = (0, len(self.config.columns))
        index_unique = (index_config[1], index_config[1] + len(self.unique_config.columns))
        
        for row in self.data:
            for name, str_value, index in zip((self.config.name, self.unique_config.name), 
                                              str_values, 
                                              (index_config, index_unique)):
                
                index_start, index_end = index
                data = row[index_start: index_end]

                self.execute_sql(f'UPDATE {name} SET {str_value} WHERE id={data[0]}', data)
        self.commit_sql()
        
    def get_index_form_name_filed(self, field: str) -> int:
        for i, col in enumerate(self.config.columns + self.unique_config.columns):
            if col.field == field:
                return i
        return -1 


class InventorSpecificationDataItem(SpecificationDataItem):
    def __init__(self, database):
        super().__init__(database)
        self.type_spec = NameTableSQL.INVENTOR
        self.unique_config = INVENTOR_ITEM_CONFIG


class BuySpecificationDataItem(SpecificationDataItem):
    def __init__(self, database):
        super().__init__(database)
        self.type_spec = NameTableSQL.BUY
        self.unique_config = BUY_ITEM_CONFIG


class ProdSpecificationDataItem(SpecificationDataItem):
    def __init__(self, database):
        super().__init__(database)
        self.type_spec = NameTableSQL.PROD
        self.unique_config = PROD_ITEM_CONFG


if __name__ == '__main__':
    import os
    from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx

    pp_data = PropertyProjectData()
    pp_data.set_filepath_db(os.path.join(os.getcwd(), '_data.scdata'))
    database = pp_data.database
    pp_data.create_sql()
    pp_data_dict = {
        'file_name': 'Проект 1',
        'project_name': 'ЛебедяньМолоко',
        'project_number': r'1642/24',
        'number_contract': '3.2',
        'manager': None,
        'technologist': None,
        'constructor': None,
        'name_model': None,
        'name_drawing': None
    }
    pp_data.set_data(pp_data_dict)
    pp_data.insert_sql()
    

    inv_data = InventorSpecificationDataItem(database)
    inv_data.create_sql()
    
    path_xlsx = r'D:\Python\AlfaServis\Constructor\projects\specification\DEBUG\ALS.1642.5.3.05.01.00.000 - Инвентор.xlsx'
    data = get_specifitaction_inventor_from_xlsx(path_xlsx)

    inv_data.set_data(data)
    inv_data.insert_sql()

    # buy_data = BuySpecificationDataItem(database)
    # buy_data.create_sql()

    # tables = pp_data.get_all_specification_data()
    # print(tables)


