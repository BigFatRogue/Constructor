import os
import pathlib
import json
import shutil
import zipfile
import PyInstaller.__main__ as PyInst


VERSION = 1.09
PROJECTS = {
    # 'CopyDrinage': 'drainage_tray',
    '_CopyAssembly': 'projects\\copy_assembly'
}

__root_pathlib = pathlib.Path(__file__).parent
TOTAL_PROJECT_ROOT = str(__root_pathlib.parent)        
TOTAL_PROJECT_NAME = str(__root_pathlib.parent.name)                    
TO_EXE_ROOT = str(__root_pathlib)

EMPTY_FILE_NAME = 'empty'
EMPTY_PY_NAME = f'{EMPTY_FILE_NAME}.py'
EMPTY_PY_FULL_FILEPATH = os.path.join(TO_EXE_ROOT, 'build', 'py', EMPTY_PY_NAME)
EMPTY_EXE_NAME = f'{EMPTY_FILE_NAME}.exe'
PATH_RESOURCES = os.path.join(TOTAL_PROJECT_ROOT, 'projects\\resources')


def init():
    path_build = pathlib.Path(TO_EXE_ROOT, 'build')
    if not path_build.exists():
        path_build.mkdir()

    for dirname in ('py', 'exe', 'zip'):
        path_bulid_to = pathlib.Path(TO_EXE_ROOT, 'build', dirname)
        if not path_bulid_to.exists():
            path_bulid_to.mkdir()

def get_import_from_py_file(pathfile: str) -> dict:
    """
    Получение всех строк импорта из файлов py
    :param pathfile: путь к файлу
    :return: множество состоящие из строк тип "import...", "from ... import ..."
    """
    dict_import = {}
    with open(pathfile, 'r', encoding='utf-8') as py:
        rows = py.readlines()
        for row in rows:
            if 'import' in row:
                dict_import[row.split()[1]] = row.strip()

    return dict_import

def get_dict_all_import_from_py_file() -> dict:
    """
    Получение импортов из всех файлов проектов указанных в словаре "PROJECTS"\n
    return: множество состоящие из строк тип "import...", "from ... import ..."
    """
    lst_file = []
    dict_all_import = {}
    for name_project, path_project in PROJECTS.items():
        for roots, folders, files in os.walk(os.path.join(TOTAL_PROJECT_ROOT, path_project)):
            for file in files:
                p = pathlib.Path(file)
                if p.suffix == '.py':
                    lst_file.append(pathlib.Path(file).stem)
                    dict_all_import.update(get_import_from_py_file(os.path.join(roots, file)))

    for file in lst_file:
        if file in dict_all_import:
            dict_all_import.pop(file)

    return dict_all_import

def get_import_from_empty() -> dict:
    """
    Получение всех строк импорта из пустого файла
    :return: {'sys': 'import sys', ...}
    """
    rows_dict = {}
    if os.path.exists(EMPTY_PY_FULL_FILEPATH):
        with open(EMPTY_PY_FULL_FILEPATH, 'r', encoding='utf-8') as py:
            rows = [i.strip() for i in py.readlines()]

        rows = rows[:rows.index('')]
        for row in rows:
            rows_dict[row.split()[1]] = row

    return rows_dict

def check_empty_exe(need_import: dict) -> bool:
    """
    Проверка на то, появились ли новые импорты после последней компиляции
    :param need_import:
    :return: True - не надо.
    """
    list_need_import = sorted(need_import.keys())
    import_from_empty = sorted(get_import_from_empty().keys())

    return list_need_import == import_from_empty

def check_and_create_empty_py():
    dict_import_from_py_file = get_dict_all_import_from_py_file()
    if dict_import_from_py_file:
        if not check_empty_exe(dict_import_from_py_file):
            with open(EMPTY_PY_FULL_FILEPATH, 'w', encoding='utf-8') as py:
                for lib, string in dict_import_from_py_file.items():
                    py.write(string + '\n')
                end_string = '\nif name == "main":\n\tprint("DONE")\n\ts = input("Press Enter to exit")'
                py.write(end_string)
                return True
    return False

def create_empty_to_exe() -> None:
    """
    Компиляция пустого файла со всеми импортами
    """
    path_exe = os.path.join(TO_EXE_ROOT, 'build', 'exe')
    if os.path.exists(path_exe):
        shutil.rmtree(path_exe)
    
    path_temp = os.path.join(TO_EXE_ROOT, '_temp')
    if not os.path.exists(path_temp):
        os.mkdir(path_temp)
    
    PyInst.run(["--noconsole", f'--name={EMPTY_FILE_NAME}', f'--distpath={path_exe}', f'--contents-directory=.', f'--workpath={path_temp}', EMPTY_PY_FULL_FILEPATH])

def clear_lib():
    """
    Очистка скомпилированных библиотек, для облегчения готового zip
    :return:
    """
    with open(os.path.join(TO_EXE_ROOT, 'resources', 'clear_config.txt'), 'r', encoding='utf-8') as config:
        for row in config.readlines():
            try:
                os.remove(row.strip())
            except Exception:
                continue

    if os.path.exists(os.path.join(TO_EXE_ROOT, 'build', 'exe', EMPTY_FILE_NAME, 'numpy')):
        shutil.rmtree(os.path.join(TO_EXE_ROOT, 'build', 'exe', EMPTY_FILE_NAME, 'numpy'))
    if os.path.exists(os.path.join(TO_EXE_ROOT, 'build', 'exe', EMPTY_FILE_NAME, 'numpy.libs')):
        shutil.rmtree(os.path.join(TO_EXE_ROOT, 'build', 'exe', EMPTY_FILE_NAME, 'numpy.libs'))

