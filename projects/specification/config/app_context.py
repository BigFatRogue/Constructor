from projects.specification.config.ac_setiing import AppContextSetting
from projects.specification.config.ac_enums import AppContextEnums
from projects.specification.config.ac_single_bus import signal_bus
from projects.specification.config.ac_dataclasses import AppContextDataClasses
from projects.specification.config.ac_decorate import decorate


class __AppContext:
    def __init__(self):
        self.context_setting = AppContextSetting()
        self.single_bus = signal_bus
        self.context_enums = AppContextEnums
        self.dataclasses = AppContextDataClasses
        self.decorate = decorate


__app_context = __AppContext()
SETTING = __app_context.context_setting
SIGNAL_BUS = __app_context.single_bus
ENUMS = __app_context.context_enums
DATACLASSES = __app_context.dataclasses
DECORATE = __app_context.decorate