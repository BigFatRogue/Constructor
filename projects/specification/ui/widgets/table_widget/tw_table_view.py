from PyQt5 import QtCore, QtGui, QtWidgets

from projects.specification.config.app_context.app_context import DATACLASSES

from projects.specification.core.config_table import ColumnConfig, SPECIFICATION_CONFIG
from projects.specification.core.data_tables import SpecificationDataItem


class TableView(QtWidgets.QTableView):
    def __init__(self, parent):
        super().__init__(parent)

        