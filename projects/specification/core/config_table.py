from dataclasses import dataclass, field

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)
    sys.path.append(test_path)


from projects.specification.config.app_context import ENUMS


@dataclass
class ColumnConfig:
    field: str = ''
    type_data: str = ''
    column_name: str = ''
    mode_column_name: str = ''
    internal_name: str = ''
    is_view: bool = True
    is_link: bool = False
    is_id: bool = False
    is_foreign_id: bool = False
    is_foreign_key: bool = False
    parent_table_name: str = None
    is_key: bool = False
    is_value: bool = False
    is_unique: bool = False
    
    @property
    def sql_definition(self) -> str:
        return f"{self.field} {self.type_data}"

    def __str__(self):
        return f'{self.field} {self.column_name}'
    
    def __repr__(self):
        return f'{self.field} {self.column_name}' 


class TableConfig:
    def __init__(self, name: str, columns: list[ColumnConfig]):
        self.name = name
        self.columns = columns
        self.columns_property = []
        self.__set_property_columns()

        self.__set_str_fields_and_values()
        
    def __set_property_columns(self) -> None:
        unique = []
        for col in self.columns:
            if col.is_foreign_id and col.parent_table_name is not None:
                col_foreign_key = ColumnConfig('', f'FOREIGN KEY ({col.field}) REFERENCES {col.parent_table_name} ON UPDATE CASCADE ON DELETE CASCADE', is_foreign_key=True, is_view=False)
                self.columns_property.append(col_foreign_key)
            if col.is_unique:
                unique.append(col.field)
        if unique:
            col_unique = ', '.join(unique)
            self.columns_property.append(ColumnConfig('', f'UNIQUE({col_unique})', is_view=False))
    
    def __set_str_fields_and_values(self) -> None:
        fields = []
        fields_without_id = []

        for col in self.columns:
            fields.append(col.field)
            if not col.is_id:
                fields_without_id.append(col.field)  

        self.str_field: str = ', '.join(fields)
        self.str_value: str = ', '.join(['?'] * len(fields))
        
        self.str_field_without_id: str = ', '.join(fields_without_id)
        self.str_value_without_id: str = ', '.join(['?'] * len(fields_without_id))

    def get_foreign_field(self) -> str:
        for col in self.columns:
            if col.is_foreign_id:
                return col.field
    
    def get_view_fields(self) -> tuple[str]:
        return tuple(col.field for col in self.columns if col.is_view)

    def get_view_columns_name(self) -> tuple[str]:
        return tuple(col.column_name for col in self.columns if col.is_view)
    
    def get_keys(self) -> tuple[int]:
        return tuple(col for col in self.columns if col.is_key)
    
    def get_values(self) -> tuple[int]:
        return tuple(col for col in self.columns if col.is_value)
    

FIELDS_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.NAME_FIELDS.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
        ColumnConfig('field', 'TEXT'),
        ColumnConfig('column_name', 'TEXT'),
        ColumnConfig('internal_name', 'TEXT'),
        ColumnConfig('is_key', 'BOOLEAN')
    ]
)

LINK_ITEM_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.LINKS.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
        ColumnConfig('element_1', 'INTEGER'),
        ColumnConfig('element_2', 'INTEGER')
    ]
)

PROPERTY_PROJECT_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.PROJECT_PROPERTY.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True, is_view=False),
        ColumnConfig('file_name', 'TEXT', 'Название файла', ' <span style=color:red;>*</span>'),
        ColumnConfig('project_name', 'TEXT', 'Обозначение проекта'),
        ColumnConfig('project_number', 'TEXT', 'Номер проекта', ' <span style=color:red;>*</span>'),
        ColumnConfig('number_contract', 'TEXT', 'Пункт договора'),
        ColumnConfig('address', 'TEXT', 'Адрес объекта'),
        ColumnConfig('manager', 'TEXT', 'Руководитель проекта'),
        ColumnConfig('technologist', 'TEXT', 'Инженер-технолог'),
        ColumnConfig('constructor', 'TEXT', 'Инженер-конструктор'),
        ColumnConfig('name_model', 'TEXT', 'Модель установки'),
        ColumnConfig('name_drawing', 'TEXT', 'Обозначение чертежа')
    ]
)

SPECIFICATION_CONFIG = TableConfig(
    name = ENUMS.NAME_TABLE_SQL.SPECIFICATION.value,
    columns = [
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
        ColumnConfig('type_spec', 'TEXT'),
        ColumnConfig('name_spec', 'TEXT'),
        ColumnConfig('datetime', 'TEXT'),
    ]
)

