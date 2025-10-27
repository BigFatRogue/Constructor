
from PyQt5 import QtWidgets


def decorater_set_object_name(cls, *args, **kwargs):
    def wraper(*args, **kwargs):
        instance = cls(*args, **kwargs)

        for name, widget in instance.__dict__.items():
            if isinstance(widget, QtWidgets.QWidget):
                if not widget.objectName():
                    widget.setObjectName(f'{instance.__class__.__name__}_{name}')
        return instance
    return wraper