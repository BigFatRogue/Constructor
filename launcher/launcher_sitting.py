import json
import os
import sys


def get_root_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__) 

ROOT = get_root_path()
PATH_TEPM = os.path.join(ROOT, '_temp')
PATH_SRC = os.path.join(ROOT, 'src')

with open(os.path.join(ROOT, 'launcher_config.json'), 'r') as config_file:
    DICT_CONFIG: dict = json.load(config_file)

    PATH_UPDATE_RESOURCES: str = DICT_CONFIG.get("PATH_UPDATE_RESOURCES")
    LIST_APPLICATION: list = DICT_CONFIG.get('application')
    CODE_RUNNER_PY: list = DICT_CONFIG.get('code_runner_py')
 