import sqlite3


class DataBase:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.conn: sqlite3.Connection = None
        self.cur: sqlite3.Cursor = None
        self._hash_str_fields: dict[tuple, str] = {}
    
    def connect(self) -> None:
        if self.conn:
            return
        
        try:
            self.conn = sqlite3.connect(self.filepath)
            self.cur = self.conn.cursor()
        except Exception as error:
            print('Ошибка подключения к БД')
            print(error)
            print()

    def get_exist_tables(self) -> list[str]:
        self.connect()

        try:
            list_names = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        except Exception as error:
            print(error)
            print('Ошибка подключения к БД')
            return []
        
        return [i[0] for i in list_names]

    def commit(self) -> None:
        if self.conn:
            try:
                self.conn.commit()
            except Exception as error:
                print(error)
                print('Не удалсоь совершиьт Commit')

    def close(self) -> None:
        if self.conn:            
            try:
                self.conn.close()
            except Exception as error:
                print(error)
                print('Не удалсоь совершиьт Close')

            self.conn = None

    def execute(self, query, *args, **kwargs) -> sqlite3.Cursor | None:
        self.connect()
        return self.conn.execute(query, *args, **kwargs)
        # try:
        #     return self.conn.execute(query, *args, **kwargs)
        # except Exception as erorr:
        #     print(erorr)
        #     print('Ошибка выполнения запроса')
        #     print(query, *args, **kwargs, sep='\n')

    def get_last_id(self) -> int:
        """
        Последний добавленый id в БД. Должен вызывается сразу же после команды по вставки новой строки  
        
        :return: id
        :rtype: int
        """
        return self.execute('SELECT last_insert_rowid();').fetchall()[0][0]

    def _list_fields_to_str(self, fields: list[str] | tuple[str, ...]) -> str:
        if not isinstance(fields, tuple):
            fields = tuple(fields)

        if fields not in self._hash_str_fields:
            self._hash_str_fields[fields] = ', '.join(i for i in fields)

        return self._hash_str_fields[fields]

    def create(self, table_name: str, fields: list[str] | tuple[str, ...]) -> None:
        self.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({self._list_fields_to_str(fields)})")

    def insert(self, table_name: str, fields: list[str] | tuple[str, ...], values: list[str | int | float | bool], add_qurey: str = '') -> None:
        count_values = ', '.join(['?'] * len(fields))
        query = f"INSERT INTO {table_name} ({self._list_fields_to_str(fields)}) VALUES({count_values})" + add_qurey
        self.execute(query, values)

    def update(self, table_name: str, fields: list[str] | tuple[str, ...], value: list[int | float | str | bool], id_row: int = None, add_query: str = '') -> None:
        id_where = f' WHERE id={id_row}' if id_row is not None else ''
        
        str_values = ', '.join([f'{f} = ?' for f in fields])
        self.execute(f'UPDATE {table_name} SET {str_values}' + id_where + add_query, value)

    def select(self, table_table: str, fields: list[str] | tuple[str, ...], add_qurey='') -> sqlite3.Cursor:
        return self.execute(f'SELECT {self._list_fields_to_str(fields)} FROM {table_table}' + add_qurey)
    
    def delete(self, table_name: str, id_row: int = None, add_query: str = '') -> None:
        id_where = f' WHERE id={id_row}' if id_row is not None else ''
        
        self.execute(f'DELETE FROM {table_name}' + id_where + add_query)

if __name__ == '__main__':
    import os
    p_db = os.path.join(os.path.dirname(__file__), 'DEBUG\\ALS.1642.4.2.01.00.00.000 СБ.spec')

    db = DataBase()
    db.set_path(p_db)
    db.connect()

    print(db.get_exist_tables())