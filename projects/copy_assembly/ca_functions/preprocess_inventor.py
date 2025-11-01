import psutil
import pythoncom
import win32com.client as wc32
from typing import Union, Any
from projects.copy_assembly.settings import *
from projects.copy_assembly.ca_modes.error_code import ErrorCode
from projects.copy_assembly.ca_logging.my_logging import loging_try


def check_open_process(name_process: str) -> bool:
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == name_process.lower():
            return True
    return False


def kill_process_for_name_process(name_process: str) -> None:
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == name_process.lower():
            proc.kill()

def kill_process_for_pid(pid: int) -> None:
    process = psutil.Process(pid)
    process.kill()


def get_app_inventor(is_CoInitialize=False) -> Union[Any, int, ErrorCode]:
    if is_CoInitialize:
        pythoncom.CoInitialize()

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


def get_active_app_inventor() -> Union[Any, ErrorCode]:
    if check_open_process('inventor.exe'):
        inv_app = wc32.GetActiveObject('Inventor.Application')
        return inv_app, ErrorCode.SUCCESS
    return None, ErrorCode.CONNECT_INVENTOR_APPLICATION
