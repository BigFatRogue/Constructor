import sqlite3


class DataBase:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.conn: sqlite3.Connection = None
        self.cur: sqlite3.Cursor = None
    
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
        
        try:
            return self.conn.execute(query, *args, **kwargs)
        except Exception as erorr:
            print(erorr)
            print('Ошибка выполнения запроса')
            print(query, *args, **kwargs, sep='\n')


if __name__ == '__main__':
    import os
    p_db = os.path.join(os.path.dirname(__file__), 'DEBUG\\ALS.1642.4.2.01.00.00.000 СБ.spec')

    db = DataBase()
    db.set_path(p_db)
    db.connect()

    print(db.get_exist_tables())