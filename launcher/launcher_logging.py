import os
import traceback
from datetime import datetime
from launcher_sitting import ROOT

def loging_try() -> None:
    path_dirname = os.path.join(ROOT, 'log_files_small')
    count_file = 10

    if not os.path.exists(path_dirname):
        os.mkdir(path_dirname)

    lst_log_files = []
    for i in os.listdir(path_dirname):
        filepath = os.path.join(path_dirname, i)
        lst_log_files.append((filepath, os.path.getctime(filepath)))
    sorted_lst_log_files = sorted(lst_log_files, key=lambda item: item[1])
    count_log_files = len(sorted_lst_log_files)
    if count_log_files > count_file:
        for (path_log_file, ctime) in sorted_lst_log_files[: count_log_files - count_file]:
            os.remove(path_log_file)

    now_time = f'{datetime.today():%d-%m-%Y$%H-%M-%S}'
    with open(os.path.join(path_dirname, f'log_error_update{now_time}.txt'), 'w+', encoding='utf-8') as log_error:
        for row in traceback.format_exc():
            log_error.write(row)