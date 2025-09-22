"""
Хеширование артикулов для добавления в БД
Хеширования либо одной строки или отсортированного списка list[str, str,...]
"""

import hashlib


def my_hash(string: str) -> str:
    if isinstance(string, (tuple, list, set)):
        string = [str(i) for i in string]
        string = ''.join(sorted(string))
    elif isinstance(string, dict):
        string = ''.join(sorted(string.keys()))

    decode_string = string.encode()

    hsh = hashlib.sha1()
    hsh.update(decode_string)

    return hsh.hexdigest()