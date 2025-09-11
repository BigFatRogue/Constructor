"""
Запускает файл exe с таким же именем, но перед этим запускает launcher.exe 
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import traceback
import subprocess


ROOT = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__) 


def loging_try() -> None:
    path_dirname = os.path.join(ROOT, 'log_launcher')
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
    with open(os.path.join(path_dirname, f'log_launcher_error_{now_time}.txt'), 'w', encoding='utf-8') as log_error:
        for row in traceback.format_exc():
            log_error.write(row)


def main() -> None:
    try:
        path_appliction = Path(__file__)
        stem_application = path_appliction.stem
        full_file_name_application = os.path.join(ROOT, 'src', f'_{stem_application}.exe')
        full_file_name_launcher = os.path.join(ROOT, 'launcher.exe')

        # subprocess.Popen([r'C:\Users\p.golubev\Desktop\python\Constructor\venv\Scripts\python.exe', full_file_name_launcher, full_file_name_application])
        subprocess.Popen([full_file_name_launcher, full_file_name_application])
    except Exception:
        loging_try()


if __name__  == '__main__':
    main()