from typing import Union
from dataclasses import dataclass, fields

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)

    sys.path.append(test_path)

from projects.specification.config.app_context.app_context import DATACLASSES, ENUMS


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
    PROD_ITEM_CONFG,
    STYLE_CELL_CONFIG,
    STYLE_CELL_LINK_CONFIG,
    STYLE_SECTION_CONFIG
)
from projects.specification.core.functions import get_now_time


class GeneralDataItem:
    def __init__(self):
        self.database: DataBase = None        
        self.data: dict[str, str] | list[list[DATACLASSES.DATA_CELL]] = None
        self.config: TableConfig = None
        self.__is_init: bool = False
        self.__is_save: bool = False

    def get_data(self) -> dict[str, str] | list[list[DATACLASSES.DATA_CELL]]:
        return self.data
    
    def set_data(self, data: dict[str, str] | list[list[DATACLASSES.DATA_CELL]]):
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

    def __insert_style_sql(self, style_cells: list[DATACLASSES.CELL_STYLE], style_section: list[DATACLASSES.SECTION_STYLE]) -> None:
        """
        Сохранение стилей для таблицы
        
        """

    def load_data(self) -> dict[str, str] | list[list[DATACLASSES.DATA_CELL]] | None:
        """
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

    def delete(self) -> None:
        """
        Docstring для delete
        Удаление спецификации из БД
        
        :param: Описание
        """
        
    def get_filepath(self) -> str:
        return '' if self.database is None else self.database.filepath

    def get_filed_and_count(self, columns: list[ColumnConfig]) -> tuple[str, str]:
        fields = tuple(col.field for col in columns if not col.is_id)
        return ', '.join(fields), ', '.join(['?'] * len(fields))

    def get_last_id(self) -> int:
        return self.database.execute('SELECT last_insert_rowid();').fetchall()[0][0]

    def __create_sql(self) -> None:
        ...
    
    def __insert_sql(self) -> None:
        ...
    
    def __update_sql(self) -> None:
        ...

    def __select_sql(self) -> tuple | None:
        ... 
    
    def __delee_sql(self) -> None:
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

    def load_data(self, filepath: str)-> list[dict[str, str | list[list[DATACLASSES.DATA_CELL]]]]:
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
    
    def delete(self):
        return super().delete()

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

    def __delete_sql(self) -> None:
        ...

    def __get_all_specification_data(self) -> list[dict[str, list[list[DATACLASSES.DATA_CELL]]]]:    
        if SPECIFICATION_CONFIG.name not in self.database.get_exist_tables():
            return
        
        columns = SPECIFICATION_CONFIG.columns
        query = f"SELECT * FROM {SPECIFICATION_CONFIG.name}"
        eixst_table_sql = self.database.execute(query).fetchall()

        tables = []
        for row in eixst_table_sql:
            table: dict[str, Union[str, list[list[DATACLASSES.DATA_CELL]]]] = {}
            for col, value in zip(columns, row):
                table[col.field] = value
            
            if table['type_spec'] == ENUMS.NAME_TABLE_SQL.INVENTOR.value:
                data_item = InventorSpecificationDataItem(self.database)
                data_item.set_sid(table['id'])
            elif table['type_spec'] == ENUMS.NAME_TABLE_SQL.BUY.value:
                ...
            elif table['type_spec'] == ENUMS.NAME_TABLE_SQL.PROD.value:
                ...
            data_item.load_data()
            # query = f"""
            # SELECT * 
            # FROM {ENUMS.NAME_TABLE_SQL.GENERAL.value} 
            # LEFT JOIN {table['type_spec']} ON {table['type_spec']}.parent_id = {ENUMS.NAME_TABLE_SQL.GENERAL.value}.id 
            # WHERE {ENUMS.NAME_TABLE_SQL.GENERAL.value}.parent_id = {table['id']}
            # ORDER BY number_row
            # """

            # data = [[DATACLASSES.DATA_CELL(value=cell) for cell in row] for row in self.database.execute(query).fetchall()]
            table['data'] = data_item
            tables.append(table)
        return tables


