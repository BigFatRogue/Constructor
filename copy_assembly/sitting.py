import pathlib
import json

DEBUG = False
PROJECT_ROOT = pathlib.Path(__file__).parent

with open(f'{PROJECT_ROOT}\\resources\\parameters_copy_assembly.json', 'r', encoding='utf-8') as param:
    dct: dict = json.load(param)
    ICO_FOLDER = f'{PROJECT_ROOT}\\resources\\icon'
    FILTERS = dct.get('filters')
    PATH_TMP = dct.get('path_tmp')
    DEFAULT_PATH_DIALOG_WINDOW = dct.get('default_path')
    URL_INSTRUCTION_ONLINE = dct.get('url_instruction_online')
    URL_INSTRUCTION_OFFLINE = dct.get('url_instruction_offline')
    PROJECT_INVENTOR_FILENAME = dct.get('project_inventor_filename')
    PATH_PDM_RESOURCES = dct.get('path_pdm_resources')


