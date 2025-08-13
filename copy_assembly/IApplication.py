import win32com.client as wc32
import pythoncom
import psutil
import os
import shutil


class IApplication:
    __instance = None
    __application = None
    __pid = None
    
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    @staticmethod
    def __del_gen_py():
        gen_py_path = os.path.join(os.environ["TEMP"], "gen_py")
        if os.path.exists(gen_py_path):
            shutil.rmtree(gen_py_path)

        cache_path = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "gen_py")
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)

    def __run_application(self):
        # pythoncom.CoInitialize()
        
        self.process_name = 'Inventor.exe'
        before_pids = {p.pid for p in psutil.process_iter(['pid', 'name']) if p.name() == self.process_name}
        
        self.__application = wc32.DispatchEx("Inventor.Application")
        
        after_pids = {p.pid for p in psutil.process_iter(['pid', 'name']) if p.name() == self.process_name}
        self.__pid = list(after_pids - before_pids)[0]

    def run(self):
        self.__del_gen_py()
        self.__run_application()

    @property
    def application(self):
        return self.__application
    
    @property
    def pid(self):
        return self.__pid
    
    def kill_process(self) -> None:
        if self.__pid:
            psutil.Process(self.__pid).kill()