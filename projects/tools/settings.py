import sys
import os



if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
    RESOURCES_PATH = os.path.join(PROJECT_ROOT, 'resources\\tool_resources')
else:
    PROJECT_ROOT = os.path.dirname(__file__) 
    RESOURCES_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), 'resources\\tool_resources')


DEBUG = False
ICO_FOLDER_HELPER = f'{RESOURCES_PATH}\\icon'
LAST_FILE_GEN_CONFIG = f'{RESOURCES_PATH}\\gen_conf_last_file.txt'




