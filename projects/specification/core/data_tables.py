from typing import Union
from dataclasses import dataclass, fields
import json

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)

    sys.path.append(test_path)

from projects.specification.config.app_context import DATACLASSES, ENUMS


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
    PARAMETER_CELL_CONFIG,
    PARAMETER_CELL_LINK_CONFIG,
    PARAMETER_HEADER_CONFIG,
    PARAMETER_TABLE_CONFIG
)
from projects.specification.core.functions import get_now_time


class GeneralDataItem:
    """
    Базовый класс для хранения и обработки данных проекта (свойства проекта, таблицы)
    """
    def __init__(self):
        self.database: DataBase = None        
        self.data: dict[str, str] | list[list[DATACLASSES.DATA_CELL]] = None
        self.config: TableConfig = None
        self._is_init: bool = False
        self._is_save: bool = False

    def get_data(self) -> dict[str, str] | list[list[DATACLASSES.DATA_CELL]]:
        return self.data
    
    def set_data(self, data: dict[str, str] | list[list[DATACLASSES.DATA_CELL]]):
        self.data = data
    
    @property
    def is_init(self) -> bool:
        return self._is_init

    def set_is_init(self, value: bool) -> True:
        self._is_init = value

    @property
    def is_save(self) -> bool:
        return self._is_save

    def set_is_save(self, value: bool) -> None:
        """
        Установка флага, что данные сохранены в БД
        
        :param value: True - сохранены, False - не сохранены
        :type value: bool
        """
        self._is_save = value

    def save(self) -> None:
        """
        Docstring для load

        Сохранение self.data в БД для save

        :return:
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
        """
        Получение полного пути файла БД, где хранится проект
        
        :return: полный путь
        :rtype: str
        """
        return '' if self.database is None else self.database.filepath

    def get_filed_and_count(self, columns: list[ColumnConfig]) -> tuple[str, str]:
        """
        - Генерация строчка, где перечислены поля через запятную без id\n
        - А также строчка "?, ? ...", где количество вопросов равно длине полей без id"\n
        Нужно для формирования строчки SQL запроса
        
        :param columns: список строчек
        :type columns: list[ColumnConfig]
        :return:  'number, description, ...' '?, ?, ...'
        :rtype: tuple[str, str]
        """
        fields = tuple(col.field for col in columns if not col.is_id)
        return ', '.join(fields), ', '.join(['?'] * len(fields))

    def _create_sql(self) -> None:
        ...
    
    def _insert_sql(self) -> None:
        ...
    
    # def _insert_style_sql(self, x: int, y: int, fields_style: tuple[str,...], value_style_cell: list[str | int | bool], fields_style_link: tuple[str, ...]) -> None:
    #     """
    #     Добавления стилей для каждой ячейки в БД
        
    #     :param x: номер столбца
    #     :type x: int
    #     :param y: номер строки
    #     :type y: int
    #     :param value_style_cell: стили ячейки
    #     :type cell: DATACLASSES.DATA_CELL
    #     :param fields_style: список имён полей стиливой таблицы
    #     :type fields_style: tuple[str, ...]
    #     :param fields_style_link: списко имён полей таблицы стилей ячейки
    #     :type fields_style_link: tuple[str, ...]
    #     """

    def _update_sql(self) -> None:
        ...

    def _select_sql(self) -> tuple | None:
        ... 
    
    def _delete_sql(self) -> None:
        ...
    

