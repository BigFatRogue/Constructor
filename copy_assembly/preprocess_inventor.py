import os
import psutil
import pythoncom
import shutil
from time import time, sleep
import win32com.client as wc32
from typing import Union, Any
from sitting import *
from error_code import ErrorCode
from my_logging import loging_try


def check_open_process(name_process: str) -> bool:
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == name_process.lower():
            return True
    return False


def kill_process_for_pid(name_process: str) -> None:
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == name_process.lower():
            proc.kill()

def kill_process_for_pid(pid: int) -> None:
    process = psutil.Process(pid)
    process.kill()


def get_app_inventor(is_CoInitialize=False) -> Union[Any, int, ErrorCode]:
    if is_CoInitialize:
        # ...
        pythoncom.CoInitialize()

    # gen_py_path = os.path.join(os.environ["TEMP"], "gen_py")
    # if os.path.exists(gen_py_path):
    #     shutil.rmtree(gen_py_path)

    # cache_path = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "gen_py")
    # if os.path.exists(cache_path):
    #     shutil.rmtree(cache_path)

    process_name = 'Inventor.exe'
    before_pids = {p.pid for p in psutil.process_iter(['pid', 'name']) if p.name() == process_name}

    try:
        inv_app = wc32.DispatchEx("Inventor.Application")
    except Exception:
        loging_try()
        return None, None, ErrorCode.OPEN_INVENTOR_APPLICATION
    after_pids = {p.pid for p in psutil.process_iter(['pid', 'name']) if p.name() == process_name}
    pid = list(after_pids - before_pids)[0]
    return inv_app, pid, ErrorCode.SUCCESS


def get_app_inventor_2() -> Union[Any, ErrorCode]:
    """
    :return: экземпляр Inventor.Application и код ошибки
    """

    project_inventor_full_filename = os.path.join(PATH_TMP, PROJECT_INVENTOR_FILENAME)
    if check_open_process('inventor.exe'):
        try:
            # pythoncom.CoInitialize()
            inv_app = wc32.DispatchEx("Inventor.Application")
            # pythoncom.CoUninitialize()
            inv_app.DesignProjectManager.DesignProjects.AddExisting(project_inventor_full_filename).Activate()
            return inv_app, ErrorCode.SUCCESS
        except Exception:
            return None, ErrorCode.OPEN_INVENTOR_PROJECT
    else:
        # os.startfile(project_inventor_full_filename)

        t_start = time()
        while True:
            try:
                inv_app = wc32.DispatchEx('Inventor.Application')
                break
            except Exception as error:
                sleep(1)
                t_end = time()
                print(t_end - t_start, error)
                if t_end - t_start > 30:
                    return None, ErrorCode.OPEN_INVENTOR_APPLICATION
        return inv_app, ErrorCode.SUCCESS


def get_active_app_inventor() -> Union[Any, ErrorCode]:
    if check_open_process('inventor.exe'):
        inv_app = wc32.GetActiveObject('Inventor.Application')
        return inv_app, ErrorCode.SUCCESS
    return None, ErrorCode.CONNECT_INVENTOR_APPLICATION
