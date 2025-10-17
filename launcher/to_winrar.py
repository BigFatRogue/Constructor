from launcher_sitting import ROOT

import subprocess
import os
import tempfile

def create_advanced_sfx_winrar(source_dir=None, output_sfx=None, program_name='launcher'):
    source_dir = source_dir if source_dir is not None else r'C:\Users\p.golubev\Desktop\python\Constructor\to_exe\build\exe\launcher'
    output_sfx = output_sfx if output_sfx is not None else os.path.join(os.path.dirname(ROOT), r'to_exe\build\zip', program_name)   
    rar_path = r"C:\Program Files\WinRAR\Rar.exe"
    
    config_content_dict = {
        'Path': r'C:\Programs',
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


if __name__ == "__main__":
    create_advanced_sfx_winrar()