import os
import shutil
import pathlib
import PyInstaller.__main__
from launcher_sitting import ROOT

if __name__ == '__main__':
    PROJECT_ROOT = str(pathlib.Path(ROOT).parent)
    
    ico = os.path.join(ROOT, r'resources\icon\icon_launcher.png')
    workpath = os.path.join(PROJECT_ROOT, 'to_exe', '_temp')
    full_file_path = os.path.join(ROOT, 'window_launcher.py')
    distpath = os.path.join(PROJECT_ROOT, 'to_exe', 'build', 'exe')
    args = ["-D", "--noconsole", f"--ico={ico}", "--name=launcher", f"--distpath={distpath}", f"--workpath={workpath}", full_file_path]
    PyInstaller.__main__.run(args)

    shutil.copytree(os.path.join(ROOT, 'resources'), os.path.join(PROJECT_ROOT, 'to_exe', 'build', 'exe', 'launcher', 'resources'))
    shutil.copy(os.path.join(ROOT, 'launcher_config.json'), os.path.join(PROJECT_ROOT, 'to_exe', 'build', 'exe', 'launcher', 'launcher_config.json'))