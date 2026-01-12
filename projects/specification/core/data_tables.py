from typing import Union, Sequence
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
    
    def _delete_specification_sql(self) -> None:
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
                            row_id=1, 
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

    def _delete_specification_sql(self) -> None:
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
            WHERE {ENUMS.NAME_TABLE_SQL.GENERAL.value}.sid = {table['id']}
            ORDER BY number_row
            """

            data = [[DATACLASSES.DATA_CELL(value=str(cell) if cell is not None else cell) for cell in row] for row in self.database.execute(query).fetchall()]
            table['data'] = data

            cells_style = self._load_styles(table['id'])
            for (row, column), cell_style in cells_style.items():
                for name_style, value in cell_style.items():
                    setattr(data[row][column], name_style, value)
            tables.append(table)

            table['header_data'] = self._load_parameter_header(table['id'])
            table['table_data'] = self._load_parameter_table(table['id'])
            table['links'] = self._load_link_item(table['id'])

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
        WHERE {GENERAL_ITEM_CONFIG.name}.sid = {sid}
        ORDER BY number_row
        """).fetchall()

        dct = {}
        for data in res:
            row, column, style = data
            dct[(row, column)] = json.loads(style)
        
        return dct

    def _load_parameter_header(self, sid: int) -> list[list]:
        fields: list[str] = [col.field for col in PARAMETER_HEADER_CONFIG.columns if not col.is_id and not col.is_foreign_id]
        add_query = f' WHERE sid = {sid}'
        res = self.database.select(PARAMETER_HEADER_CONFIG.name, fields, add_query).fetchall()

        data_header = []
        for row in res:
            data_header.append(DATACLASSES.DATA_HEADERS(**{k: v for k, v in zip(fields, row)}))
        return data_header

    def _load_parameter_table(self, sid: int) -> dict[str, int | tuple[int, int, int, int]] | None:
        fields = [col.field for col in PARAMETER_TABLE_CONFIG.columns if not col.is_id and not col.is_foreign_id]
        add_query = f' WHERE sid = {sid}'
        res = self.database.select(PARAMETER_TABLE_CONFIG.name, fields, add_query).fetchall()

        if res:
            return DATACLASSES.PARAMETER_TABLE(**json.loads(res[0][0]))

    def _load_link_item(self, sid: int) -> dict[int, list[list]]:
        fields_general = [f'{GENERAL_ITEM_CONFIG.name}.{col.field}' for col in GENERAL_ITEM_CONFIG.columns if col]
        fields_inventor = [f'{INVENTOR_ITEM_CONFIG.name}.{col.field}' for col in INVENTOR_ITEM_CONFIG.columns]
        str_fields = ', '.join(fields_general + fields_inventor)
        print(f"""
        SELECT {LINK_ITEM_CONFIG.name}.parent_item, {str_fields}
        FROM {LINK_ITEM_CONFIG.name}
        LEFT JOIN {GENERAL_ITEM_CONFIG.name} ON {GENERAL_ITEM_CONFIG.name}.id = {LINK_ITEM_CONFIG.name}.invetor_item
        LEFT JOIN {INVENTOR_ITEM_CONFIG.name} ON {INVENTOR_ITEM_CONFIG.name}.parent_id  = {GENERAL_ITEM_CONFIG.name}.id
        WHERE {LINK_ITEM_CONFIG.name}.sid = {sid}
        """)
        res = self.database.execute(f"""
        SELECT {LINK_ITEM_CONFIG.name}.parent_item, {str_fields}
        FROM {LINK_ITEM_CONFIG.name}
        LEFT JOIN {GENERAL_ITEM_CONFIG.name} ON {GENERAL_ITEM_CONFIG.name}.id = {LINK_ITEM_CONFIG.name}.invetor_item
        LEFT JOIN {INVENTOR_ITEM_CONFIG.name} ON {INVENTOR_ITEM_CONFIG.name}.parent_id  = {GENERAL_ITEM_CONFIG.name}.id
        WHERE {LINK_ITEM_CONFIG.name}.sid = {sid}
        """)

        dct: dict[int, list[list]] = {}
        if res:
            for row in res:
                key, *value = row
                value = [DATACLASSES.DATA_CELL(value=i) for i in value]
                if key not in dct:
                    dct[key] = [value]
                else:
                    dct[key].append(value)
        return dct


