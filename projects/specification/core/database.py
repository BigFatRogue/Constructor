from typing import Union
import sqlite3

from projects.specification.config.table_config import TableConfigPropertyProject, TableConfigInventor, TableConfigBuy, TableConfigProd


class DataBase:
    def __init__(self):
        self.path_db = None
        self.conn = None
        self.cur = None
    
    def set_path(self, path_db: str) -> None:
        self.path_db = path_db

    def connect(self, filepath: str) -> None:
        if self.conn is None:
            self.path_db = filepath
            self.conn = sqlite3.connect(self.path_db)
            self.cur = self.conn.cursor()

    def create_table(self, table: Union[TableConfigPropertyProject, TableConfigInventor, TableConfigBuy, TableConfigProd]) -> None:
        self.cur.execute(table.create_sql())
        self.conn.commit()

    def fill_table_from_data(self, table: Union[TableConfigPropertyProject, TableConfigInventor, TableConfigBuy, TableConfigProd], data: list[list]) -> None:
        fields = table.get_fileds(is_ignore=True)

        str_filed = ','.join(fields)
        values = ','.join(['?' for _ in fields])
        for row in data:
            self.cur.execute(f'''INSERT INTO {table.name} ({str_filed}) VALUES({values})''', row)
        self.conn.commit()

    def get_list_tables(self) -> list[str]:
        list_names = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        return [i[0] for i in list_names]

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()
        self.conn = None


if __name__ == '__main__':
    import os
    p_db = os.path.join(os.path.dirname(__file__), 'DEBUG\\ALS.1642.4.2.01.00.00.000 СБ.spec')

    db = DataBase()
    db.set_path(p_db)
    db.connect()

    print(db.get_list_tables())