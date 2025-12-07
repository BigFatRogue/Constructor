from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.settings import *
from projects.specification.config.enums import TypeAlignText, TypeSignalFromControlPanel
from projects.specification.config.constants import *

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button



class BlockControlPanel(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QFrame):
        super().__init__(parent)

        self.current_item = None
        self.signals: dict[TypeSignalFromControlPanel, QtCore.pyqtSignal] = {}

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(3)

    def view_property(self, item) -> None:
        self.current_item = item


@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class MainBlock(BlockControlPanel):
    signal_save =  QtCore.pyqtSignal() 

    def __init__(self, parent: QtWidgets.QFrame):
        super().__init__(parent)
        
        self.signals: dict[TypeSignalFromControlPanel, QtCore.pyqtSignal] = {
            TypeSignalFromControlPanel.SAVE: self.signal_save
        }

        self.btn_save = QtWidgets.QPushButton(self)
        self.btn_save.setFixedSize(23, 23)
        self.btn_save.setToolTip('Сохранить таблицу\nCtrl + S')
        self.btn_save.setShortcut('Ctrl+S')
        self.btn_save.clicked.connect(self.click_save_table)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'save.png'))
        self.btn_save.setIcon(icon)
        self.grid.addWidget(self.btn_save, 0, 0, 1, 1)

        self.btn_back = QtWidgets.QPushButton(self)
        self.btn_back.setFixedSize(23, 23)
        self.btn_back.setToolTip('Отменить изменения\nCtrl + Z')
        self.btn_back.setShortcut('Ctrl+Z')
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'arrow_back.png'))
        self.btn_back.setIcon(icon)
        self.grid.addWidget(self.btn_back, 1, 0, 1, 1)

        self.btn_forward = QtWidgets.QPushButton(self)
        self.btn_forward.setFixedSize(23, 23)
        self.btn_forward.setToolTip('Вернуть изменения\nCtrl + Shift + Z')
        self.btn_forward.setShortcut('Ctrl+Shift+Z')
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'arrow_forward.png'))
        self.btn_forward.setIcon(icon)
        self.grid.addWidget(self.btn_forward, 1, 1, 1, 1)
    
    def click_save_table(self) -> None:
        self.signal_save.emit()
    

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class AlignCellBlock(BlockControlPanel):
    signal_set_align = QtCore.pyqtSignal(tuple)

    def __init__(self, parent: QtWidgets.QFrame):
        super().__init__(parent)

        self.signals: dict[TypeSignalFromControlPanel, QtCore.pyqtSignal] = {
            TypeSignalFromControlPanel.SET_ALIGN:  self.signal_set_align
        }

        list_btn_aligment = [
            [('align_v_top.png', TypeAlignText.V_ALIGN, QtCore.Qt.AlignmentFlag.AlignTop), 
             ('align_v_center.png', TypeAlignText.V_ALIGN, QtCore.Qt.AlignmentFlag.AlignVCenter), 
             ('align_v_bottom.png', TypeAlignText.V_ALIGN, QtCore.Qt.AlignmentFlag.AlignBottom)],
            [('align_h_left.png', TypeAlignText.H_ALIGN, QtCore.Qt.AlignmentFlag.AlignLeft), 
             ('align_h_center.png', TypeAlignText.H_ALIGN, QtCore.Qt.AlignmentFlag.AlignHCenter), 
             ('align_h_rigth.png', TypeAlignText.H_ALIGN, QtCore.Qt.AlignmentFlag.AlignRight)]
        ]

        self.dict_align_btn: dict[int, QtWidgets.QPushButton] = {}
        for y, row in enumerate(list_btn_aligment):
            group = QtWidgets.QButtonGroup(self)
            group.setExclusive(True)
            for x, (filename_icon, type_align, flag_align) in enumerate(row):
                btn_align = QtWidgets.QPushButton(self)
                btn_align.setCheckable(True)
                btn_align.setFixedSize(25, 25)
                icon = QtGui.QIcon()
                icon.addFile(os.path.join(ICO_FOLDER, filename_icon))
                btn_align.setIcon(icon)
                btn_align.clicked.connect(self.set_text_align)

                btn_align.setProperty('flag_align', flag_align)
                btn_align.setProperty('type_align', type_align)
                
                group.addButton(btn_align, x)
                self.dict_align_btn[flag_align] = btn_align
                
                self.grid.addWidget(btn_align, y, x, 1, 1)
    
    def view_property(self, tree_item: QtWidgets.QTableWidgetItem) -> None:
        super().view_property(tree_item)
        
        self.dict_align_btn[tree_item.data(QROLE_V_TEXT_ALIGN)].setChecked(True)
        self.dict_align_btn[tree_item.data(QROLE_H_TEXT_ALIGN)].setChecked(True)

    def set_text_align(self):
        btn: QtWidgets.QPushButton = self.sender()
        
        self.signal_set_align.emit((btn.property('flag_align'), btn.property('type_align')))
    
    def set_align(self, value: tuple[TypeAlignText, int]) -> None:
        flag_align, type_align = value

        if type_align == TypeAlignText.H_ALIGN:
            role = QROLE_V_TEXT_ALIGN
            role_2 = QROLE_H_TEXT_ALIGN
        else:
            role = QROLE_H_TEXT_ALIGN
            role_2 = QROLE_V_TEXT_ALIGN
        
        for item in self.selectedItems():
            item.setTextAlignment(item.data(role) | flag_align)
            item.setData(role_2, flag_align)
        
        self.signal_change_table.emit()

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class FontStyleBlock(BlockControlPanel):
    signal_font_family = QtCore.pyqtSignal()
    signal_font_size = QtCore.pyqtSignal()
    signal_bold = QtCore.pyqtSignal()
    signal_italic = QtCore.pyqtSignal()
    signal_underline = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.signals: dict[TypeSignalFromControlPanel, QtCore.pyqtSignal] = {
            TypeSignalFromControlPanel.FONT_FAMILY:  self.signal_font_family,
            TypeSignalFromControlPanel.FONT_SIZE:  self.signal_font_size,
            TypeSignalFromControlPanel.FONT_BOLD:  self.signal_bold,
            TypeSignalFromControlPanel.FONT_ITALIC:  self.signal_italic,
            TypeSignalFromControlPanel.FONT_UNDERLINE:  self.signal_underline,
        }

        self.h_layout_row_1 = QtWidgets.QHBoxLayout(self)
        self.h_layout_row_1.setContentsMargins(0, 0, 0, 0)
        self.h_layout_row_1.setSpacing(2)
        self.grid.addLayout(self.h_layout_row_1, 0, 0, 1, 1)

        self.combo_box_font_family = QtWidgets.QFontComboBox(self)
        self.h_layout_row_1.addWidget(self.combo_box_font_family)

        self.combo_box_font_size = QtWidgets.QComboBox(self)
        self.__fill_font_size()
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
        self.h_layout_row_2.addWidget(self.btn_bold)

        self.btn_italic =  QtWidgets.QPushButton(self)
        self.btn_italic.setFixedSize(20, 20)
        self.btn_italic.setText('К')
        font = self.btn_italic.font()
        font.setBold(True)
        font.setItalic(True)
        self.btn_italic.setFont(font)
        self.btn_bold.setCheckable(True)
        self.h_layout_row_2.addWidget(self.btn_italic)

        self.btn_underline =  QtWidgets.QPushButton(self)
        self.btn_underline.setFixedSize(20, 20)
        self.btn_underline.setText('Ч')
        font = self.btn_underline.font()
        font.setBold(True)
        font.setUnderline(True)
        self.btn_underline.setFont(font)
        self.btn_bold.setCheckable(True)
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

    def view_property(self, tree_item: QtWidgets.QTableWidgetItem):
        font = tree_item.font()
        self.combo_box_font_family.setCurrentFont(font)
        self.combo_box_font_size.setCurrentText(str(font.pointSize()))
        self.btn_bold.setChecked(font.bold())
        self.btn_italic.setChecked(font.italic())
        self.btn_underline.setChecked(font.underline())