class SpecificationDataItem(GeneralDataItem):
    def __init__(self, database, unique_config: TableConfig):
        super().__init__()
        self.database: DataBase = database
        self.specification_config: TableConfig = SPECIFICATION_CONFIG
        self.config: TableConfig = GENERAL_ITEM_CONFIG
        self.unique_config: TableConfig = unique_config
        self.fields_config: TableConfig = FIELDS_CONFIG
        self.style_cell_config: TableConfig = STYLE_CELL_CONFIG
        self.style_cell_link_config: TableConfig = STYLE_CELL_LINK_CONFIG
        self.style_table_config: TableConfig = STYLE_SECTION_CONFIG
        self.data_index_view = self.__set_data_index()
        self.data: list[list[DATACLASSES.DATA_CELL]] = None
        self.type_spec = None
        self._sid: int = None
    
    def set_sid(self, sid: int) -> None:
        self._sid = sid

    def __set_data_index(self) -> tuple[int, ...]:
        """
        Формирование только видимых индексов таблицы

        :return: [0, 1, 3, 7, ...] - индексы колонок у которы is_view = True
        :rtype: tuple[int, ...]
        """
        return tuple(i for i, col in enumerate(self.config.columns + self.unique_config.columns) if col.is_view)

    def get_data(self) -> list[list[DATACLASSES.DATA_CELL]]:
        return super().get_data()

    def get_cell(self, row: int, column: int) -> DATACLASSES.DATA_CELL:
        """
        Получение ячейки по указанному адресу
        
        :param row: Номер строки
        :type row: int
        :param column: Номер столбца
        :type column: int
        :return: Ячейка
        :rtype: DATA_CELL
        """
        return self.data[row][self.data_index_view[column]]

    def set_cell(self, row: int, column: int, cell: DATACLASSES.DATA_CELL) -> None:
        """
        Присваивание значения по указанному адресу
        
        :param row: Номер строки
        :type row: int
        :param column: Номер столбца
        :type column: int
        :param cell: Ячейка
        :type cell: DATACLASSES.DATA_CELL
        """
        self.data[row][self.data_index_view[column]] = cell

    def get_value(self, row: int, column: int) -> int | float | str | None:
        """
        Получение значения из указаной ячейки

        :param row: Номер строки
        :type row: int
        :param column: Номер колонки
        :type column: int
        :return: Значение ячейки
        :rtype: int | float | str | None
        """
        return self.get_cell(row, column).value

    def set_value(self, row: int, column: int, value: int | float | str | None) -> None:
        """
        Присваивание значения по указанному адресу
        
        :param row: Номер строки
        :type row: int
        :param column: Номер колонки
        :type column: int
        :param value: Новое значение ячейки
        :type value: TData
        """
        self.data[row][self.data_index_view[column]].value = value
    
    def load_data(self) -> None:
        if self._sid:
            query = f"""
            SELECT * 
            FROM {ENUMS.NAME_TABLE_SQL.GENERAL.value} 
            LEFT JOIN {self.type_spec.value} ON {self.type_spec.value}.parent_id = {ENUMS.NAME_TABLE_SQL.GENERAL.value}.id 
            WHERE {ENUMS.NAME_TABLE_SQL.GENERAL.value}.parent_id = {self._sid}
            ORDER BY number_row
            """
            self.set_data(
                [[DATACLASSES.DATA_CELL(value=cell) if col.is_view else cell for col, cell in zip(self.config.columns + self.unique_config.columns, row)] 
                    for row in self.database.execute(query).fetchall()]
            )
        else:
            raise AttributeError('Отсутствует sid')

    def save(self) -> None:
        if not self.is_init:
            self.__create_sql()
            self.__insert_specification_sql(self.type_spec)
            self.__insert_in_sql_filed()
            self.__insert_or_update()
        else:
            self.__insert_or_update()
        
        self.database.commit()
        self.database.close()

    def delete(self) -> None:
        if self._sid:
            self.__delete_sql()
            self.database.commit()
            self.database.close()
        
    def __create_sql(self) -> None:
        for config in (self.specification_config, self.config, self.unique_config, self.style_cell_config, self.style_cell_link_config, self.style_table_config):
            if config:
                columns_sql = ", ".join(col.sql_definition for col in config.columns + config.columns_property)
                self.database.execute(f"CREATE TABLE IF NOT EXISTS {config.name} ({columns_sql})")

        self.database.commit()

    def __insert_specification_sql(self, type_spec: ENUMS.NAME_TABLE_SQL) -> None:
        field_sql = tuple(col.field for col in self.specification_config.columns if not col.is_id)
        field_str = ', '.join(field_sql)
        values_str = ', '.join(['?'] * len(field_sql))
        
        now_str = get_now_time()

        self.database.execute(f"INSERT INTO {self.specification_config.name} ({field_str}) VALUES({values_str})", (type_spec.value, now_str, now_str))
        self._sid = self.database.execute('SELECT last_insert_rowid();').fetchall()[0][0]

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
    
    def __insert_or_update(self) -> None:
        total_columns: list[ColumnConfig] = self.config.columns + self.unique_config.columns
        
        str_field_config, str_values_config = self.config.get_str_field_and_value_filter()
        str_field_unique_config, str_values_unique_config = self.get_filed_and_count(self.unique_config.columns)

        str_field_style_cells, str_values_style_cells = self.get_filed_and_count(self.style_cell_config.columns)
        str_field_style_cell_link, str_values_style_cell_link = self.get_filed_and_count(self.style_cell_link_config.columns)
                
        for y, row in enumerate(self.data):
            value_config = []
            value_unique_config = []

            for x, (cell, col) in enumerate(zip(row, total_columns)):
                cell_is_data_cell = isinstance(cell, DATACLASSES.DATA_CELL)
                value = cell.value if cell_is_data_cell else cell
                if x < len(self.config.columns):
                    value_config.append(value)
                else:
                    value_unique_config.append(value)

                if cell_is_data_cell:
                    self.__insert_cell_style_sql(cell, str_field_style_cells, str_values_style_cells)
                    self.__insert_cell_style_link_sql(y, x, str_field_style_cell_link, str_values_style_cell_link)
     
            if value_config[0] is None:
                self.database.execute(f'INSERT INTO {self.config.name} ({str_field_config}) VALUES({str_values_config})', value_config[1:])
                last_id = self.get_last_id()
                self.__set_foreign_key(self.config, last_id=last_id, parent_id=self._sid)
            else:
                self.database.execute(f'UPDATE {self.config.name} SET {str_field_config} WHERE id={value_config[0]}', value_config)

            if value_unique_config[0] is None:
                self.database.execute(f'INSERT INTO {self.unique_config.name} ({str_field_unique_config}) VALUES({str_values_unique_config})', value_unique_config[1:])
                last_id = self.get_last_id()
                self.__set_foreign_key(self.unique_config, last_id=last_id, parent_id=last_id)
            else:
                self.database.execute(f'UPDATE {self.unique_config.name} SET {str_field_unique_config} WHERE id={value_unique_config[0]}', value_unique_config)


    def __insert_sql(self) -> None:
        f_columns_without_id = lambda columns: [col for col in columns if not col.is_id]

        str_field_config, str_values_config = self.get_filed_and_count(f_columns_without_id(self.config.columns))
        str_field_unique_config, str_values_unique_config = self.get_filed_and_count(f_columns_without_id(self.unique_config.columns))

        str_field_style_cells, str_values_style_cells = self.get_filed_and_count(f_columns_without_id(self.style_cell_config.columns))
        str_field_style_cell_link, str_values_style_cell_link = self.get_filed_and_count(f_columns_without_id(self.style_cell_link_config.columns))
        
        total_columns: list[ColumnConfig] = self.config.columns + self.unique_config.columns
        
        for y, row in enumerate(self.data):
            value_config = []
            value_unique_config = []
            for x, (cell, col) in enumerate(zip(row, total_columns)):
                if not col.is_id:
                    value = cell.value if isinstance(cell, DATACLASSES.DATA_CELL) else cell
                    if x < len(self.config.columns):
                        value_config.append(value)
                    else:
                        value_unique_config.append(value)
                    
                    if isinstance(cell, DATACLASSES.DATA_CELL):
                        self.__insert_cell_style_sql(cell, str_field_style_cells, str_values_style_cells)
                        self.__insert_cell_style_link_sql(y, x, str_field_style_cell_link, str_values_style_cell_link)

            self.database.execute(f'INSERT INTO {self.config.name} ({str_field_config}) VALUES({str_values_config})', value_config)
            last_id = self.get_last_id()
            self.__set_foreign_key(self.config, last_id=last_id, parent_id=self._sid)

            self.database.execute(f'INSERT INTO {self.unique_config.name} ({str_field_unique_config}) VALUES({str_values_unique_config})', value_unique_config)
            last_id = self.get_last_id()
            self.__set_foreign_key(self.unique_config, last_id=last_id, parent_id=last_id)
        
        self.database.commit()

    def __insert_value_sql(self, row: list[DATACLASSES.DATA_CELL]) -> None:
        start = 0
        for config in (self.config, self.unique_config):
            if config:
                len_columns = len(config.columns)
                part_row = row[start: start + len_columns]
                start = len_columns

                str_fields, str_values = self.get_filed_and_count(config.columns)

                part_data_row = [data.value for data, col in zip(part_row, config.columns) if not col.is_id]
                    
                self.database.execute(f'INSERT INTO {config.name} ({str_fields}) VALUES({str_values})', part_data_row)
                if config.parent_config:
                    last_id = self.database.execute('SELECT last_insert_rowid();').fetchall()[0][0]
                    parent_id = self._sid if config == self.config else last_id
                    self.__set_foreign_key(config, last_id=last_id, parent_id=parent_id)

    def __set_foreign_key(self, config: TableConfig, last_id:int, parent_id: int) -> None:
        field_foreign_key = config.get_foreign_field()
        
        if field_foreign_key:       
            self.database.execute(f"UPDATE {config.name} SET {field_foreign_key} = '{parent_id}' WHERE id={last_id}")

    def __insert_cell_style_sql(self, cell: DATACLASSES.DATA_CELL, str_field_style_cells, str_values_style_cells) -> None:
        value_style_cell = [getattr(cell, col.field) for col in self.style_cell_config.columns if hasattr(cell, col.field)]
        self.database.execute(f"""
                              INSERT INTO {self.style_cell_config.name} ({str_field_style_cells}) 
                              VALUES({str_values_style_cells})
                              ON CONFLICT({str_field_style_cells})
                              DO NOTHING
                              """, value_style_cell)

    def __insert_cell_style_link_sql(self, row:int, column: int, str_field_style_cell_link, str_values_style_cell_link) -> None:
        self.database.execute(f'INSERT INTO {self.style_cell_link_config.name} ({str_field_style_cell_link}) VALUES({str_values_style_cell_link})', [row, column, self._sid])


        # fields_style_table = ", ".join(col.sql_definition for col in self.style_table_config.columns if not col.is_id)
        # str_values_fields_style_table = ', '.join(['?'] * len(fields_style_table))

        # for st_cell in style_cells:
        #     value = (st_cell.)

    def __update_sql(self) -> None:
        f_columns_without_id = lambda columns: [col for col in columns if not col.is_id]

        str_field_config, str_values_config = self.get_filed_and_count(f_columns_without_id(self.config.columns))
        str_field_unique_config, str_values_unique_config = self.get_filed_and_count(f_columns_without_id(self.unique_config.columns))

        str_field_style_cells, str_values_style_cells = self.get_filed_and_count(f_columns_without_id(self.style_cell_config.columns))
        str_field_style_cell_link, str_values_style_cell_link = self.get_filed_and_count(f_columns_without_id(self.style_cell_link_config.columns))

        total_columns: list[ColumnConfig] = self.config.columns + self.unique_config.columns
        
        for y, row in enumerate(self.data):
            value_config = []
            value_unique_config = []
            for x, (cell, col) in enumerate(zip(row, total_columns)):
                if not col.is_id:
                    value = cell.value if isinstance(cell, DATACLASSES.DATA_CELL) else cell
                    if x < len(self.config.columns):
                        value_config.append(value)
                    else:
                        value_unique_config.append(value)

            if isinstance(cell, DATACLASSES.DATA_CELL):
                    self.__insert_cell_style_sql(cell, str_field_style_cells, str_values_style_cells)
                    self.__insert_cell_style_link_sql(y, x, str_field_style_cell_link, str_values_style_cell_link)
            
            row_id = self.get_index_from_name_filed()
            self.database.execute(f'UPDATE {self.config.name} SET {str_field_config} WHERE id={self.data}', data)
            # self.database.execute(f'INSERT INTO {self.config.name} ({str_field_config}) VALUES({str_values_config})', value_config)
            # last_id = self.get_last_id()
            # self.__set_foreign_key(self.config, last_id=last_id, parent_id=self._sid)

            # self.database.execute(f'INSERT INTO {self.unique_config.name} ({str_field_unique_config}) VALUES({str_values_unique_config})', value_unique_config)
            # last_id = self.get_last_id()
            # self.__set_foreign_key(self.unique_config, last_id=last_id, parent_id=last_id)

        str_values = [', '.join([f'{col.field} = ?' for col in config.columns]) for config in (self.config, self.unique_config)]
        
        index_config = (0, len(self.config.columns))
        index_unique = (index_config[1], index_config[1] + len(self.unique_config.columns))
        


        for row in self.data:
            for name, str_value, index in zip((self.config.name, self.unique_config.name), 
                                              str_values, 
                                              (index_config, index_unique)):
                
                index_start, index_end = index
                data = [cell.value if isinstance(cell, DATACLASSES.DATA_CELL) else cell for cell in row[index_start: index_end]]

                self.database.execute(f'UPDATE {name} SET {str_value} WHERE id={data[0]}', data)

    def get_index_from_name_filed(self, field: str) -> int:
        for i, col in enumerate(self.config.columns + self.unique_config.columns):
            if col.field == field:
                return i
        return -1 

    def __delete_sql(self) -> None:
        self.database.execute(f'DELETE FROM {self.specification_config.name} WHERE id={self._sid}')


