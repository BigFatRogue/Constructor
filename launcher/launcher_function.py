import sys
import os
import re
import shutil    
import pathlib
import subprocess
import zipfile
import json
import winshell
from win32com.client import Dispatch
import PyInstaller.__main__
from launcher_sitting import ROOT, PATH_UPDATE_RESOURCES, LIST_APPLICATION, DICT_CONFIG, PATH_TEPM, PATH_SRC, CODE_RUNNER_PY


def create_shortcut(name, filepath, dirpath):
    desktop = winshell.desktop()
    path = os.path.join(desktop, f"{name}.lnk")
    icon = filepath
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = filepath
    shortcut.WorkingDirectory = dirpath
    shortcut.IconLocation = icon
    shortcut.save()

def get_actual_version() -> float:
    template = r'v(.*?)\.zip'
    actual_version = sorted(float(re.findall(template, version)[-1]) for version in os.listdir(PATH_UPDATE_RESOURCES))
    return actual_version[-1]

def download_programm() -> None:
    """
    Скачка архива программы и его распоковки в папке src
    """
    actual_version = get_actual_version()
    name_zip = f'Constructor v{actual_version}.zip'

    if not os.path.exists(PATH_TEPM):
        os.mkdir(PATH_TEPM)
    shutil.copy(os.path.join(PATH_UPDATE_RESOURCES, name_zip), os.path.join(PATH_TEPM, name_zip))
        
    os.mkdir(PATH_SRC)
    with zipfile.ZipFile(os.path.join(PATH_TEPM, name_zip)) as zip:
        zip.extractall(PATH_SRC)
    
def update_list_app_in_config_file(list_application: list) -> None:
    global LIST_APPLICATION
    LIST_APPLICATION = list_application
    DICT_CONFIG['application'] = LIST_APPLICATION
    with open(os.path.join(ROOT, 'launcher_config.json'), 'w') as file_config:
        json.dump(DICT_CONFIG, file_config)

def get_list_new_application() -> list[str]:
    """
    Проверка новых приложение _app.exe, ...\n
    return: [app.exe, ...]
    """
    list_application = []
    for file in os.listdir(PATH_SRC):
        path_file = pathlib.Path(file)
        if str(path_file)[0] == '_' and path_file.suffix == '.exe':
            name_application = path_file.name
            if name_application not in LIST_APPLICATION:
                list_application.append(name_application)
    return list_application

def create_runner_py(name_application: str) -> str:
    full_file_path_name_application = os.path.join(ROOT, f'{name_application}.py')
    with open(full_file_path_name_application, 'w', encoding='utf-8') as code:
        for line in CODE_RUNNER_PY:
            code.write(line + '\n')
    return full_file_path_name_application

def check_and_create_new_app_runner() -> None:
    """
    Проверки и создание новых exe лаунчеров для приложений
    ['_app.exe', ...] -> [app.py, ...] -> [app.exe, ...]
    """
    list_new_appliction = get_list_new_application()
    print(list_new_appliction)
    for filename_application in list_new_appliction:
        name_application = filename_application.replace('.exe', '')
        full_file_path_py_runner_app = create_runner_py(name_application)

        path_icon = os.path.join(PATH_SRC, 'resources\\icon', f'{name_application[1:]}.png')
        workpath = os.path.join(ROOT, 'build')

        PyInstaller.__main__.run(["-F", "--noconsole", f"--name={name_application[1:]}", f"--distpath={ROOT}", f"--workpath={workpath}", f"--icon={path_icon}", full_file_path_py_runner_app])

        os.remove(full_file_path_py_runner_app)
        os.remove(os.path.join(ROOT, f'{name_application[1:]}.spec'))
        shutil.rmtree(workpath)
        create_shortcut(name=name_application[1:], filepath=os.path.join(ROOT, f'{name_application[1:]}.exe'), dirpath=ROOT)

    update_list_app_in_config_file(list_new_appliction)

def del_scr() -> None:
    """
    Удаление папки src с основной программой и все сгенерированных exe файлов
    """
    global LIST_APPLICATION
    if os.path.exists(PATH_SRC):
        shutil.rmtree(PATH_SRC)
    
    for file_exe in LIST_APPLICATION:
        os.remove(os.path.join(ROOT, file_exe[1:]))    
    update_list_app_in_config_file([])

def check_actual_version() -> bool:
    with open(os.path.join(PATH_SRC, 'version'), 'r', encoding='utf-8') as file_version:
        version = float(file_version.read())
    
    return version == get_actual_version()

def update_appliction() -> None:
    del_scr()
    if not os.path.exists(PATH_SRC):
        download_programm()

def run_application(full_file_name_application: str) -> None:
    try:
        subprocess.Popen([full_file_name_application])
    except Exception as error:
        print(error)

def main() -> None:
    if not os.path.exists(PATH_TEPM):
        os.mkdir(PATH_TEPM)
    
    if not os.path.exists(PATH_SRC):
        download_programm()

    argv = sys.argv
    if len(argv) == 1:
        check_and_create_new_app_runner()
    if len(argv) == 2:
        update_appliction()
        check_and_create_new_app_runner()
        run_application(argv[1])

if __name__ == '__main__':
    main()

    

