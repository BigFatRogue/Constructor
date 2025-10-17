import os
import subprocess
import tempfile
import shutil
import pathlib
import PyInstaller.__main__
from launcher_sitting import ROOT


PROJECT_ROOT = str(pathlib.Path(ROOT).parent)


def to_exe() -> None:
    ico = os.path.join(ROOT, r'resources\icon\icon_launcher.png')
    workpath = os.path.join(PROJECT_ROOT, 'to_exe', '_temp')
    full_file_path = os.path.join(ROOT, 'window_launcher.py')
    distpath = os.path.join(PROJECT_ROOT, 'to_exe', 'build', 'exe')
    args = ["-D", "--noconsole", f"--ico={ico}", "--name=launcher", f"--distpath={distpath}", f"--workpath={workpath}", full_file_path]
    PyInstaller.__main__.run(args)

    shutil.copytree(os.path.join(ROOT, 'resources'), os.path.join(PROJECT_ROOT, 'to_exe', 'build', 'exe', 'launcher', 'resources'))
    shutil.copy(os.path.join(ROOT, 'launcher_config.json'), os.path.join(PROJECT_ROOT, 'to_exe', 'build', 'exe', 'launcher', 'launcher_config.json'))

def create_advanced_sfx_winrar(source_dir=None, output_sfx=None, out_path_unzip=None, program_name=None) -> None:
    rar_path = r"C:\Program Files\WinRAR\Rar.exe"
    
    config_content_dict = {
        'Path': out_path_unzip,
        'Title': f'setup {program_name}',
        'Text': "",
        'Setup': f'{program_name}.exe',
    }
    config_content_str = '\n'.join([f'{k}={v}' for k, v in config_content_dict.items()])
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write(config_content_str)
        config_file = f.name
    
    try:
        cmd = [
            rar_path,
            "a",
            "-sfx", 
            f"-z{config_file}",
            "-r",
            "-ep1",
            "-m5",
            output_sfx,
            f"{source_dir}\\*"
        ]
        
        subprocess.run(cmd, check=True)
        
    finally:
        if os.path.exists(config_file):
            os.remove(config_file)


def main() -> None:
    to_exe()

    create_advanced_sfx_winrar(source_dir='C:\Programs', 
                               output_sfx='launcher', 
                               program_name=r'C:\Users\p.golubev\Desktop\python\Constructor\to_exe\build\exe\launcher', 
                               out_path_unzip=os.path.join(os.path.dirname(ROOT), r'to_exe\build\zip', 'launcher')
                               ) 

if __name__ == '__main__':
    main()