from projects.specification.config.app_context.ac_setiing import AppContextSetting
from projects.specification.config.app_context.ac_enums import AppContextEnums
from projects.specification.config.single_bus import SignalBus
from projects.specification.config.app_context.ac_constants import AppContextConstants



class AppContext:
    def __init__(self):
        self.context_setting = AppContextSetting()
        self.context_enums = AppContextEnums()
        self.single_bus = SignalBus()
        self.constants = AppContextConstants()


app_context = AppContext()
SETTING = app_context.context_setting
SIGNAL_BUS = app_context.single_bus
ENUMS = app_context.context_enums
CONSTANTS = app_context.constants