GENERAL_ITEM_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.GENERAL.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True, is_view=False),
        ColumnConfig('number_row', 'INTEGER', is_view=False),
        ColumnConfig('articul', 'TEXT', 'Инвентарный номер', internal_name='Stock Number', is_key=True),
        ColumnConfig('description', 'TEXT', 'Описание', internal_name='Description', is_key=True),
        ColumnConfig('specifications', 'TEXT', 'Технические характеристики', internal_name='Технические характеристики', is_key=True),
        ColumnConfig('quantity', 'REAL', 'КОЛ.', is_value=True),
        ColumnConfig('unit', 'TEXT', 'Единичная величина', is_value=True),
        ColumnConfig('material', 'TEXT', 'Материал', internal_name='Material', is_key=True),
        ColumnConfig('parent_id', 'INTEGER', is_view=False, is_foreign_id=True, parent_table_name=SPECIFICATION_CONFIG.name),
    ]
)

INVENTOR_ITEM_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.INVENTOR.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True, is_view=False),
        ColumnConfig('is_select', 'BOOLEAN', is_view=False),
        ColumnConfig('name', 'TEXT', 'Обозначение', internal_name='Part Number', is_key=True),
        ColumnConfig('groups', 'TEXT', 'Раздел', internal_name='Раздел', is_key=True),
        ColumnConfig('diff', 'REAL', 'Изменение количества'),
        ColumnConfig('parent_id', 'INTEGER', 'Связь', is_view=False, is_foreign_id=True, parent_table_name=GENERAL_ITEM_CONFIG.name),
    ]
)

BUY_ITEM_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.BUY.value,
    columns=[
        ColumnConfig('diametr', 'TEXT', 'Номинальный диаметр'),
        ColumnConfig('manufactureretr', 'TEXT', 'Производитель'),
        ColumnConfig('note', 'TEXT', 'Примечание'),
        ColumnConfig('invoice', 'TEXT', 'Счёт ОМТС'),
        ColumnConfig('link', 'BOOLEAN', 'Связь', is_link=True),
        ColumnConfig('parent_id', 'INTEGER', is_view=False, is_foreign_id=True, parent_table_name=GENERAL_ITEM_CONFIG.name)
    ]
)

PROD_ITEM_CONFG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.PROD.value,
    columns = [
        ColumnConfig('number_prod', 'INTEGER', '№'),
        ColumnConfig('diametr', 'TEXT', 'Номинальный диаметр'),
        ColumnConfig('manufactureretr', 'TEXT', 'Производитель'),
        ColumnConfig('note', 'TEXT', 'Примечание'),
        ColumnConfig('invoice', 'TEXT', 'Счёт ОМТС'),
        ColumnConfig('link', 'BOOLEAN', 'Связь', is_link=True),
        ColumnConfig('parent_id', 'INTEGER',is_view=False, is_foreign_id=True, parent_table_name=GENERAL_ITEM_CONFIG.name)
    ]
)

PARAMETER_CELL_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.PARAMETER_CELL.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
        ColumnConfig('style', 'TEXT', is_unique=True)
    ]
)

PARAMETER_CELL_LINK_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.PARAMETER_CELL_LINK.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
        ColumnConfig('parent_id', 'INTEGER', is_foreign_id=True, parent_table_name=GENERAL_ITEM_CONFIG.name),
        ColumnConfig('column', 'INTEGER'),
        ColumnConfig('sid', 'INTEGER'),
        ColumnConfig('style_id', 'INTEGER'),
    ],
)

PARAMETER_HEADER_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.PARAETER_SECTION.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
        ColumnConfig('row', 'INTEGER'),
        ColumnConfig('column', 'INTEGER'),
        ColumnConfig('size', 'INTEGER'),
        ColumnConfig('is_view', 'BOOLEAN'),
        ColumnConfig('parameters', 'TEXT'),
        ColumnConfig('parent_id', 'INTEGER', is_view=False, is_foreign_id=True, parent_table_name=SPECIFICATION_CONFIG.name)
    ]
)

PARAMETER_TABLE_CONFIG = TableConfig(
    name=ENUMS.NAME_TABLE_SQL.PARAMETER_TABLE.value,
    columns=[
        ColumnConfig('id', 'INTEGER PRIMARY KEY AUTOINCREMENT', is_id=True),
        ColumnConfig('current_zoom', 'INTEGER'),
        ColumnConfig('active_row', 'INTEGER'),
        ColumnConfig('active_column', 'INTEGER'),
        ColumnConfig('parent_id', 'INTEGER', is_view=False, is_foreign_id=True, parent_table_name=SPECIFICATION_CONFIG.name)
    ]
)


if __name__ == '__main__':
    for i in INVENTOR_ITEM_CONFIG.columns:
        print(i)