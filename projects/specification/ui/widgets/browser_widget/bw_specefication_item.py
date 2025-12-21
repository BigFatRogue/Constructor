from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.ui.widgets.browser_widget.bw_item import BrowserItem


class SpecificationItem(BrowserItem): 
    """
    Корневой элемент для таблиц соответствующего типа
    """
    def __init__(self, tree: QtWidgets.QTreeWidget, project_item, text: str, path_ico: str):
        super().__init__(tree, project_item)

        self.setText(text)
        self.set_icon(path_ico)

    def set_icon(self, path_ico: str) -> None:
        """
        Установка иконки слева для элемента дерева барузера
        
        :param path_ico: полный путь к иконки
        :type path_ico: str
        """
        icon = QtGui.QIcon()
        icon.addFile(path_ico)
        self.setIcon(0, icon)