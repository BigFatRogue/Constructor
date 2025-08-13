"""
Запускает файл exe с таким же именем, но перед этим запускает launcher.exe 
"""


try:
    import os
    from pathlib import Path
    import subprocess
    from launcher_sitting import ROOT
    from launcher_logging import loging_try

    path_appliction = Path(__file__)
    stem_application = path_appliction.stem
    full_file_name_application = os.path.join(ROOT, 'src', f'{stem_application}.exe')
    full_file_name_launcher = os.path.join(ROOT, 'launcher.py')

    subprocess.call(['python', full_file_name_launcher, full_file_name_application])
except Exception:
    loging_try()