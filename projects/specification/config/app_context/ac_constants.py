from PyQt5 import QtCore


class AppContextConstants:
    def __init__(self):
        self.MY_FORMAT = 'scdata'
        self.QROLE_LINK_ITEM_WIDGET_TREE = QtCore.Qt.UserRole
        self.QROLE_DATA_X = QtCore.Qt.UserRole + 1
        self.QROLE_V_TEXT_ALIGN = QtCore.Qt.UserRole + 2
        self.QROLE_H_TEXT_ALIGN = QtCore.Qt.UserRole + 3