class InventorSpecificationDataItem(SpecificationDataItem):
    def __init__(self, database):
        super().__init__(database, INVENTOR_ITEM_CONFIG)
        self.type_spec = ENUMS.NAME_TABLE_SQL.INVENTOR
        
        
class BuySpecificationDataItem(SpecificationDataItem):
    def __init__(self, database):
        super().__init__(database, BUY_ITEM_CONFIG)
        self.type_spec = ENUMS.NAME_TABLE_SQL.BUY


class ProdSpecificationDataItem(SpecificationDataItem):
    def __init__(self, database):
        super().__init__(database, PROD_ITEM_CONFG)
        self.type_spec = ENUMS.NAME_TABLE_SQL.PROD


if __name__ == '__main__':
    import os
    from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx

    pp_data = PropertyProjectData()
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
    pp_data.save(os.path.join(os.getcwd(), '_data2.scdata'))
    

    inv_data = InventorSpecificationDataItem(pp_data.database)    
    path_xlsx = r'C:\Users\p.golubev\Desktop\python\AfaLServis\Constructor\projects\specification\DEBUG\ALS.1648.8.2.01.Из инвентора.xlsx'
    data = get_specifitaction_inventor_from_xlsx(path_xlsx)

    inv_data.set_data(data)
    inv_data.save()

    # buy_data = BuySpecificationDataItem(database)
    # buy_data.create_sql()

    # tables = pp_data.get_all_specification_data()
    # print(tables)

