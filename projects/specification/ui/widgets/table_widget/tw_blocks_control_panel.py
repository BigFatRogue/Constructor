import os

from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.app_context.app_context import SETTING, SIGNAL_BUS, ENUMS, CONSTANTS

from projects.specification.ui.widgets.table_widget.tw_table_item import TableItem

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button


class BlockControlPanel(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QFrame):
        super().__init__(parent)

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(3)

    def view_property(self, style: dict[str, int | float | str]) -> None:
        ...
    

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class AlignCellBlock(BlockControlPanel):
    def __init__(self, parent: QtWidgets.QFrame):
        super().__init__(parent)

        self.current_h_align = QtCore.Qt.AlignmentFlag.AlignHCenter
        self.current_v_align = QtCore.Qt.AlignmentFlag.AlignVCenter

        list_btn_aligment = [
            [('align_v_top.png', QtCore.Qt.AlignmentFlag.AlignTop), 
             ('align_v_center.png', QtCore.Qt.AlignmentFlag.AlignVCenter), 
             ('align_v_bottom.png', QtCore.Qt.AlignmentFlag.AlignBottom)],
            [('align_h_left.png', QtCore.Qt.AlignmentFlag.AlignLeft), 
             ('align_h_center.png', QtCore.Qt.AlignmentFlag.AlignHCenter), 
             ('align_h_rigth.png', QtCore.Qt.AlignmentFlag.AlignRight)]
        ]

        self.dict_align_btn: dict[int, QtWidgets.QPushButton] = {}
        for y, row in enumerate(list_btn_aligment):
            group = QtWidgets.QButtonGroup(self)
            group.setExclusive(True)
            for x, (filename_icon, flag_align) in enumerate(row):
                btn_align = QtWidgets.QPushButton(self)
                btn_align.setCheckable(True)
                btn_align.setFixedSize(25, 25)
                icon = QtGui.QIcon()
                icon.addFile(os.path.join(SETTING.ICO_FOLDER, filename_icon))
                btn_align.setIcon(icon)
                btn_align.clicked.connect(self.set_text_align)
                btn_align.setProperty('flag_align', flag_align)
                self.dict_align_btn[flag_align] = btn_align
            
                group.addButton(btn_align, x)
                self.grid.addWidget(btn_align, y, x, 1, 1)
    
    def view_property(self, style: dict[str, int | float | str]) -> None:  
        print(style['h_align'], style['v_align'])
        self.dict_align_btn[style['h_align']].setChecked(True)
        self.dict_align_btn[style['v_align']].setChecked(True)

    def set_text_align(self):
        flag = None
        for btn in self.dict_align_btn.values():
            if btn.isChecked():
                if flag is None:
                    flag = btn.property('flag_align')
                else:
                    flag = flag | btn.property('flag_align')

        SIGNAL_BUS.set_align_cell.emit(flag)
    

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class FontStyleBlock(BlockControlPanel):
    def __init__(self, parent):
        super().__init__(parent)

        self.h_layout_row_1 = QtWidgets.QHBoxLayout(self)
        self.h_layout_row_1.setContentsMargins(0, 0, 0, 0)
        self.h_layout_row_1.setSpacing(2)
        self.grid.addLayout(self.h_layout_row_1, 0, 0, 1, 1)

        self.combo_box_font_family = QtWidgets.QFontComboBox(self)
        self.combo_box_font_family.currentFontChanged.connect(SIGNAL_BUS.font_family.emit)
        self.h_layout_row_1.addWidget(self.combo_box_font_family)

        self.combo_box_font_size = QtWidgets.QComboBox(self)
        self.__fill_font_size()
        self.combo_box_font_family.currentIndexChanged.connect(SIGNAL_BUS.font_size.emit)
        self.h_layout_row_1.addWidget(self.combo_box_font_size)

        self.h_layout_row_2 = QtWidgets.QHBoxLayout(self)
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
        self.btn_bold.clicked.connect(SIGNAL_BUS.bold.emit)
        self.h_layout_row_2.addWidget(self.btn_bold)

        self.btn_italic =  QtWidgets.QPushButton(self)
        self.btn_italic.setFixedSize(20, 20)
        self.btn_italic.setText('К')
        font = self.btn_italic.font()
        font.setBold(True)
        font.setItalic(True)
        self.btn_italic.setFont(font)
        self.btn_italic.setCheckable(True)
        self.btn_italic.clicked.connect(SIGNAL_BUS.italic.emit)
        self.h_layout_row_2.addWidget(self.btn_italic)

        self.btn_underline =  QtWidgets.QPushButton(self)
        self.btn_underline.setFixedSize(20, 20)
        self.btn_underline.setText('Ч')
        font = self.btn_underline.font()
        font.setBold(True)
        font.setUnderline(True)
        self.btn_underline.setFont(font)
        self.btn_underline.setCheckable(True)
        self.btn_underline.clicked.connect(SIGNAL_BUS.underline.emit)
        self.h_layout_row_2.addWidget(self.btn_underline)

        self.color_dialog = QtWidgets.QColorDialog(self)

        self.btn_background_color = QtWidgets.QPushButton(self)
        self.btn_background_color.setFixedSize(20, 20)
        self.btn_background_color.setText('P')
        self.btn_background_color.clicked.connect(lambda: self.color_dialog.getColor())
        self.h_layout_row_2.addWidget(self.btn_background_color)

    def __fill_font_size(self) -> None:
        self.combo_box_font_size.addItems(['8', '9', '10', '11', '12', '14', '16', '18', '20', '22', '24', '26', '28', '36', '48', '72'])
    
    def click_btn_bold(self) -> None:
        ...

    def view_property(self, style: dict[str, int | float | str]):
        # self.combo_box_font_family.setCurrentFont(font)
        # self.combo_box_font_size.setCurrentText(str(font.pointSize()))
        self.btn_bold.setChecked(style['bold'])
        self.btn_italic.setChecked(style['italic'])
        self.btn_underline.setChecked(style['underline'])
