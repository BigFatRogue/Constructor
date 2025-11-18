from PyQt5 import QtCore
from itertools import count

count_qrole = count(start=1)

QROLE_LINK_ITEM_WIDGET_TREE = QtCore.Qt.UserRole

# QROLE_TYPE_TREE_ITEM = QtCore.Qt.UserRole                                   #TypeTreeItem
# QROLE_PROJCET_NAME = QtCore.Qt.UserRole + next(count_qrole)                 #str
# QROLE_STATUS_INIT_PROJECT_ITEM = QtCore.Qt.UserRole + next(count_qrole)     #bool
# QROLE_STATUS_SAVE_PROJECT_ITEM = QtCore.Qt.UserRole + next(count_qrole)     #bool
# QROLE_CHANGE_PROPERTY_PROJECT = QtCore.Qt.UserRole + next(count_qrole)      #dict[str, QLineEdit]
# QROLE_DATA_TREE_ITEM = QtCore.Qt.UserRole + next(count_qrole)               #dict[str, Any]
