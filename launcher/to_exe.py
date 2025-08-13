import os
import PyInstaller.__main__
from launcher_sitting import ROOT

if __name__ == '__main__':
    path_icon = ""
    workpath = os.path.join(ROOT, 'build')
    full_file_path = os.path.join(ROOT, 'window_launcher.py')
    args = ["-D", "--name=launcher", f"--distpath={ROOT}", f"--workpath={workpath}", full_file_path]
    PyInstaller.__main__.run(args)