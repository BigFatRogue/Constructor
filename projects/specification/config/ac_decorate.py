from PyQt5 import QtCore, QtGui, QtWidgets
from enum import Enum, auto

from projects.specification.config.app_context import signal_bus


class __UndoRedoGroup(QtCore.QObject):    
    def __init__(self):
        super().__init__(parent=None)
        self.current_widget = None
        self.btn_undo: QtWidgets.QPushButton = None
        self.btn_redo: QtWidgets.QPushButton = None

    def set_btn_undo(self, button: QtWidgets.QPushButton) -> None:
        button.setEnabled(False)
        self.btn_undo = button
        self.btn_undo.focusInEvent = self.focusInEvent(self.btn_undo.focusInEvent, self.btn_undo)
        self.btn_undo.focusOutEvent = self.focusOutEvent(self.btn_undo.focusOutEvent, self.btn_undo)
        self.btn_undo.clicked.connect(self.undo)

    def set_btn_reod(self, button: QtWidgets.QPushButton) -> None:
        button.setEnabled(False)
        self.btn_redo = button
        self.btn_redo.focusInEvent = self.focusInEvent(self.btn_redo.focusInEvent, self.btn_redo)
        self.btn_redo.focusOutEvent = self.focusOutEvent(self.btn_redo.focusOutEvent, self.btn_redo)
        self.btn_redo.clicked.connect(self.redo) 

    def focusInEvent(self, func, widget):
        def wrapper(*argv, **kwarg):
            _UNDO_REDO_GROUP.in_widget(widget)
            return func(*argv, *kwarg)
        return wrapper

    def focusOutEvent(self, func, widget):
        def wrapper(*argv, **kwarg):
            _UNDO_REDO_GROUP.out_widget(widget)
            return func(*argv, *kwarg)
        return wrapper

    def _set_enabled_buttons(self, widget) -> None:
        if widget == self.btn_redo or widget == self.btn_undo:
            return
        
        check = hasattr(widget, 'redo') and hasattr(widget, 'undo')
        if self.btn_undo:
            self.btn_undo.setEnabled(check)
        else:
            print('Клавиша UNDO не задана!')
        
        if self.btn_redo:
            self.btn_redo.setEnabled(check)
        else:
            print('Клавиша REDO не задана!')

    def in_widget(self, widget) -> None:
        self._set_enabled_buttons(widget)

        if widget == self.btn_redo or widget == self.btn_undo:
            return
        
        self.current_widget = widget
        
    def out_widget(self, widget) -> None:
        _widget = QtWidgets.QApplication.focusWidget()

        self._set_enabled_buttons(_widget)
        
        if _widget == self.btn_redo or _widget == self.btn_undo:
            return

        self.current_widget = QtWidgets.QApplication.focusWidget()
                
    def undo(self) -> None:
        if self.current_widget and hasattr(self.current_widget, 'undo'):
            self.current_widget.undo()

    def redo(self) -> None:
        if self.current_widget and hasattr(self.current_widget, 'redo'):
            self.current_widget.redo()
    
def undo_redo_focusable(cls):
    original_fucus_in = getattr(cls, 'focusInEvent', None)
    def focusInEvent(self, event: QtGui.QFocusEvent):
        _UNDO_REDO_GROUP.in_widget(self)
        return original_fucus_in(self, event)

    cls.focusInEvent = focusInEvent

    original_fucus_out = getattr(cls, 'focusOutEvent', None)
    def focusOutEvent(self, event: QtGui.QFocusEvent):
        _UNDO_REDO_GROUP.out_widget(self)
        return original_fucus_out(self, event)
    
    cls.focusOutEvent = focusOutEvent

    return cls

class __Decorate():
    def __init__(self):
        self.UNDO_REDO_GROUP = _UNDO_REDO_GROUP
        self.UNDO_REDO_FOCUSABLE = undo_redo_focusable


_UNDO_REDO_GROUP = __UndoRedoGroup()
decorate = __Decorate()