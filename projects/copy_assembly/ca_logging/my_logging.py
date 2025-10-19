import os
from datetime import datetime
import traceback


def loging_try() -> None:
    dirname = 'log_files_small'
    count_file = 10

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    lst_log_files = []
    for i in os.listdir(dirname):
        filepath = os.path.join(dirname, i)
        lst_log_files.append((filepath, os.path.getctime(filepath)))
    sorted_lst_log_files = sorted(lst_log_files, key=lambda item: item[1])
    count_log_files = len(sorted_lst_log_files)
    if count_log_files > count_file:
        for (path_log_file, ctime) in sorted_lst_log_files[: count_log_files - count_file]:
            os.remove(path_log_file)

    now_time = f'{datetime.today():%d-%m-%Y$%H-%M-%S}'
    with open(os.path.join(dirname, f'log_error_small_{now_time}.txt'), 'w+', encoding='utf-8') as log_error:
        for row in traceback.format_exc():
            log_error.write(row)


def loging_sys(type, value, tback) -> None:
    dirname = 'log_files'
    count_file = 10

    if not os.path.exists(dirname):
        os.mkdir(dirname)

    lst_log_files = []
    for i in os.listdir(dirname):
        filepath = os.path.join(dirname, i)
        lst_log_files.append((filepath, os.path.getctime(filepath)))
    sorted_lst_log_files = sorted(lst_log_files, key=lambda item: item[1])
    count_log_files = len(sorted_lst_log_files)
    if count_log_files > count_file:
        for (path_log_file, ctime) in sorted_lst_log_files[: count_log_files - count_file]:
            os.remove(path_log_file)

    now_time = f'{datetime.today():%d-%m-%Y$%H-%M-%S}'
    with open(os.path.join(dirname, f'log_error_{now_time}.txt'), 'w+', encoding='utf-8') as log_error:
        for row in traceback.format_exception(type, value, tback):
            log_error.write(row)

def my_excepthook(type, value, tback):
    loging_sys(type, value, tback)


if __name__ == '__main__':
    import sys
    sys.excepthook = my_excepthook
    a = 1/0
    # try:
    #     a = 1/0
    # except Exception as error:
    #     loging_sys()