class PropertyProjectData(GeneralDataItem):
    """
    - Хранения и обработка данных проекта
    - Выгрузка из БД всех таблиц 
    """
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
            self._create_sql()
            self._insert_sql()
        else:
            self._update_sql()
        
        self.database.commit()
        self.database.close()

    def load_project(self, filepath: str)-> list[dict[str, str | list[list[DATACLASSES.DATA_CELL]]]]:
        """
        Загрузка всех данных по проекту
        
        :param filepath: Полный путь к проекту
        :type filepath: str
        :return: таблицы и их свойства
        :rtype: list[dict[str, str | list[list[DATA_CELL]]]]
        """
        if self.database is None:
            if filepath:
                self.database = DataBase(filepath) 
            else:
                raise SystemError('Необходимо передать filepath')

        self.set_data(self._select_sql())
        tables = self._get_all_specification_data()
        self.set_is_init(True)
        self.database.close()

        return tables
    
    def delete(self):
        """
        Удаление проекта из БД
        """
        return super().delete()

    def _create_sql(self):
        """
        Создание таблицы свойств проекта без таблиц
        """
        fields = tuple(col.sql_definition for col in self.config.columns)
        self.database.create(self.config.name, fields)

    def _insert_sql(self):
        """
        Вставка строк в таблицу свойств проекта
        """
        self.database.insert(self.config.name, tuple(self.data.keys()), tuple(self.data.values()))

    def _update_sql(self):  
        """
        Обновление данных в таблице свойств проекта
        """
        self.database.update(table_name=self.config.name, 
                            id_row=1, 
                            fields=tuple(self.data.keys()), 
                            value=tuple(self.data.values()))    
    
    def _select_sql(self) -> dict[str, str]:
        """
        Получение из БД свойст проекта без таблиц
        
        :param self: Описание
        :return: словарь, key ключ имя поля, value его значение 
        :rtype: dict[str, str]
        """
        
        view_fields = self.config.get_view_fields()
        res = self.database.select(self.config.name, view_fields)
        
        return {k: v for k, v in zip(view_fields, res.fetchall()[0])} if res else {}

    def _delete_sql(self) -> None:
        """
        Реализация метода удаление проекта из БД
        """

    def _get_all_specification_data(self) -> list[dict[str, list[list[DATACLASSES.DATA_CELL]]]]:
        """
        Загрузка всех спецификация из БД соответствующих данному проекту
        
        :return: таблицы и их свойства
        :rtype: list[dict[str, list[list[DATA_CELL]]]]
        """    
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
            
            query = f"""
            SELECT * 
            FROM {ENUMS.NAME_TABLE_SQL.GENERAL.value} 
            LEFT JOIN {table['type_spec']} ON {table['type_spec']}.parent_id = {ENUMS.NAME_TABLE_SQL.GENERAL.value}.id 
            WHERE {ENUMS.NAME_TABLE_SQL.GENERAL.value}.parent_id = {table['id']}
            ORDER BY number_row
            """

            data = [[DATACLASSES.DATA_CELL(value=cell) for cell in row] for row in self.database.execute(query).fetchall()]
            table['data'] = data

            cells_style = self._load_styles(table['id'])
            for (row, column), cell_style in cells_style.items():
                for name_style, value in cell_style.items():
                    setattr(data[row][column], name_style, value)
            tables.append(table)

            table['header_data'] = self._load_parameter_header(table['id'])

        return tables

    def _load_styles(self, sid: int) -> dict[tuple[int, int], dict[str, str | bool | int]]:
        """
        Загрузка стилей для таблицы
        
        :param sid: номер id спецификации
        :type sid: int
        :return: {(row, column): {'align_h': 28, ...}}
        :rtype: dict[tuple[int, int], dict[str, str | bool | int]]
        """
        fields_style = tuple(col.field for col in PARAMETER_CELL_CONFIG.columns if not col.is_id)
        
        res = self.database.execute(f"""
        SELECT number_row, column, {', '.join(fields_style)}
        FROM {PARAMETER_CELL_LINK_CONFIG.name}
        LEFT JOIN {GENERAL_ITEM_CONFIG.name} ON {GENERAL_ITEM_CONFIG.name}.id = {PARAMETER_CELL_LINK_CONFIG.name}.parent_id
        LEFT JOIN {PARAMETER_CELL_CONFIG.name} ON {PARAMETER_CELL_CONFIG.name}.id = {PARAMETER_CELL_LINK_CONFIG.name}.style_id
        WHERE sid = {sid}
        ORDER BY number_row
        """)

        dct = {}
        for data in res:
            row, column, style = data
            dct[(row, column)] = json.loads(style)
        
        return dct

    def _load_parameter_header(self, sid: int) -> list[list]:
        fields: list[str] = [col.field for col in PARAMETER_HEADER_CONFIG.columns if not col.is_id and not col.is_foreign_id]
        add_query = f' WHERE parent_id = {sid}'
        res = self.database.select(PARAMETER_HEADER_CONFIG.name, fields, add_query).fetchall()

        data_header = []
        for row in res:
            data_header.append(DATACLASSES.DATA_HEADERS(**{k: v for k, v in zip(fields, row)}))
        return data_header


