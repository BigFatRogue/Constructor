import json
import sys
import os

DEBUG = False


if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
    RESOURCES_PATH = os.path.join(PROJECT_ROOT, 'resources\\ca_resources')
else:
    PROJECT_ROOT = os.path.dirname(__file__) 
    RESOURCES_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), 'resources\\ca_resources')


with open(os.path.join(RESOURCES_PATH, 'parameters_copy_assembly.json'), 'r', encoding='utf-8') as param:
    dct: dict = json.load(param)
    ICO_FOLDER = os.path.join(RESOURCES_PATH, 'icon')
    FILTERS = dct.get('filters')
    PATH_TMP = dct.get('path_tmp')
    DEFAULT_PATH_DIALOG_WINDOW = dct.get('default_path')
    URL_INSTRUCTION_ONLINE = dct.get('url_instruction_online')
    URL_INSTRUCTION_OFFLINE = dct.get('url_instruction_offline')
    PROJECT_INVENTOR_FILENAME = dct.get('project_inventor_filename')
    PATH_PDM_RESOURCES = dct.get('path_pdm_resources')


