import pyodbc
import sqlite3 as sql
try:
    from ..function.sitting_global import *
except ImportError:
    from sitting_global import *


def query_lst_to_str(values: tuple) -> str:
    return '(' + ", ".join(f"'{i}'".replace("''", "''''") for i in values) + ')'


def error_connect_db(func):
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except Exception:
            return ['Ошибка доступа к БД']
    return wrapper


# Connect to the database
@error_connect_db
def query_get_db(query: str) -> list:
    query_server = 'DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password+''
    conn = pyodbc.connect(query_server)

    with conn.cursor() as cursors:
        res = cursors.execute(query).fetchall()
    conn.close()

    return res


@error_connect_db
def query_set_db(query: str) -> None:
    query_server = 'DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password+''
    conn = pyodbc.connect(query_server)

    with conn.cursor() as cursors:
        cursors.execute(query)

    conn.close()


def query_db_details(query: str, path_db: str = None) -> list:
    try:
        path_db = r'C:\Users\p.golubev\Desktop\python\Автоматизация сборки\Detail_DB\db_details.db' if path_db is None else path_db

        conn = sql.connect(path_db)
        cursor = conn.cursor()

        res = cursor.execute(query).fetchall()

        conn.commit()

        return res
    except Exception:
        return ['Ошибка доступа к БД']


if __name__ == '__main__':
    query = "SELECT * FROM dbo.co_detail"
    res = query_get_db(query)
    print(res)