class SpecificationDataItem(GeneralDataItem):
    def __init__(self, database, unique_config: TableConfig):
        super().__init__()
        self.database: DataBase = database

        self.specification_config: TableConfig = SPECIFICATION_CONFIG
        self.general_config: TableConfig = GENERAL_ITEM_CONFIG
        self.unique_config: TableConfig = unique_config
        self.fields_config: TableConfig = FIELDS_CONFIG
        self.parameter_cell_config: TableConfig = PARAMETER_CELL_CONFIG
        self.parameter_cell_link_config: TableConfig = PARAMETER_CELL_LINK_CONFIG
        self.parameter_header_config: TableConfig = PARAMETER_HEADER_CONFIG
        self.parameter_table_config: TableConfig =  PARAMETER_TABLE_CONFIG
        
        self.data: list[list[DATACLASSES.DATA_CELL]] = None
        self.table_data: DATACLASSES.PARAMETER_TABLE = None
        self.horizontal_header_data: list [DATACLASSES.DATA_HEADERS] = None
        self.vertical_header_data: list [DATACLASSES.DATA_HEADERS] = None
        
        self.type_spec = None
        self._sid: int = None

        self.total_columns: tuple[ColumnConfig] = tuple(self.general_config.columns + self.unique_config.columns)  
        self.fields_general: tuple[str] = tuple(col.field for col in self.general_config.columns)
        self.fields_unique: tuple[str] = tuple(col.field for col in self.unique_config.columns)
        self.fields_style: tuple[str] = tuple(col.field for col in self.parameter_cell_config.columns)
        self.fields_style_link: tuple[str] = tuple(col.field for col in self.parameter_cell_link_config.columns)
    
    def set_sid(self, sid: int) -> None:
        self._sid = sid

    def _set_data_index(self) -> tuple[int, ...]:
        """
        Формирование только видимых индексов таблицы

        :return: [0, 1, 3, 7, ...] - индексы колонок у которы is_view = True
        :rtype: tuple[int, ...]
        """
        return tuple(i for i, col in enumerate(self.general_config.columns + self.unique_config.columns) if col.is_view)

    def get_data(self) -> list[list[DATACLASSES.DATA_CELL]]:
        return super().get_data()

    def set_header_data(self, header_data: list[DATACLASSES.DATA_HEADERS]) -> None:
        self.vertical_header_data = []
        self.horizontal_header_data = []
        for data in header_data:
            if isinstance(data.parameters, str):
                data.parameters = json.loads(data.parameters)
            if data.row == -1:
                self.horizontal_header_data.append(data)
            else:
                self.vertical_header_data.append(data)

    def save(self) -> None:
        if not self.is_init:
            self._create_sql()
            self._insert_specification_sql(self.type_spec)
            self._insert_in_sql_filed()

        self._insert_or_update_sql()
        self._insert_or_update_header_data()
        
        self.database.commit()
        self.database.close()

    def delete(self) -> None:
        if self._sid:
            self.__delete_sql()
            self.database.commit()
            self.database.close()
        
    def _create_sql(self) -> None:
        """
        Создание всех стандартных таблиц, если они ещё не созданы
        """
        for config in (self.specification_config, 
                       self.general_config, 
                       self.unique_config, 
                       self.parameter_cell_config, 
                       self.parameter_cell_link_config, 
                       self.parameter_header_config, 
                       self.parameter_table_config):
            if config:
                columns_sql = tuple(col.sql_definition for col in config.columns + config.columns_property)
                self.database.create(config.name, columns_sql)

        self.database.commit()

    def _insert_specification_sql(self, type_spec: ENUMS.NAME_TABLE_SQL) -> None:
        """
        Вставка записи в таблицу спецификаций о новой таблице
        
        :param type_spec: тип передаваемой таблицы
        :type type_spec: ENUMS.NAME_TABLE_SQL
        """
        
        field_sql = tuple(col.field for col in self.specification_config.columns if not col.is_id)
        now_str = get_now_time()

        self.database.insert(self.specification_config.name, field_sql, (type_spec.value, now_str, now_str))
        self._sid = self.database.get_last_id()

        self.database.commit()
    
    def _insert_in_sql_filed(self) -> None:
        """
        Вставка названий колонк для спецификаций в БД
        """
        columns_sql = tuple(col.sql_definition for col in self.fields_config.columns)
        self.database.create(self.fields_config.name, columns_sql)
        
        fields = tuple(col.field for col in self.fields_config.columns if not col.is_id)

        for config in (self.general_config, self.unique_config):
            for column in config.columns:
                if not column.is_id:
                    values = tuple(getattr(column,  field) for field in fields if hasattr(column, field))
                    self.database.insert(self.fields_config.name, fields, values)
        self.database.commit()
    
    def _insert_or_update_sql(self) -> None:
        for y, row in enumerate(self.data):
            if row[0].value is None:
                self._insert_row_sql(y, row)
            else:
                self._update_row_sql(y, row)
    
    def _insert_row_sql(self, y: int, row: list[DATACLASSES.DATA_CELL]) -> None:
        id_general, *value_general = [cell.value for cell in row[:len(self.general_config.columns)]]
        id_unique, *value_unique = [cell.value for cell in row[len(self.general_config.columns): ]]

        self.database.insert(self.general_config.name, self.fields_general[1:], value_general)
        id_general = self.database.get_last_id()
        self._set_foreign_key(self.general_config, last_id=id_general, parent_id=self._sid)

        self.database.insert(self.unique_config.name, self.fields_unique[1:], value_unique)
        id_unique = self.database.get_last_id()
        self._set_foreign_key(self.unique_config, last_id=id_unique, parent_id=id_unique)

        for x, (cell, col) in enumerate(zip(row, self.total_columns)):
            if not col.is_id and col.is_view:
                value_style_cell: str = json.dumps(cell.get_dict_style())
                self._insert_sytle_sql(value_style_cell)
                self._insert_cell_style_sql(id_general, x, value_style_cell)

    def _update_row_sql(self, y: int, row: list[DATACLASSES.DATA_CELL]) -> None:
        id_general, *value_general = [cell.value for cell in row[:len(self.general_config.columns)]]
        id_unique, *value_unique = [cell.value for cell in row[len(self.general_config.columns): ]]

        self.database.update(self.general_config.name, self.fields_general[1:], value_general, id_general)
        self.database.update(self.unique_config.name, self.fields_unique[1:], value_unique, id_unique)

        for x, (cell, col) in enumerate(zip(row, self.total_columns)):
            if col.is_view and col.is_view:
                value_style_cell: str = json.dumps(cell.get_dict_style())
                self._insert_sytle_sql(value_style_cell)
                self._updata_cell_style_sql(id_general, x, value_style_cell)

    def _insert_sytle_sql(self, value: str) -> None:
        """
        Добавление уникальных стилей в таблицу стилей
        """
        add_query = f'ON CONFLICT({", ".join(self.fields_style[1:])}) DO NOTHING'
        self.database.insert(self.parameter_cell_config.name, self.fields_style[1:], [value], add_query)

    def _insert_cell_style_sql(self, id_general: int, column: int, value: str) -> None:
        """
        Добавление адреса ячейка и ссылки на стиль
        """
        style_id = self._get_id_style(value)
        self.database.insert(self.parameter_cell_link_config.name, self.fields_style_link[1:], [id_general, column, self._sid, style_id])

        #TODO реализовать вставка размеров заголовков таблицы
    
    def _updata_cell_style_sql(self, id_general: int, x: int, value: str) -> None:
        """
        Обновление стиля для ячейки
        """
        style_id = self._get_id_style(value)
        add_query = f" WHERE parent_id='{id_general}' AND column='{x}'"
        self.database.update(table_name=self.parameter_cell_link_config.name, fields=['style_id'], value=[style_id], add_query=add_query)

    def _get_id_style(self, value: str) -> int | None:
        """
        Получение id стиля из таблицы по заданным значениям. Так как значение стиля уникальное, то надо передать все значения стиля
        
        :param values: значения стиля
        :type values: tuple[str | int | bool]
        :return: id стиля в таблице
        :rtype: int | None
        """
        add_query_select = f" WHERE style = '{value}'"
        res = self.database.select(self.parameter_cell_config.name, ('id', ), add_query_select).fetchall()
        if res:
            return res[0][0]

    def _set_foreign_key(self, config: TableConfig, last_id:int, parent_id: int) -> None:
        field_foreign_key = config.get_foreign_field()
        
        if field_foreign_key:       
            self.database.execute(f"UPDATE {config.name} SET {field_foreign_key} = '{parent_id}' WHERE id={last_id}")

    def _insert_or_update_header_data(self) -> None:
        fields: list[str ]= [col.field for col in self.parameter_header_config.columns if not col.is_id]

        for header_data in self.horizontal_header_data + self.vertical_header_data:
            dict_data_header = header_data.get_dict_data()
            values = []
            for field in fields:
                param = dict_data_header.get(field)
                if param is not None:
                    if isinstance(param, dict):
                        param = json.dumps(param)
                    values.append(param)
            values.append(self._sid)
            
            query = f"""
            SELECT
                EXISTS(SELECT * FROM {self.parameter_header_config.name} WHERE row = {header_data.row} AND column = {header_data.column} AND parent_id = {self._sid}) as cell
            """
            exist = self.database.execute(query).fetchall()[0][0]
        
            if exist == 0:
                self.database.insert(PARAMETER_HEADER_CONFIG.name, fields, values)
            else:
                add_query = f" WHERE row = {header_data.row} AND column = {header_data.column} AND parent_id = {self._sid}"
                self.database.update(table_name=PARAMETER_HEADER_CONFIG.name, fields=fields, value=values, add_query=add_query)
 
    def get_index_from_name_filed(self, field: str) -> int:
        for i, col in enumerate(self.general_config.columns + self.unique_config.columns):
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

