
from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    signal_get_data = pyqtSignal(object)
    signal_click = pyqtSignal()

    # save ловит main_window, чтобы последовательно вызвать методы сохранения у брауузера и контент области
    save = pyqtSignal() 
    back = pyqtSignal()
    forward = pyqtSignal()

    open_project = pyqtSignal()
    delele_item = pyqtSignal()
    satus_bar = pyqtSignal(str)
    delete_item_tree = pyqtSignal(object)

    load_specification_from_xlsx = pyqtSignal(str)
    select_item_browser = pyqtSignal(object)
    change_item = pyqtSignal(object)

    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    

signal_bus = SignalBus()

