import sys
import os
import re
import shutil    
import pathlib
import subprocess
import zipfile
import winshell
from win32com.client import Dispatch
from launcher_sitting import ROOT, PATH_UPDATE_RESOURCES, PATH_TEPM, PATH_SRC


def create_shortcut_in_desktop(name, filepath, dirpath):
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
    name_zip = f'Constructor v{get_actual_version()}.zip'

    if not os.path.exists(PATH_TEPM):
        os.mkdir(PATH_TEPM)
    shutil.copy(os.path.join(PATH_UPDATE_RESOURCES, name_zip), os.path.join(PATH_TEPM, name_zip))
        
    os.mkdir(PATH_SRC)
    with zipfile.ZipFile(os.path.join(PATH_TEPM, name_zip)) as zip:
        zip.extractall(PATH_SRC)
    
def create_shortcut_for_exe() -> None:
    """
    Проверка новых приложение app.exe, ...
    """
    list_application = []
    for file in os.listdir(PATH_SRC):
        path_file = pathlib.Path(file)
        if path_file.suffix == '.exe' and str(path_file)[0] != '_':
            path_from_ = os.path.join(PATH_SRC, file)
            path_to = os.path.join(ROOT, file)
            shutil.move(path_from_, path_to)
            create_shortcut_in_desktop(path_file.stem, path_to, ROOT)
    return list_application

def del_scr() -> None:
    """
    Удаление папки src с основной программой и все сгенерированных exe файлов
    """
    if os.path.exists(PATH_SRC):
        shutil.rmtree(PATH_SRC) 

    for file in os.listdir(ROOT):
        if '.exe' in file and 'launcehr' not in file:
            try:
                os.remove(os.join(ROOT, file))
            except Exception:
                ...

def check_actual_version() -> bool:
    with open(os.path.join(PATH_SRC, 'version'), 'r', encoding='utf-8') as file_version:
        version = float(file_version.read())
    return version == get_actual_version()

def run_application(full_file_name_application: str) -> None:
    try:
        if os.path.exists(full_file_name_application):
            subprocess.Popen([full_file_name_application])
    except Exception as error:
        print(error)

def main() -> None:
    if not os.path.exists(PATH_SRC):
        download_programm()
        create_shortcut_for_exe()
        return

    argv = sys.argv
    # argv = [1, 2]
    if len(argv) == 2:
        if not check_actual_version():
            del_scr()
            download_programm()
            create_shortcut_for_exe()
        run_application(argv[1])


if __name__ == '__main__':
    main()

    

