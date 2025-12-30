from PyQt5 import QtWidgets, QtGui
from typing import Callable


def create_action(menu: QtWidgets.QMenu, title: str, triggerd: Callable=None, filepath_icon: str = None) -> QtWidgets.QAction:
    action = QtWidgets.QAction(menu)
    action.setText(title)
    if filepath_icon:
        icon = QtGui.QIcon()
        icon.addFile(filepath_icon)
        action.setIcon(icon)
    if triggerd:
        action.triggered.connect(triggerd)
    menu.addAction(action)