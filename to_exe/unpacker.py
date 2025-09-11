import os
import sys
import zipfile
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import winshell
from win32com.client import Dispatch


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def init(self) -> None:
        self.extract_dir = r'C:\Programs'
        self.WIDTH, self.HEIGHT = 300, 110

        self.zipfile_name = self.get_zipfile_name()
        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) // 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) // 2
        
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}+{x}+{y}')
        self.resizable(True, False)
        self.title('Setup')

    def init_widgets(self) -> None:
        self.frame_filepath = tk.LabelFrame(self, text='Установка программы')
        self.frame_filepath.pack(fill=tk.X)

        text_label = f'{self.extract_dir}\\{self.zipfile_name}'
        self.textEdit = tk.Entry(self.frame_filepath, font=('Arial', 11))
        self.textEdit.insert(0, text_label)
        self.textEdit.grid(row=0, column=0, columnspan=2, sticky="news", pady=5, padx=5)

        self.button_set_path = tk.Button(self.frame_filepath, width=3, text='. . .', command=self.set_path,
                                         highlightcolor='#CFF1FF', highlightthickness=2)
        self.button_set_path.grid(row=0, column=2)

        self.pb = ttk.Progressbar(self.frame_filepath, length=self.WIDTH - 25)
        self.pb.grid(row=1, column=0, columnspan=3, sticky="news", pady=5, padx=5)

        self.button_unpack = tk.Button(self.frame_filepath, text='Установить', command=self.unpack)
        self.button_unpack.grid(row=2, column=1)
        self.button_close = tk.Button(self.frame_filepath, text='Закрыть', command=self.close, bg='#ff7463')
        self.button_close.grid(row=2, column=2)

        self.frame_filepath.columnconfigure((0, 1), weight=1)
        self.frame_filepath.rowconfigure(0, weight=1)

    @staticmethod
    def get_zipfile_name():
        for file in os.listdir(os.getcwd()):
            if 'zip' in file:
                return file[:file.index('.')]

    def set_path(self):
        pathfile = filedialog.askdirectory(initialdir=self.extract_dir)
        self.extract_dir = pathfile if pathfile else self.extract_dir

        self.textEdit.delete(0, tk.END)
        self.textEdit.insert(0, f'{self.extract_dir}/{self.zipfile_name}')

    def unpack(self):
        if not os.path.exists(self.extract_dir):
            os.mkdir(self.extract_dir)

        with zipfile.ZipFile(os.path.join(os.getcwd(), self.zipfile_name)) as zf:
            zf.extractall(self.extract_dir)

        for file in os.listdir(f'{self.extract_dir}\\{self.zipfile_name}'):
            if 'exe' in file:
                name_lnk = file.split(".")[0]
                filepath = f'{self.extract_dir}\\{self.zipfile_name}\\{file}'
                dirpath = f'{self.extract_dir}\\{self.zipfile_name}'
                self.create_shortcut(name_lnk, filepath, dirpath)

        self.pb.configure(value=100)

    @staticmethod
    def close():
        sys.exit()

    @staticmethod
    def create_shortcut(name, filepath, wDir):
        desktop = winshell.desktop()
        path = os.path.join(desktop, f"{name}.lnk")
        icon = filepath
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = filepath
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()

    def run(self):
        self.mainloop()


if __name__ == '__main__':
    app = Application()
    app.run()