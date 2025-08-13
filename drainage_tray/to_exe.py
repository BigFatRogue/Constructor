import os

ico = 'resources\icon\ico_drinage.ico'
command = f'pyinstaller --noconsole --name=MoveDrinage --icon={ico} WindowDrinage.py'

os.system(command)
