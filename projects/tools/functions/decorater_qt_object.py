from PyQt5 import QtWidgets, QtGui, QtCore


def decorater_set_object_name(cls, *args, **kwargs):
    def wraper(*args, **kwargs):
        instance = cls(*args, **kwargs)

        for name, widget in instance.__dict__.items():
            if isinstance(widget, QtWidgets.QWidget):
                if not widget.objectName():
                    widget.setObjectName(f'{instance.__class__.__name__}_{name}')
        return instance
    return wraper


def decorater_set_hand_cursor_button(list_type_widget: list[QtWidgets.QWidget]):
    def decorator(cls, *args, **kwargs): 
        def wraper(*args, **kwargs):
            instance = cls(*args, **kwargs)

            for name, widget in instance.__dict__.items():
                for tp_widget in list_type_widget:
                    if isinstance(widget, tp_widget):
                        widget.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            return instance
        return wraper
    return decorator