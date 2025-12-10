import sys
import os
from pathlib import Path


class AppContextSetting:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.PROJECT_ROOT = os.path.dirname(sys.executable)
            self.RESOURCES_PATH = os.path.join(self.PROJECT_ROOT, 'resources\\spec_resources')
        else:
            self.PROJECT_ROOT = Path(__file__).parent.parent.parent
            self.RESOURCES_PATH = os.path.join(os.path.dirname(self.PROJECT_ROOT), 'resources\\spec_resources')

        self.ICO_FOLDER = os.path.join(self.RESOURCES_PATH, 'icon')


if __name__ == '__main__':
    print(AppContextSetting().PROJECT_ROOT)