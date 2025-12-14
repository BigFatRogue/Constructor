import os

from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.app_context.app_context import SETTING, SIGNAL_BUS, DATACLASSES

from projects.specification.ui.widgets.table_widget.tw_table import Table, TableItem

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button


class BlockControlPanel(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QFrame, table: Table):
        super().__init__(parent)
        self.table = table

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(3)
        self.setLayout(self.grid)

    def view_property(self, style: dict[str, int | float | str]) -> None:
        ...
    
    
@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class FontStyleBlock(BlockControlPanel):
    def __init__(self, parent: QtWidgets.QFrame, table: Table):
        super().__init__(parent, table)

        self.h_layout_row_1 = QtWidgets.QHBoxLayout()
        self.h_layout_row_1.setContentsMargins(0, 0, 0, 0)
        self.h_layout_row_1.setSpacing(2)
        self.grid.addLayout(self.h_layout_row_1, 0, 0, 1, 1)

        self.combo_box_font_family = QtWidgets.QFontComboBox(self)
        self.combo_box_font_family.currentFontChanged.connect(self.set_font_family_range)
        self.h_layout_row_1.addWidget(self.combo_box_font_family)

        self.combo_box_font_size = QtWidgets.QComboBox(self)
        self.__fill_font_size()
        self.combo_box_font_size.currentTextChanged.connect(self.set_font_size_range)
        self.h_layout_row_1.addWidget(self.combo_box_font_size)

        self.h_layout_row_2 = QtWidgets.QHBoxLayout()
        self.h_layout_row_2.setContentsMargins(0, 0, 0, 0)
        self.h_layout_row_2.setSpacing(2)
        self.grid.addLayout(self.h_layout_row_2, 1, 0, 1, 1, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        self.btn_bold =  QtWidgets.QPushButton(self)
        self.btn_bold.setFixedSize(20, 20)
        self.btn_bold.setText('Ж')
        font = self.btn_bold.font()
        font.setBold(True)
        self.btn_bold.setFont(font)
        self.btn_bold.setCheckable(True)
        self.btn_bold.clicked.connect(self.set_bold_range)
        self.h_layout_row_2.addWidget(self.btn_bold)

        self.btn_italic =  QtWidgets.QPushButton(self)
        self.btn_italic.setFixedSize(20, 20)
        self.btn_italic.setText('К')
        font = self.btn_italic.font()
        font.setBold(True)
        font.setItalic(True)
        self.btn_italic.setFont(font)
        self.btn_italic.setCheckable(True)
        self.btn_italic.clicked.connect(self.set_italic_range)
        self.h_layout_row_2.addWidget(self.btn_italic)

        self.btn_underline =  QtWidgets.QPushButton(self)
        self.btn_underline.setFixedSize(20, 20)
        self.btn_underline.setText('Ч')
        font = self.btn_underline.font()
        font.setBold(True)
        font.setUnderline(True)
        self.btn_underline.setFont(font)
        self.btn_underline.setCheckable(True)
        self.btn_underline.clicked.connect(self.set_underline_range)
        self.h_layout_row_2.addWidget(self.btn_underline)

        self.color_dialog = QtWidgets.QColorDialog(self)

        self.btn_background_color = QtWidgets.QPushButton(self)
        self.btn_background_color.setFixedSize(20, 20)
        self.btn_background_color.setText('P')
        self.btn_background_color.clicked.connect(lambda: self.color_dialog.getColor())
        self.h_layout_row_2.addWidget(self.btn_background_color)

    def __fill_font_size(self) -> None:
        self.combo_box_font_size.addItems(['8', '9', '10', '11', '12', '14', '16', '18', '20', '22', '24', '26', '28', '36', '48', '72'])
    
    def view_property(self, style: DATACLASSES.CELL_STYLE):
        self.combo_box_font_family.setCurrentText(style.font_family)
        self.combo_box_font_size.setCurrentText(str(style.font_size))

        check_value = lambda value: value if value is not None else False
        self.btn_bold.setChecked(check_value(style.bold))
        self.btn_italic.setChecked(check_value(style.italic))
        self.btn_underline.setChecked(check_value(style.underline))
    
    def set_font_family_range(self, value: QtGui.QFont) -> None:
        for item in self.table.selectedItems():
            font = item.font()
            font.setFamily(value.family())
            item.setFont(font)

    def set_font_size_range(self, value: str) -> None:
        for item in self.table.selectedItems():
            item: TableItem
            item.set_font_size(int(value))
    
    def set_bold_range(self, value) -> None:
        for item in self.table.selectedItems():
            font = item.font()
            font.setBold(value)
            item.setFont(font)

    def set_italic_range(self, value) -> None:
        for item in self.table.selectedItems():
            font = item.font()
            font.setItalic(value)
            item.setFont(font)

    def set_underline_range(self, value) -> None:
        for item in self.table.selectedItems():
            font = item.font()
            font.setUnderline(value)
            item.setFont(font)



@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class AlignCellBlock(BlockControlPanel):
    def __init__(self, parent: QtWidgets.QFrame, table: Table):
        super().__init__(parent, table)

        self.align_h_default = QtCore.Qt.AlignmentFlag.AlignLeft
        self.align_v_default = QtCore.Qt.AlignmentFlag.AlignTop

        self.btns_align: dict[int, QtWidgets.QPushButton] = {}

        self.group_vertical_buttons = QtWidgets.QButtonGroup(self)
        self.group_vertical_buttons.setExclusive(True)
        self.btn_align_vt = self.__create_btn(0, 0, 'align_v_top.png', QtCore.Qt.AlignmentFlag.AlignTop, self.group_vertical_buttons)
        self.btn_align_vc = self.__create_btn(0, 1, 'align_v_center.png', QtCore.Qt.AlignmentFlag.AlignVCenter, self.group_vertical_buttons)
        self.btn_align_vb = self.__create_btn(0, 2, 'align_v_bottom.png', QtCore.Qt.AlignmentFlag.AlignBottom, self.group_vertical_buttons)

        self.group_horizontal_buttons = QtWidgets.QButtonGroup(self)
        self.group_horizontal_buttons.setExclusive(True)
        self.btn_align_l = self.__create_btn(1, 0, 'align_h_left.png', QtCore.Qt.AlignmentFlag.AlignLeft, self.group_horizontal_buttons)
        self.btn_align_hc = self.__create_btn(1, 1, 'align_h_center.png', QtCore.Qt.AlignmentFlag.AlignHCenter, self.group_horizontal_buttons)
        self.btn_align_r = self.__create_btn(1, 2, 'align_h_rigth.png', QtCore.Qt.AlignmentFlag.AlignRight, self.group_horizontal_buttons)
    
    def __create_btn(self, row, column, icon_name: str, flag_align: int, group: QtWidgets.QButtonGroup) -> QtWidgets.QPushButton:
        btn_align = QtWidgets.QPushButton(self)
        btn_align.setCheckable(True)
        btn_align.setFixedSize(25, 25)
        
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(SETTING.ICO_FOLDER, icon_name))
        btn_align.setIcon(icon)

        btn_align.clicked.connect(self.set_align_range)
        
        btn_align.setProperty('flag_align', flag_align)
        
        self.btns_align[flag_align] = btn_align

        group.addButton(btn_align, column)
        self.grid.addWidget(btn_align, row, column, 1, 1)

        return btn_align

    def view_property(self, style: DATACLASSES.CELL_STYLE) -> None:
        if style.align_h is not None:
            btn = self.btns_align.get(style.align_h)
            if btn:
                btn.setChecked(True) 
        else:
            self.group_horizontal_buttons.setExclusive(False)
            for btn in self.group_horizontal_buttons.buttons():
                btn.setChecked(False)
            self.group_horizontal_buttons.setExclusive(True)

        if style.align_v is not None:
            btn = self.btns_align.get(style.align_v)
            if btn:
                btn.setChecked(True) 
        else:
            self.group_vertical_buttons.setExclusive(False)
            for btn in self.group_vertical_buttons.buttons():
                btn.setChecked(False)
            self.group_vertical_buttons.setExclusive(True)
        
    def set_align_range(self):
        align_h = [btn.property('flag_align') for btn in self.group_horizontal_buttons.buttons() if btn.isChecked()]
        align_h = align_h[0] if align_h else self.align_h_default

        align_v = [btn.property('flag_align') for btn in self.group_vertical_buttons.buttons() if btn.isChecked()]
        align_v = align_v[0] if align_v else self.align_v_default

        for item in self.table.selectedItems():
            item.setTextAlignment(align_v | align_h)

    

