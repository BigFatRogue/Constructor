from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem


class SpecificationItem(BrowserItem): 
    signal_load_specification = QtCore.pyqtSignal(list)
    
    def __init__(self, tree: QtWidgets.QTreeWidget, project_item, text: str, path_ico: str):
        super().__init__(tree, project_item)

        self.setText(text)

        icon = QtGui.QIcon()
        icon.addFile(path_ico)
        self.setIcon(0, icon)