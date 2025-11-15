import sys
import os


if getattr(sys, 'frozen', False):
    PROJECT_ROOT = os.path.dirname(sys.executable)
    RESOURCES_PATH = os.path.join(PROJECT_ROOT, 'resources\\spec_resources')
else:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__)) 
    RESOURCES_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), 'resources\\spec_resources')

ICO_FOLDER = f'{RESOURCES_PATH}\\icon'