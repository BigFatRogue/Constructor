from PyQt5 import QtWidgets, QtCore

from projects.specification.ui.widgets.content_widget.cw_page import PageContent


class PageEmpty(PageContent):
    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.v_layout)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setText('Ничего не выбрано')
        self.v_layout.addWidget(self.label)