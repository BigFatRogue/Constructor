from PyQt5 import QtCore

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.core.config_table import ColumnConfig


QROLE_LINK_ITEM_WIDGET_TREE = QtCore.Qt.UserRole
MY_FROMAT = 'scdata'