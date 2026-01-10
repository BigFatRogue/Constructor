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
            self.cur.execute("PRAGMA foreign_keys = ON;")
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
        # print(f'{query=}', f'args=')
        return self.conn.execute(query, *args, **kwargs)

    def _list_fields_to_str(self, fields: list[str] | tuple[str, ...]) -> str:
        if not isinstance(fields, tuple):
            fields = tuple(fields)

        if fields not in self._hash_str_fields:
            self._hash_str_fields[fields] = ', '.join(i for i in fields)

        return self._hash_str_fields[fields]

    def create(self, table_name: str, fields: list[str] | tuple[str, ...]) -> None:
        self.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({self._list_fields_to_str(fields)})")

    def insert(self, table_name: str, fields: list[str] | tuple[str, ...], values: list[str | int | float | bool], add_qurey: str = '') -> sqlite3.Cursor:
        count_values = ', '.join(['?'] * len(fields))
        query = f"INSERT INTO {table_name} ({self._list_fields_to_str(fields)}) VALUES({count_values})" + add_qurey + ' RETURNING id'
        return self.execute(query, values)

    def update(self, table_name: str, fields: list[str] | tuple[str, ...], value: list[int | float | str | bool], row_id: int = None, add_query: str = '') -> None:
        id_where = f' WHERE id={row_id}' if row_id is not None else ''
        
        str_values = ', '.join([f'{f} = ?' for f in fields])
        self.execute(f'UPDATE {table_name} SET {str_values}' + id_where + add_query, value)

    def select(self, table_table: str, fields: list[str] | tuple[str, ...], add_qurey='') -> sqlite3.Cursor:
        return self.execute(f'SELECT {self._list_fields_to_str(fields)} FROM {table_table}' + add_qurey)
    
    def delete(self, table_name: str, row_id: int = None, add_query: str = '') -> None:
        id_where = f' WHERE id={row_id}' if row_id is not None else ''
        self.execute(f'DELETE FROM {table_name}' + id_where + add_query)

if __name__ == '__main__':
    import os
    p_db = r"D:\Python\AlfaServis\Constructor\Proekt 1.scdata"

    db = DataBase(p_db)
    db.execute("DELETE FROM specification WHERE id=1")
    db.commit()
    db.close()
    # print(db.get_exist_tables())