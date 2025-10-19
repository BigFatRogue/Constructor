import os
import sqlite3


def create_table(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS liberty(
       detail_id INT PRIMARY KEY,
       filepath TEXT,
       filepath_lower TEXT,
       filename TEXT);
    """)
    count = 1
    for roots, folders, files in os.walk(p):
        for filename in files:
            if ('ipt' in filename or 'iam' in filename) and 'OldVersions' not in roots:
                filepath = f'{roots.replace(p, "")}\\{filename}'[1:]
                filename = filename.replace('.ipt', '').replace('.iam', '')
                values = (count, filepath, filename)

                cursor.execute(f"INSERT INTO liberty(detail_id, filepath, filename) VALUES {values}")
                count += 1


def del_table(cursor):
    cursor.execute("DELETE FROM liberty ")
    conn.commit()
    os.remove('lib.db')


def query_get_db(query: str, func=None) -> list:
    conn = sqlite3.connect(r'lib.db')
    if func is not None:
        conn.create_function('func', 1, func)

    cur = conn.cursor()
    # cur.execute('CREATE TABLE IF NOT EXISTS liberty(detail_id INT PRIMARY KEY, filepath TEXT, filename TEXT)')
    result = cur.execute(query).fetchall()
    conn.commit()

    return result


if __name__ == '__main__':
    p = r'\\192.168.1.11\PKODocs\Inventor Project\Библиотека оборудования ALS'
    conn = sqlite3.connect(r'lib.db')
    cur = conn.cursor()

    # del_table(cur)
    # create_table(cur)
    # res = cur.execute(f'-- SELECT filename, count(filename) AS count FROM liberty GROUP BY filename HAVING count > 1').fetchall()
    res = cur.execute('SELECT * FROM liberty LIMIT 10').fetchall()
    print(res)

    conn.commit()