class SpecificationDataItem(GeneralDataItem):
    def __init__(self, database, unique_config: TableConfig):
        super().__init__()
        self.database: DataBase = database
        self.table_name: str = 'Спецификация'

        self._is_update_link = False

        self.specification_config: TableConfig = SPECIFICATION_CONFIG
        self.general_config: TableConfig = GENERAL_ITEM_CONFIG
        self.unique_config: TableConfig = unique_config
        self.fields_config: TableConfig = FIELDS_CONFIG
        self.parameter_cell_config: TableConfig = PARAMETER_CELL_CONFIG
        self.parameter_cell_link_config: TableConfig = PARAMETER_CELL_LINK_CONFIG
        self.parameter_header_config: TableConfig = PARAMETER_HEADER_CONFIG
        self.parameter_table_config: TableConfig =  PARAMETER_TABLE_CONFIG
        self.link_item_config: TableConfig = LINK_ITEM_CONFIG
        
        self.data: list[list[DATACLASSES.DATA_CELL]] = None
        self.data_link: dict[int | str, list[list[DATACLASSES.DATA_CELL]]] = None
        self._list_delete_row: list[int] = [] #хранит id из general_config
        self.table_parameter: DATACLASSES.PARAMETER_TABLE = None
        self.horizontal_header_parameter: list [DATACLASSES.DATA_HEADERS] = None
        self.vertical_header_parameter: list [DATACLASSES.DATA_HEADERS] = None
        
        self.type_spec = None
        self._sid: int = None

        self.total_columns: tuple[ColumnConfig] = tuple(self.general_config.columns + self.unique_config.columns)  
        self.fields_general: tuple[str] = tuple(col.field for col in self.general_config.columns)
        self.fields_unique: tuple[str] = tuple(col.field for col in self.unique_config.columns)
        self.fields_style: tuple[str] = tuple(col.field for col in self.parameter_cell_config.columns)
        self.fields_style_link: tuple[str] = tuple(col.field for col in self.parameter_cell_link_config.columns)
    
    def set_sid(self, sid: int) -> None:
        self._sid = sid

    def set_data_link(self, data: list[list[DATACLASSES.DATA_CELL]]) -> None:
        self.data_link = data

    def add_item_data_link(self, id_row: int, row: list[DATACLASSES.DATA_CELL]) -> None:
        """
        Добавляет связанне ячейки для заданного id 
        """
        if id_row not in self.data_link:
            self.data_link[id_row] = [row]
        else:
            for added_row in self.data_link[id_row]:
                id_added_row = added_row[0].value
                if id_added_row == row[0].value:
                    return
            self.data_link[id_row].append(row)

    def set_is_update_link(self, value: bool) -> None:
        """
        Установка флага необходимости обновления ссылок
        
        :param value: True - обновить, False - не обновлять
        :type value: bool
        """
        self._is_update_link = value

    def get_data(self) -> list[list[DATACLASSES.DATA_CELL]]:
        return super().get_data()

    def set_header_data(self, header_data: list[DATACLASSES.DATA_HEADERS]) -> None:
        self.vertical_header_parameter = []
        self.horizontal_header_parameter = []
        for data in header_data:
            if isinstance(data.parameters, str):
                data.parameters = json.loads(data.parameters)
            if data.row == -1:
                self.horizontal_header_parameter.append(data)
            else:
                self.vertical_header_parameter.append(data)

    def set_table_data(self, table_data: DATACLASSES.PARAMETER_TABLE | None) -> None:
        if table_data is not None:
            self.table_parameter = table_data

    def save(self) -> None:
        if not self.is_init:
            self._create_sql()
            self._insert_specification_sql()
            self._insert_in_sql_filed()
        
        self._insert_or_update_sql()
        self._delete_row_sql()

        self.database.commit()
        if self._is_update_link:
            self._insert_and_update_data_link_sql()
            self._is_update_link = False
        
        self._insert_or_update_header_parameter_sql()
        self._insert_or_update_table_parameter_sql()
        
        self.database.commit()
        self.database.close()

    def delete(self) -> None:
        if self._sid:
            self._delete_specification_sql()
            self.database.commit()
            self.database.close()
        
    def _create_sql(self) -> None:
        """
        Создание всех стандартных таблиц, если они ещё не созданы
        """
        for config in (self.specification_config, 
                       self.general_config, 
                       self.unique_config, 
                       self.fields_config,
                       self.parameter_cell_config, 
                       self.parameter_cell_link_config, 
                       self.parameter_header_config, 
                       self.parameter_table_config,
                       self.link_item_config):
            if config:
                columns_sql = tuple(col.sql_definition for col in config.columns + config.columns_property)
                self.database.create(config.name, columns_sql)

        self.database.commit()

    def _insert_specification_sql(self) -> None:
        """
        Вставка записи в таблицу спецификаций о новой таблице
        
        :param type_spec: тип передаваемой таблицы
        :type type_spec: ENUMS.NAME_TABLE_SQL
        """
        
        field_sql = tuple(col.field for col in self.specification_config.columns if not col.is_id)
        now_str = get_now_time()

        cur = self.database.insert(self.specification_config.name, field_sql, (self.type_spec.value, self.table_name, now_str))
        row_id = cur.fetchall()[0][0]
        self._sid = row_id

        self.database.commit()
    
    def _insert_in_sql_filed(self) -> None:
        """
        Вставка названий колонк для спецификаций в БД
        """
        columns_sql = tuple(col.sql_definition for col in self.fields_config.columns)
        self.database.create(self.fields_config.name, columns_sql)
        
        fields = tuple(col.field for col in self.fields_config.columns if not col.is_id)
        str_fields = ", ".join(fields)

        for config in (self.general_config, self.unique_config):
            for column in config.columns:
                if not column.is_id:
                    values = tuple(getattr(column,  field) for field in fields if hasattr(column, field))
                    add_query = f' ON CONFLICT({str_fields}) DO NOTHING'
                    self.database.insert(self.fields_config.name, fields, values, add_query)
        self.database.commit()
    
    def _insert_or_update_sql(self) -> None:
        for y, row_data in enumerate(self.data):
            if row_data[0].value is None or isinstance(row_data[0].value, str):
                self._insert_row_sql(y, row_data)
            else:
                self._update_row_sql(y, row_data)
    
    def _insert_row_sql(self, y: int, row_data: list[DATACLASSES.DATA_CELL]) -> None:
        """
        Вставка в БД строки

        Важно, чтобы id был вначале таблицы, а parent_id в конце таблицы
        
        :param self: Описание
        :param y: Описание
        :type y: int
        :param row_data: Описание
        :type row_data: list[DATACLASSES.DATA_CELL]
        """
        id_general, *value_general = [cell.value for cell in row_data[:len(self.general_config.columns)]]
        id_unique, *value_unique = [cell.value for cell in row_data[len(self.general_config.columns): ]]

        # ----------------- Работа с general_config
        value_general[-1] = self._sid
        cur = self.database.insert(self.general_config.name, self.fields_general[1:], value_general)
        id_general = cur.fetchall()[0][0]

        self._update_id_link_data(old_id=row_data[0].value, new_id=id_general)

        row_data[0].value = id_general
        row_data[len(self.general_config.columns) -1].value = self._sid

        # ----------------- Работа с unique_config
        value_unique[-1] = id_general
        cur = self.database.insert(self.unique_config.name, self.fields_unique[1:], value_unique)
        id_unique = cur.fetchall()[0][0]
        row_data[len(self.general_config.columns)].value = id_unique
        row_data[len(self.total_columns) - 1].value = id_general

        for x, (cell, col) in enumerate(zip(row_data, self.total_columns)):
            if not col.is_id and col.is_view:
                value_style_cell: str = json.dumps(cell.get_dict_style())
                self._insert_sytle_sql(value_style_cell)
                self._insert_cell_style_sql(id_general, x, value_style_cell)
        
    def _update_row_sql(self, y: int, row: list[DATACLASSES.DATA_CELL]) -> None:
        id_general, *value_general = [cell.value for cell in row[:len(self.general_config.columns)]]
        id_unique, *value_unique = [cell.value for cell in row[len(self.general_config.columns): ]]

        self.database.update(self.general_config.name, self.fields_general[1:], value_general, id_general)
        self._update_id_link_data(id_general, id_general)
        self.database.update(self.unique_config.name, self.fields_unique[1:], value_unique, id_unique)

        for x, (cell, col) in enumerate(zip(row, self.total_columns)):
            if col.is_view and col.is_view:
                value_style_cell: str = json.dumps(cell.get_dict_style())
                self._insert_sytle_sql(value_style_cell)
                self._updata_cell_style_sql(id_general, x, value_style_cell)

    def _update_id_link_data(self, old_id: int | str, new_id: int | str) -> None:
        """
        Замена временных id до сохранения спецификации на id из БД
        
        :param old_id: Временный ключ
        :type old_id: int | str
        :param new_id: Ключ из БД
        :type new_id: int | str
        """
        if self.data_link is not None:
            rows = self.data_link.get(old_id)
            if rows is not None:
                self.data_link[new_id] = rows
                if new_id != old_id:
                    del self.data_link[old_id]
    
    def _insert_and_update_data_link_sql(self) -> None:
        if self.data_link is not None:
            fields = [col.field for col in self.link_item_config.columns if not col.is_id]
            for parent_id, rows in self.data_link.items():
                add_query = f' WHERE parent_item={parent_id}'
                
                # Сначала удалить все связи связанные с id
                for row in rows:
                    child_id = row[0].value
                    self.database.delete(self.link_item_config.name, add_query=add_query)
                
                # Затем записать новые связи связанные с id
                for row in rows:
                    child_id = row[0].value
                    self.database.insert(self.link_item_config.name, fields, [int(parent_id), int(child_id), self._sid])

    def _insert_sytle_sql(self, value: str) -> None:
        """
        Добавление уникальных стилей в таблицу стилей
        """
        add_query = f' ON CONFLICT({", ".join(self.fields_style[1:])}) DO NOTHING'
        self.database.insert(self.parameter_cell_config.name, self.fields_style[1:], [value], add_query)

    def _insert_cell_style_sql(self, id_general: int, column: int, value: str) -> None:
        """
        Добавление адреса ячейка и ссылки на стиль
        """
        style_id = self._get_id_style(value)
        self.database.insert(self.parameter_cell_link_config.name, self.fields_style_link[1:], [id_general, column, self._sid, style_id])
    
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

    def _insert_or_update_header_parameter_sql(self) -> None:
        fields: list[str ]= [col.field for col in self.parameter_header_config.columns if not col.is_id]

        for header_data in self.horizontal_header_parameter + self.vertical_header_parameter:
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
                EXISTS(SELECT * FROM {self.parameter_header_config.name} WHERE row = {header_data.row} AND column = {header_data.column} AND sid = {self._sid}) as cell
            """
            exists = self.database.execute(query).fetchall()[0][0]
        
            if exists == 0:
                self.database.insert(PARAMETER_HEADER_CONFIG.name, fields, values)
            else:
                add_query = f" WHERE row = {header_data.row} AND column = {header_data.column} AND sid = {self._sid}"
                self.database.update(table_name=PARAMETER_HEADER_CONFIG.name, fields=fields, value=values, add_query=add_query)
    
    def _insert_or_update_table_parameter_sql(self) -> None:
        """
        Сохранение в БД данных о текущих параметрах таблицы (масштабирвоание, координаты скрола и др.)
        """
        value: str = json.dumps(self.table_parameter.get_dict_data())

        query = f"""
        SELECT 
            EXISTS(SELECT * FROM {self.parameter_table_config.name} WHERE sid = {self._sid}) as paramaters_table
        """
        exists = self.database.execute(query).fetchall()[0][0]

        if exists == 0:
            fields = [col.field for col in self.parameter_table_config.columns if not col.is_id]
            self.database.insert(self.parameter_table_config.name, fields, [value, self._sid])
        else:
            add_query = f' WHERE sid = {self._sid}'
            self.database.update(self.parameter_table_config.name, ['parameters'], [value], add_query=add_query)
        
    def get_index_from_name_filed(self, field: str) -> int:
        for i, col in enumerate(self.general_config.columns + self.unique_config.columns):
            if col.field == field:
                return i
        return -1 

    def _delete_specification_sql(self) -> None:
        """
        Удалить спецификацию из БД
        
        :param self: Описание
        """
        self.database.delete(self.specification_config.name, row_id=self._sid)

    def insert_row(self, row: int, row_data: list[DATACLASSES.DATA_CELL] = None, vertical_header_data: list[DATACLASSES.DATA_HEADERS]=None) -> None:
        if row_data is None:
            self.data.insert(row, [DATACLASSES.DATA_CELL(value='') for i in range(len(self.data[0]))])
            tmp_id = f'_{len(self.data)}'
            self.data[row][0].value = tmp_id
            self.data_link[tmp_id] = []
        else:
            self.data.insert(row, row_data)
            row_id = row_data[0].value
            if row_id in self._list_delete_row:
                self._list_delete_row.remove(row_id)
        
        if vertical_header_data is None:
            self.vertical_header_parameter.insert(row, DATACLASSES.DATA_HEADERS(row=row, column=-1, size=30))
        else:
            self.vertical_header_parameter.insert(row, vertical_header_data)
        
        for i, header_data in enumerate(self.vertical_header_parameter):
            header_data.row = i

    def delete_row(self, rows: Sequence[int]) -> tuple[list[DATACLASSES.DATA_CELL], list[DATACLASSES.DATA_HEADERS]]:
        self._list_delete_row += [self.data[row][0].value for row in rows]

        delete_row = [row for i, row in enumerate(self.data) if i in rows]
        delete_vertical_header = [row for i, row in enumerate(self.vertical_header_parameter) if i in rows]

        self.data[:] = [row for i, row in enumerate(self.data) if i not in rows]
        self.vertical_header_parameter[:] = [row for i, row in enumerate(self.vertical_header_parameter) if i not in rows]

        return delete_row, delete_vertical_header

    def _delete_row_sql(self) -> None:
        if self._list_delete_row:
            str_list_delete_row = ', '.join([str(i) for i in self._list_delete_row])
            add_query = f' WHERE id IN ({str_list_delete_row})'
            self.database.delete(table_name=self.general_config.name, add_query=add_query)
            self._list_delete_row.clear()


class InventorSpecificationDataItem(SpecificationDataItem):
    def __init__(self, database: DataBase, table_name: str):
        super().__init__(database, INVENTOR_ITEM_CONFIG)
        self.type_spec = ENUMS.NAME_TABLE_SQL.INVENTOR
        self.table_name = table_name
    
    def data_to_by(self) -> list[list[DATACLASSES.DATA_CELL]]:
        """
        Формирование спецификации на закупуку 
        
        :return: data Для BuySpecificationDataItem
        :rtype: list[list[DATA_CELL]]
        """

        by_data = []
        for header_cell, row in zip(self.vertical_header_parameter, self.data):
            by_row = []
            if not header_cell.parameters[ENUMS.PARAMETERS_HEADER.SELECT_ROW.name]:
                for cell, col in zip(row, self.general_config.columns):
                    # by_cell = DATACLASSES.DATA_CELL() if col.is_id else DATACLASSES.DATA_CELL(value=cell.value)
                    by_row.append(DATACLASSES.DATA_CELL(value=cell.value))
                by_data.append(by_row + [DATACLASSES.DATA_CELL() for _ in BUY_ITEM_CONFIG.columns] )

        return by_data
        
        
class BuySpecificationDataItem(SpecificationDataItem):
    def __init__(self, database: DataBase, table_name: str):
        super().__init__(database, BUY_ITEM_CONFIG)
        self.type_spec = ENUMS.NAME_TABLE_SQL.BUY
        self.table_name = table_name

    def set_data(self, data):
        self._set_data_link(data)
        super().set_data(data)
    
    def _set_data_link(self, data: list[list[DATACLASSES.DATA_CELL]]) -> None:
        """
        Формирование временных id Для отображения связей
        """
        if self.data is None and self.data_link is None:
            self.data_link = {}
            for i, row in enumerate(data):
                tmp_id = f'_{i}'
                self.data_link[tmp_id] = [[DATACLASSES.DATA_CELL(value=cell.value) for cell in row]]
                row[0].value = tmp_id


class ProdSpecificationDataItem(SpecificationDataItem):
    def __init__(self, database: DataBase, table_name: str):
        super().__init__(database, PROD_ITEM_CONFG)
        self.type_spec = ENUMS.NAME_TABLE_SQL.PROD
        self.table_name = table_name


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
    pp_data.save(os.path.join(os.getcwd(), '_data_test.scdata'))
    
    inv_data = InventorSpecificationDataItem(pp_data.database, '16.16.16')    
    path_xlsx = r'D:\Python\AlfaServis\Constructor\projects\specification\DEBUG\ALS.1642.4.2.01.00.00.000 СБ - нивентор.xlsx'
    data = get_specifitaction_inventor_from_xlsx(path_xlsx)

    inv_data.set_data(data)
    vertical_header_parameter = [DATACLASSES.DATA_HEADERS(row=i, column=-1, parameters={ENUMS.PARAMETERS_HEADER.SELECT_ROW.name: True}) for i in range(len(data))]
    inv_data.vertical_header_parameter = vertical_header_parameter
    
    # inv_data.save()

    buy_data = BuySpecificationDataItem(pp_data.database,'Закупочная 1')
    buy_data.set_data(inv_data.data_to_by())
    buy_data.save()



