from enum import Enum, auto


class Mode(Enum):
    ADD_PPREPARED_ASSEMBLY = auto()
    EDIT_PPREPARED_ASSEMBLY = auto()
    DELETE_PPREPARED_ASSEMLY = auto()
    OPEN_ASSEMBLY = auto()
    COPY_ASSEMBLY = auto()
    MAIN_WINDOW_MODE = auto()
    INTERACTIVE_HELP = auto()