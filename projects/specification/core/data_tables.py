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
    def __init__(self):
        self.database: DataBase = None        
        self.data: TDataTable = None
        self.config: TableConfig = None
        self.__is_init: bool = False
        self.__is_save: bool = False

    def get_data(self) -> TDataTable:
        return self.data
    
    def set_data(self, data: TDataTable):
        self.data = data
    
    @property
    def is_init(self) -> bool:
        return self.__is_init

    def set_is_init(self, value: bool) -> True:
        self.__is_init = value

    @property
    def is_save(self) -> bool:
        return self.__is_save

    def set_is_save(self, value: bool) -> True:
        self.__is_save = value

    def save(self) -> None:
        """
        Docstring для load

        Сохранение self.data в БД для save

        :return:
        """
        ...

    def load(self) -> TDataTable | None:
        """
        Docstring для load

        Загрузка data из БД
        
        :return: dict для свойств проекта и list для спецификаций
        :rtype: dict | list | None
        """
        ...

    def update(self) -> None:
        """
        Docstring для update
        Обновление данных из self.data в БД
        
        :param: Описание
        """
        ...

    def get_filepath(self) -> str:
        return '' if self.database is None else self.database.filepath

    def __create_sql(self) -> None:
        ...
    
    def __insert_sql(self) -> None:
        ...
    
    def __update_sql(self) -> None:
        ...

    def __select_sql(self) -> TDataTable | None:
        ... 
    
    
class PropertyProjectData(GeneralDataItem):
    def __init__(self):
        super().__init__()
        self.config: TableConfig = PROPERTY_PROJECT_CONFIG
        self.data: dict[str, str] = {}

    def save(self, filepath: str = None) -> None:
        if self.database is None:
            if filepath:
                self.database = DataBase(filepath) 
            else:
                raise SystemError('Необходимо передать filepath')

        if not self.is_init:
            self.__create_sql()
            self.__insert_sql()
        else:
            self.__update_sql()
        
        self.database.commit()
        self.database.close()

    def load(self, filepath: str)-> list[dict[str, str | list[list[TData]]]]:
        if self.database is None:
            if filepath:
                self.database = DataBase(filepath) 
            else:
                raise SystemError('Необходимо передать filepath')

        self.set_data(self.__select_sql())
        tables = self.__get_all_specification_data()
        self.set_is_init(True)
        self.database.close()

        return tables
  
    def __create_sql(self):
        columns_sql = ", ".join(col.sql_definition for col in self.config.columns)
        self.database.execute(f"CREATE TABLE IF NOT EXISTS {self.config.name} ({columns_sql})")

    def __insert_sql(self):
        str_values = ', '.join(['?' for _ in range(len(self.data))])
        str_fields = ', '.join([field for field in self.data.keys()])
        self.database.execute(f'INSERT INTO {self.config.name} ({str_fields}) VALUES({str_values})', [v for v in self.data.values()])

    def __update_sql(self):      
        str_values = ', '.join([f'{key} = ?' for key in self.data.keys()])
        self.database.execute(f'UPDATE {self.config.name} SET {str_values} WHERE id=1', list(self.data.values()))
    
    def __select_sql(self) -> dict[str, str]:
        view_fields = self.config.get_view_fields()
        str_fields = ', '.join(view_fields)
        res = self.database.execute(f'SELECT {str_fields} FROM {self.config.name}')

        return {k: v for k, v in zip(view_fields, res.fetchall()[0])} if res else {}

    def __get_all_specification_data(self) -> list[dict[str, Union[str, list[list[TData]]]]]:    
        if SPECIFICATION_CONFIG.name not in self.database.get_exist_tables():
            return
        
        columns = SPECIFICATION_CONFIG.columns
        query = f"SELECT * FROM {SPECIFICATION_CONFIG.name}"
        eixst_table_sql = self.database.execute(query).fetchall()

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

            data = [list(row) for row in self.database.execute(query).fetchall()]
            table['data'] = data
            tables.append(table)
        return tables


