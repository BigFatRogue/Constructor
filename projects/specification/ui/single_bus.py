from PyQt5.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    signal_get_data = pyqtSignal(object)
    signal_click = pyqtSignal()

    load_specification_from_xlsx = pyqtSignal(str)
    select_item_browser = pyqtSignal(object)

    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    

signal_bus = SignalBus()

