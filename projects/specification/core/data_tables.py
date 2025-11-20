from typing import TypeVar, Sequence, Union, Optional
from datetime import datetime
from sqlite3 import Cursor

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)

    sys.path.append(test_path)

from projects.specification.config.enums import TypeSpecificationDataItem
from projects.specification.core.database import DataBase
from projects.specification.core.config_table import (
    TDataTable,
    ColumnConfig, 
    LinkItemConfig,
    PropertyProjectConfig,
    SpecificationConfig, 
    GeneralItemConfig,
    InventorItemConfig,
    BuyItemConfig
    )


TConfig = TypeVar('T', GeneralItemConfig, PropertyProjectConfig, InventorItemConfig)


class GeneralDataItem:
    def __init__(self, database: DataBase):
        self.database = database
        if self.database.conn:
            self._filepath_db: str = self.database.filepath
        else:
            self._filepath_db: str = None
        
        self.data: TDataTable = None
        self.config: TConfig = None

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
    def __init__(self, database):
        super().__init__(database)
        self.config = PropertyProjectConfig(database)
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

    def update_sql(self):
        super().update_sql()        
        str_values = ', '.join([f'{key} = ?' for key in self.data.keys()])
        self.execute_sql(f'UPDATE  {self.config.name} SET {str_values} WHERE id=1', list(self.data.values()))
        self.commit_sql()

    def select_sql(self):
        super().select_sql()
        str_fields = ', '.join(self.config.get_fileds())
        res = self.execute_sql(f'SELECT {str_fields} FROM {self.config.name}').fetchall()
        data = {}
        if res:
            data = {k: v for k, v in zip(self.config.get_fileds(), res[0])}
        return data


class SpecificationDataItem(GeneralDataItem):
    def __init__(self, database):
        super().__init__(database)
        self.specification_config = SpecificationConfig(database)
        self.config = GeneralItemConfig(database, parent_config=self.specification_config)
        self.unique_config = None
        self.data: list[list[Union[int, float, str, None]]] = None
        self.type_spec: TypeSpecificationDataItem = None
        self.sid: int = None

    def create_sql(self) -> None:
        if not self.check_connect():
            return
        
        for config in (self.specification_config, self.config, self.unique_config):
            if config:
                columns_sql = ", ".join(col.sql_definition for col in config.columns)
                self.execute_sql(f"CREATE TABLE IF NOT EXISTS {config.name} ({columns_sql})")
        
        self.__insert_specification_sql(self.type_spec)
        self.commit_sql()
        
    def __insert_specification_sql(self, type_spec: TypeSpecificationDataItem) -> None:
        field_sql = tuple(col.field for col in self.specification_config.columns if not col.is_id)
        field_str = ', '.join(field_sql)
        values_str = ', '.join(['?'] * len(field_sql))
        
        now = datetime.now()
        now_str = f'{now.day:02}.{now.month:02}.{now.year}_{now.hour:02}:{now.minute:02}:{now.second:02}'

        self.execute_sql(f"INSERT INTO {self.specification_config.name} ({field_str}) VALUES({values_str})", (type_spec.value, now_str, now_str))
        self.sid = self.execute_sql('SELECT last_insert_rowid();').fetchall()[0][0]
    
    def insert_sql(self) -> None:
        super().insert_sql()

        for row in self.data:
            start = 0
            for config in (self.config, self.unique_config):
                if config:
                    field = tuple(col.field for col in config.columns if not any((col.is_id, col.is_foreign_key, col.is_calc)))
                    str_field = ', '.join(field)
                    str_values = ', '.join(['?'] * len(field))

                    part_row = row[start: start + len(field)]
                    start = len(field)

                    self.execute_sql(f'INSERT INTO {config.name} ({str_field}) VALUES({str_values})', part_row)
                    if config.parent_config:
                        last_id = self.execute_sql('SELECT last_insert_rowid();').fetchall()[0][0]
                        parent_id = self.sid if config == self.config else last_id
                        self.__set_foreign_key(config, last_id=last_id, parent_id=parent_id)
        
        self.commit_sql()

    def __set_foreign_key(self, config: Union[GeneralDataItem, InventorItemConfig], last_id:int, parent_id: int) -> None:
        field_foreign_key = None
        for col in config.columns:
            if col.is_foreign_key:
                field_foreign_key = col.field
                break
        
        if field_foreign_key:       
            self.execute_sql(f"UPDATE {config.name} SET {field_foreign_key} = '{parent_id}' WHERE id={last_id}")


class InventorSpecificationDataItem(SpecificationDataItem):
    def __init__(self, database):
        super().__init__(database)
        self.type_spec = TypeSpecificationDataItem.INVENTOR
        self.unique_config = InventorItemConfig(database, parent_config=self.config)


class BuySpecificationDataItem(SpecificationDataItem):
    def __init__(self, database):
        super().__init__(database)
        self.type_spec = TypeSpecificationDataItem.BUY
        self.unique_config = BuyItemConfig(database, parent_config=self.config)

if __name__ == '__main__':
    import os

    database = DataBase()
    
    inv_data = InventorSpecificationDataItem(database)
    inv_data.set_filepath_db(os.path.join(os.getcwd(), '_pp_data.scdata'))
    inv_data.create_sql()
    inv_data.set_data([
        [1, 'Арт. 1', 'Бетон', "2х2х2", "2", "шт.", "AISI304", "ALS.000.01", "Арматура", 0],
        [2, 'Арт. 2', 'Картон', "11х12х32", "10", "шт.", "AISI304", "ALS.000.02", "Арматура", 0]
        ])
    inv_data.insert_sql()

    buy_data = BuySpecificationDataItem(database)
    buy_data.create_sql()


