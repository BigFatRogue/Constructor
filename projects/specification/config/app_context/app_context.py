from projects.specification.config.app_context.ac_setiing import AppContextSetting
from projects.specification.config.app_context.ac_enums import AppContextEnums
from projects.specification.config.single_bus import SignalBus
from projects.specification.config.app_context.ac_dataclasses import AppContextDataClasses



class AppContext:
    def __init__(self):
        self.context_setting = AppContextSetting()
        self.single_bus = SignalBus()
        self.context_enums = AppContextEnums
        self.dataclasses = AppContextDataClasses


app_context = AppContext()
SETTING = app_context.context_setting
SIGNAL_BUS = app_context.single_bus
ENUMS = app_context.context_enums
DATACLASSES = app_context.dataclasses