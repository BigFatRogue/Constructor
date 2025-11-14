import sys
import os

def get_root_path() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__) 


PROJECT_ROOT = get_root_path()
ICO_FOLDER = f'{PROJECT_ROOT}\\resources\\icon'