class SpecificationDataItem(GeneralDataItem):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.specification_config: TableConfig = SPECIFICATION_CONFIG
        self.config: TableConfig = GENERAL_ITEM_CONFIG
        self.unique_config: TableConfig = None
        self.fields_config: TableConfig = FIELDS_CONFIG
        self.data: list[list[TData]] = None
        self.type_spec: NameTableSQL = None
        self.sid: int = None

    def save(self) -> None:
        if not self.is_init:
            self.__create_sql()
            self.__insert_specification_sql(self.type_spec)
            self.__insert_in_sql_filed()
            self.__insert_sql()
        else:
            self.__update_sql()
        
        self.database.commit()
        self.database.close()

    def __create_sql(self) -> None:
        for config in (self.specification_config, self.config, self.unique_config):
            if config:
                columns_sql = ", ".join(col.sql_definition for col in config.columns + config.columns_property)
                self.database.execute(f"CREATE TABLE IF NOT EXISTS {config.name} ({columns_sql})")

        self.database.commit()

    def __insert_specification_sql(self, type_spec: NameTableSQL) -> None:
        field_sql = tuple(col.field for col in self.specification_config.columns if not col.is_id)
        field_str = ', '.join(field_sql)
        values_str = ', '.join(['?'] * len(field_sql))
        
        now_str = get_now_time()

        self.database.execute(f"INSERT INTO {self.specification_config.name} ({field_str}) VALUES({values_str})", (type_spec.value, now_str, now_str))
        self.sid = self.database.execute('SELECT last_insert_rowid();').fetchall()[0][0]

        self.database.commit()
    
    def __insert_in_sql_filed(self) -> None:
        columns_sql = ", ".join(col.sql_definition for col in self.fields_config.columns)
        self.database.execute(f"CREATE TABLE IF NOT EXISTS {self.fields_config.name} ({columns_sql})")
        
        fields = tuple(col.field for col in self.fields_config.columns if not col.is_id)
        str_fields = ', '.join(fields)

        for config in (self.config, self.unique_config):
            for column in config.columns:
                if not column.is_id:
                    values = tuple(getattr(column,  field) for field in fields if hasattr(column, field))
                    count_values = ', '.join(['?'] * len(values))
                    self.database.execute(f"INSERT INTO {self.fields_config.name} ({str_fields}) VALUES({count_values})", values)
        self.database.commit()
    
    def __insert_sql(self) -> None:
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
                    
                    self.database.execute(f'INSERT INTO {config.name} ({str_fields}) VALUES({str_values})', part_data_row)
                    if config.parent_config:
                        last_id = self.database.execute('SELECT last_insert_rowid();').fetchall()[0][0]
                        parent_id = self.sid if config == self.config else last_id
                        self.__set_foreign_key(config, last_id=last_id, parent_id=parent_id)
        
    def __set_foreign_key(self, config: TableConfig, last_id:int, parent_id: int) -> None:
        field_foreign_key = config.get_foreign_field()
        
        if field_foreign_key:       
            self.database.execute(f"UPDATE {config.name} SET {field_foreign_key} = '{parent_id}' WHERE id={last_id}")

    def __update_sql(self):
        str_values = [', '.join([f'{col.field} = ?' for col in config.columns]) for config in (self.config, self.unique_config)]
        
        index_config = (0, len(self.config.columns))
        index_unique = (index_config[1], index_config[1] + len(self.unique_config.columns))
        
        for row in self.data:
            for name, str_value, index in zip((self.config.name, self.unique_config.name), 
                                              str_values, 
                                              (index_config, index_unique)):
                
                index_start, index_end = index
                data = row[index_start: index_end]

                self.database.execute(f'UPDATE {name} SET {str_value} WHERE id={data[0]}', data)

    def get_index_from_name_filed(self, field: str) -> int:
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
    pp_data.__create_sql()
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
    pp_data.__insert_sql()
    

    inv_data = InventorSpecificationDataItem(database)
    inv_data.__create_sql()
    
    path_xlsx = r'D:\Python\AlfaServis\Constructor\projects\specification\DEBUG\ALS.1642.5.3.05.01.00.000 - Инвентор.xlsx'
    data = get_specifitaction_inventor_from_xlsx(path_xlsx)

    inv_data.set_data(data)
    inv_data.__insert_sql()

    # buy_data = BuySpecificationDataItem(database)
    # buy_data.create_sql()

    # tables = pp_data.get_all_specification_data()
    # print(tables)


"""
Я пишу проект на pyqt5 с испльзованием SqlIte3
У меня такая иерархия QTreeWidget.item -> QTreeItem.data_item -> (DataItem.dataset, DataItem.database) -> Databse (управляет работой с БД)
У меня есть рабочая область поделенная на две части. В левой части QTreeWidget, а в правой QWitdet, который отображает контент.
Данные, которые необходимо отображать храняться в  QTreeWidget.item.data_item
Изначально данные хронятся в SQlite.
Пользователь может изменять данные поэтому я делаю обращения к БД. Иногда может быть несколько последовательных запросов
Как мне правильно организовать работу с БД, чтобы открыть соединение и закрыть после того, как будут выполнены все нужные запросы
При нажатии кнопки сохранить в приложении происходит обращение к QTreeWidget, затем смотрится активый Item и для него происходит обращение в БД
вот пример из фунции save
self.current_item.data_item.create_sql()
self.current_item.data_item.insert_sql()

Я проверю была ли создана таблица и если нет создаю, за тем заполняю

Так выглядат методы 

    def create_sql(self):
        columns_sql = ", ".join(col.sql_definition for col in self.config.columns)
        self.database.execute(f"CREATE TABLE IF NOT EXISTS {self.config.name} ({columns_sql})")
        self.database.commit()
        self.database.close()

    def insert_sql(self):
        str_values = ', '.join(['?' for _ in range(len(self.data))])
        str_fields = ', '.join([field for field in self.data.keys()])
        self.database.execute(f'INSERT INTO {self.config.name} ({str_fields}) VALUES({str_values})', [v for v in self.data.values()])
        self.database.commit()
        self.database.close()
    
    def execute(self, query, *args, **kwargs) -> sqlite3.Cursor:
        self.connect()
        
        response_cursor = None
        try:
            response_cursor = self.conn.execute(query, *args, **kwargs)
        except Exception as erorr:
            print(erorr)
            print('Ошибка выполнения запроса')
            print(query, *args, **kwargs, sep='\n')
        
        return response_cursor


Мне не нравится, что я сначала закрываю, а потом октрываю БД 
Но также не хочу в QItemWTreeWidget при обращении в item_data прописывать отрытие и закртиые в БД, так как QItemWTreeWidget не должен знать про БД, про неё знает item_data
Я думаю прописать функцию для созадине цеопчки запоросов, как бы контекстный менеджер, но не уверен что это правильно

def chain_execute(self, *querys):
    self.database.connect()

    for query inquerys:
        self.databse.execute(*query)
    
    self.database.commit()
    self.database.close()

"""