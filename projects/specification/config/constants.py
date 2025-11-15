from PyQt5 import QtCore


QROLE_TYPE_TREE_ITEM = QtCore.Qt.UserRole                  #TypeTreeItem
QROLE_PROJCET_NAME = QtCore.Qt.UserRole + 1                #str
QROLE_STATUS_TREE_ITEM = QtCore.Qt.UserRole + 2            #bool
QROLE_CHANGE_PROPERTY_PROJECT = QtCore.Qt.UserRole + 3     #dict[str, QLineEdit]
QROLE_DATA_TREE_ITEM = QtCore.Qt.UserRole + 4              #dict[str, Any]