def create_file_version() -> None:
    with open(os.path.join(TO_EXE_ROOT, 'build', 'exe', TOTAL_PROJECT_NAME, 'version'), 'w', encoding='utf-8') as file_vers:
        file_vers.write(str(VERSION))

def project_to_exe() -> None:
    """
    Компиляция указанных проектов и копирование всех папок resources
    """
    path_exe_empty = os.path.join(TO_EXE_ROOT, 'build', 'exe', EMPTY_FILE_NAME)
    path_exe_result = os.path.join(TO_EXE_ROOT, 'build', 'exe', TOTAL_PROJECT_NAME)
    if os.path.exists(path_exe_result):
        shutil.rmtree(path_exe_result)
    shutil.copytree(path_exe_empty, path_exe_result)

    for name_project, path_project in PROJECTS.items():
        with open(os.path.join(TOTAL_PROJECT_ROOT, path_project, 'config_exe.json')) as config:
            dict_config = json.load(config)

        name_project = dict_config["name_project"]
        root_path_project = os.path.join(TOTAL_PROJECT_ROOT, path_project)
        ico = os.path.join(PATH_RESOURCES, dict_config["ico"])
        pyfile = os.path.join(TOTAL_PROJECT_ROOT, path_project, dict_config["pyfile"])

        exist_exe_project = os.path.join(root_path_project, name_project)
        if os.path.exists(exist_exe_project):
            shutil.rmtree(exist_exe_project)

        distpath = os.path.join(TO_EXE_ROOT, 'build', 'exe')
        path_temp = os.path.join(TO_EXE_ROOT, '_temp')
        if not os.path.exists(path_temp):
            os.mkdir(path_temp)
        
        PyInst.run(["--noconsole", f'--name={name_project}', f'--ico={ico}', f"--distpath={distpath}", f'--workpath={path_temp}', '--contents-directory=.', pyfile])

        for file in os.listdir(os.path.join(distpath, name_project)):
            if '.exe' in file:
                exist_exe_file = os.path.join(path_exe_result, file)
                if os.path.exists(exist_exe_file):
                    os.remove(exist_exe_file)
                shutil.copy(os.path.join(distpath, name_project, file), exist_exe_file)
                create_exe_runner(name_project, ico)
        shutil.copytree(PATH_RESOURCES, os.path.join(path_exe_result, 'resources'),
                        dirs_exist_ok=True)
    
    create_file_version()

    if os.path.exists(os.path.join(path_exe_result, EMPTY_EXE_NAME)):
        os.remove(os.path.join(path_exe_result, EMPTY_EXE_NAME))

def create_exe_runner(name_application: str, path_icon: str) -> None:
    full_file_path_py_runner_app = os.path.join(TO_EXE_ROOT, 'code_runner_application.py')
    full_file_path_py_application = os.path.join(TO_EXE_ROOT, 'build\\py', f'{name_application[1:]}.py')
    shutil.copy(full_file_path_py_runner_app, full_file_path_py_application)
    
    distpath = os.path.join(TO_EXE_ROOT, 'build', 'exe', TOTAL_PROJECT_NAME)

    path_temp = os.path.join(TO_EXE_ROOT, '_temp')
    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    PyInst.run(["-F", "--noconsole", f"--name={name_application[1:]}", f"--distpath={distpath}", f"--workpath={path_temp}", f"--icon={path_icon}", full_file_path_py_application])
    # shutil.rmtree(path_temp)

def create_zip() -> None:
    """
    Архивирование скомплированной папки
    """
    total_project_full_filename = os.path.join(TO_EXE_ROOT, 'build', 'exe', f'{TOTAL_PROJECT_NAME}')
    zip_full_filename = os.path.join(TO_EXE_ROOT, 'build', 'zip', f'{TOTAL_PROJECT_NAME} v{VERSION}.zip')
    exe_fullpath = os.path.join(TO_EXE_ROOT, 'build', 'exe', TOTAL_PROJECT_NAME)

    if os.path.exists(zip_full_filename):
        os.remove(zip_full_filename)

    with zipfile.ZipFile(zip_full_filename, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for roots, folders, files in os.walk(exe_fullpath):
            for file in files:
                full_path = os.path.join(roots, file)
                arcname = os.path.relpath(full_path, start=total_project_full_filename)
                zf.write(full_path, arcname=arcname)

def clear_tmp_files() -> None:
    for file in os.listdir(TOTAL_PROJECT_ROOT):
        if '.spec' in file:
            os.remove(file)
    if os.path.exists('build'):
        shutil.rmtree('build')

def main() -> None:
    init()
    if check_and_create_empty_py():
        create_empty_to_exe()
    project_to_exe()
    create_zip()
    clear_tmp_files()


if __name__ == '__main__':
    main()
    # project_to_exe()

