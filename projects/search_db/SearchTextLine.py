from search_lib import query_get_db


def search_text_line(text):
    low = lambda s: s.lower()

    column = ('filepath', 'filename')

    full_where = []
    for string in text.split():
        where = f"func(filepath) LIKE '%{string}%'"
        # where = '(' + ' OR '.join(f"{col} LIKE '%{string}%'" for col in column) + ')'
        full_where.append(where)
    q_where = ' AND '.join(full_where)

    query = f"SELECT {', '.join(column)} FROM liberty WHERE {q_where}"

    return query_get_db(query, low)


if __name__ == '__main__':

    res = search_text_line('кран')
    print(res)