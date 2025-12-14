import os
from PyQt5 import QtWidgets, QtCore, QtGui

from projects.specification.config.app_context.app_context import SETTING, ENUMS

from projects.specification.ui.widgets.table_widget.tw_header import HeaderWithOverlayWidgets
from projects.specification.ui.widgets.table_widget.tw_popup_order_column import PopupOrder


class ButtonHorizontalHeader(QtWidgets.QPushButton):
    signal_click = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)

        self.index_section: int = None
        self.is_checked = False
        self.state_sorted = ENUMS.STATE_SORTED_COLUMN.EMPTY 

        self.resize(22, 22)
        self.setCheckable(True)
        
        self.dict_icon = {}
        for icon_name, state, tool_tip in zip(
            ('filter.png', 'filter_az.png', 'filter_za.png'),
            (ENUMS.STATE_SORTED_COLUMN.EMPTY, ENUMS.STATE_SORTED_COLUMN.SORTED, ENUMS.STATE_SORTED_COLUMN.REVERSE),
            ('Установить фильтр', 'Установлен фильтр от А до Я', 'Установлен фильтр от Я до А')
            ):

            ico = QtGui.QIcon()
            ico.addFile(os.path.join(SETTING.ICO_FOLDER, icon_name))
            self.dict_icon[state] = (ico, tool_tip)
        self.clicked.connect(lambda: self.signal_click.emit(self.index_section))
        self.reset_view_sorted()

    def set_sorted_state(self, state) -> None:
        self.state_sorted = state
        ico, tool_tip = self.dict_icon[state]
        self.setIcon(ico)
        self.setToolTip(tool_tip)
    
    def reset_view_sorted(self) -> None:
        self.set_sorted_state(ENUMS.STATE_SORTED_COLUMN.EMPTY)


class HorizontalWithOverlayWidgets(HeaderWithOverlayWidgets):
    def __init__(self, table: QtWidgets.QTableWidget):
        super().__init__(QtCore.Qt.Orientation.Horizontal, table)
        table.horizontalScrollBar().valueChanged.connect(self._update_widgets)

        self.popup_order = PopupOrder(self.table)
    
    def add_widget(self, widget: ButtonHorizontalHeader):
        super().add_widget(widget)

        widget.clicked.connect(self.show_popup)
    
    def show_popup(self) -> None:
        self.popup_order.show(self.sender())


    