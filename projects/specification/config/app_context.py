from projects.specification.config.ac_setiing import AppContextSetting
from projects.specification.config.ac_enums import AppContextEnums
from projects.specification.config.ac_single_bus import SignalBus
from projects.specification.config.ac_dataclasses import AppContextDataClasses



class AppContext:
    def __init__(self):
        self.context_setting = AppContextSetting()
        self.single_bus = SignalBus()
        self.context_enums = AppContextEnums
        self.dataclasses = AppContextDataClasses


__app_context = AppContext()
SETTING = __app_context.context_setting
SIGNAL_BUS = __app_context.single_bus
ENUMS = __app_context.context_enums
DATACLASSES = __app_context.dataclasses