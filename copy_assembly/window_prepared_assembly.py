import sys
import json
import os
import pythoncom
import ctypes
import pathlib
from typing import Union, Optional
from PyQt5 import QtCore, QtGui, QtWidgets

from sitting import *
from error_code import ErrorCode
from mode_code import Mode
from my_logging import loging_try
from Widgets import MessegeBoxQuestion
from get_preview_file import get_bytes_png_from_inventor_file


def set_alarm_border(widget: QtWidgets.QWidget, label_error: Optional[QtWidgets.QLabel]=None) -> None:
    widget.setStyleSheet(f'#{widget.objectName()} {{border: 1px solid red}}')
    QtCore.QTimer.singleShot(2000, lambda: return_default_style_befor_alarm(widget, label_error))

def return_default_style_befor_alarm(widget: QtWidgets.QWidget, label_error: Optional[QtWidgets.QLabel]=None):
    widget.setStyleSheet('')
    if label_error:
        label_error.setStyleSheet('')
        label_error.setText('')


class PushButtonZoomPreview(QtWidgets.QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName('btn_zoom')
        self.setMaximumHeight(20)
        self.setMaximumWidth(20)
        self.setStyleSheet("#btn_zoom {border: none}")

    def setIconFromIcoName(self, ico_name) -> None:
        self.icon = QtGui.QIcon()
        self.pixmap = QtGui.QPixmap(os.path.join(ICO_FOLDER, ico_name))
        self.icon.addPixmap(self.pixmap)
        self.setIcon(self.icon)

    def enterEvent(self, a0):
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setMaximumSize(23, 23)
        self.setIconSize(QtCore.QSize(23, 23))
        return super().enterEvent(a0)

    def leaveEvent(self, a0):
        self.setMaximumSize(20, 20)
        self.setIconSize(QtCore.QSize(20, 20))
        return super().leaveEvent(a0)


class MiniViewer(QtWidgets.QWidget):
    signal_zoom = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.height_panel = 25
        self.init()

    def init(self) -> None:
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.v_layout)

        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName('lable_image_assembly')
        self.label.setStyleSheet('#lable_image_assembly {background-color: green; border: 1px solid black;}')
        self.v_layout.addWidget(self.label)
        self.visible_widgets = self.label

        self.frame_panel = QtWidgets.QFrame(self)
        self.frame_panel.setMaximumHeight(self.height_panel)
        self.h_layout = QtWidgets.QHBoxLayout(self.frame_panel)
        self.frame_panel.hide()
        
        self.btn_zoom = PushButtonZoomPreview(self.frame_panel)
        self.btn_zoom.setIconFromIcoName('icon_zoom_in.png')
        self.btn_zoom.clicked.connect(self.zoom_image)
        self.h_layout.addWidget(self.btn_zoom)
        
        self.setMouseTracking(True)

    def set_image(self, filename) -> None:
        self.icon = QtGui.QIcon()
        self.pixmap = QtGui.QPixmap(os.path.join(PATH_PDM_RESOURCES, 'prepared_assembly\\image', filename))
        self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
        self.icon.addPixmap(self.pixmap)
        self.label.setPixmap(self.pixmap)

    def set_preview(self, filename_image: str) -> None:
        self.set_image(filename_image)

    def zoom_image(self) -> None:
        self.signal_zoom.emit()
    
    def enterEvent(self, event):
        self.frame_panel.setFixedWidth(self.width())
        self.frame_panel.setFixedHeight(self.height() * 2 - 25)
        self.frame_panel.show()
        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.frame_panel.hide()
        return super().leaveEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.signal_zoom.emit()
        return super().keyPressEvent(event)


class FullViewer(MiniViewer):
    def __init__(self, parent):
        super().__init__(parent)
        self.btn_zoom.setIconFromIcoName('icon_zoom_out.png')


class EditImageLabel(QtWidgets.QLabel):
    def __init__(self, parent=None, size=(150, 150)):
        super().__init__(parent)
        self.setObjectName('EditImageLabel')
        self.setStyleSheet('#EditImageLabel {border: 1px solid black;}')
        self.path_image: Optional[str] = None
        self.bytes_image: Optional[str] = None
        self.current_size: tuple = size
        self.step_zoom: float = 1.1
        self.dragging: bool = False
        self.pixmap_label = None
        self.offset = QtCore.QPointF()
        self.position = QtCore.QPointF()

        self.setFixedSize(*self.current_size)
        self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))

    def set_pixmap_from_image(self, path_image: str) -> None:
        self.bytes_image = None if self.bytes_image is not None else self.bytes_image
        self.path_image = path_image
        self.update()

    def set_pixpam_from_bytes(self, data: bytes) -> None:
        self.path_image = None if self.path_image is not None else self.path_image
        self.bytes_image = data
        self.update()

    def wheelEvent(self, event: QtGui.QWheelEvent):
        old_current_size = tuple(i for i in self.current_size)
        if event.angleDelta().y() > 0: 
            self.current_size = tuple(i * self.step_zoom for i in self.current_size)
        else:
            self.current_size = tuple(i / self.step_zoom for i in self.current_size)
        self.position -= QtCore.QPointF(self.current_size[0] - old_current_size[0], self.current_size[1] - old_current_size[1])/2
        self.update()        
        return super().wheelEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
            self.dragging = True
            self.offset = event.pos() - self.position
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.position = event.pos() - self.offset
            self.update()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
            self.dragging = False
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        self.vh_align_image()
        return super().mouseDoubleClickEvent(event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self.path_image:
            self.pixmap_label = QtGui.QPixmap(self.path_image).scaled(*self.current_size)
            painter.drawPixmap(self.position, self.pixmap_label)
        elif self.bytes_image:
            self.pixmap_label = QtGui.QPixmap()
            self.pixmap_label.loadFromData(self.bytes_image)
            self.pixmap_label = self.pixmap_label.scaled(*self.current_size)
            if self.pixmap_label.isNull():
                self.set_pixmap_from_image(os.path.join(ICO_FOLDER, 'add_image.png'))
            painter.drawPixmap(self.position, self.pixmap_label)

    def vh_align_image(self) -> None:
        self.offset = QtCore.QPointF(0, 0)
        self.position = QtCore.QPointF(0, 0)
        self.current_size = (self.width(), self.height())
        self.update()

    def clear_image(self):
        self.path_image = None
        self.bytes_image = None
        self.update()
    
    def save_to_image(self, filepath: str) -> None:
        self.grab().toImage().save(filepath)


class AddEditAssemblyWindow(QtWidgets.QWidget):
    signal_data_add_or_edit = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.old_naming: Optional[str] = None
        self.mode = Mode.ADD_PPREPARED_ASSEMBLY
        self.__initWidgets()
        pythoncom.CoInitialize()

    def __initWidgets(self) -> None:
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ICO_FOLDER, 'CopyAssembly.png')))
        self.setFixedSize(660, 280)

        self.grid = QtWidgets.QGridLayout()
        self.grid.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.grid)

        #------------------ Privew Image Asembly ----------------------------
        self.frame_add_image_assembly = QtWidgets.QFrame(self)
        self.grid.addWidget(self.frame_add_image_assembly, 0, 0, 7, 1)

        self.vl_frame_add_image_assembly = QtWidgets.QVBoxLayout()
        self.vl_frame_add_image_assembly.setContentsMargins(0, 0, 0, 0)
        self.frame_add_image_assembly.setLayout(self.vl_frame_add_image_assembly)

        self.label_preview = EditImageLabel(self, size=(200, 200))
        self.vl_frame_add_image_assembly.addWidget(self.label_preview)

        self.label_help =  QtWidgets.QLabel(self.frame_add_image_assembly)
        self.label_help.setObjectName('label_help')
        self.label_help.setStyleSheet('#label_help {color: gray}')
        self.label_help.setWordWrap(True)
        self.label_help.setText('Зажмите ЛКМ, чтобы перемещать\nНажмите дважды ЛКМ, чтобы \nцентрировать')
        self.label_help.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.vl_frame_add_image_assembly.addWidget(self.label_help)

        self.btn_load_image = QtWidgets.QPushButton(self.frame_add_image_assembly)
        self.btn_load_image.setText('Загрузить изображение')
        self.btn_load_image.clicked.connect(self.choose_image)
        self.btn_load_image.setEnabled(False)
        self.vl_frame_add_image_assembly.addWidget(self.btn_load_image)

        #------------------ Choose Assembly ----------------------------
        self.label_choose_folder = QtWidgets.QLabel(self)
        self.label_choose_folder.setText('Выберите сборку')
        self.grid.addWidget(self.label_choose_folder, 0, 1)

        self.line_edit_choose_folder = QtWidgets.QLineEdit(self)
        self.line_edit_choose_folder.setObjectName('line_edit_choose_folder')
        self.line_edit_choose_folder.setReadOnly(True)
        self.line_edit_choose_folder.setStyleSheet('#line_edit_choose_folder {color: gray}')
        self.grid.addWidget(self.line_edit_choose_folder, 0, 2)

        self.btn_choose_folder = QtWidgets.QPushButton(self)
        self.btn_choose_folder.setText('Выбрать файл')
        self.btn_choose_folder.clicked.connect(self.choose_path_assembly)
        self.grid.addWidget(self.btn_choose_folder, 0, 3)

        #------------------ Naming  ----------------------------
        self.label_naming = QtWidgets.QLabel(self)
        self.label_naming.setText('Наименование')
        self.grid.addWidget(self.label_naming, 1, 1)

        self.line_edit_naming = QtWidgets.QLineEdit(self)
        self.line_edit_naming.setObjectName('line_edit_naming')
        self.grid.addWidget(self.line_edit_naming, 1, 2, 1, 2)
        
        #------------------ Name Assembly  ----------------------------
        self.label_name_assembly = QtWidgets.QLabel(self)
        self.label_name_assembly.setText('Текущее имя сборки')
        self.grid.addWidget(self.label_name_assembly, 2, 1)

        self.line_edit_name_assembly = QtWidgets.QLineEdit(self)
        self.line_edit_name_assembly.setObjectName('line_edit_name_assembly')
        self.line_edit_name_assembly.setReadOnly(True)
        self.line_edit_name_assembly.setStyleSheet('#line_edit_name_assembly {color: gray}')
        self.grid.addWidget(self.line_edit_name_assembly, 2, 2, 1, 2)

        #------------------ Search To  ----------------------------
        self.label_search_to = QtWidgets.QLabel(self)
        self.label_search_to.setText('Искать')
        self.grid.addWidget(self.label_search_to, 3, 1)

        self.line_edit_search_to = QtWidgets.QLineEdit(self)
        self.line_edit_search_to.setObjectName('line_edit_search_to')
        self.grid.addWidget(self.line_edit_search_to, 3, 2, 1, 2)
        
        #-------------- Lable Error ------------------
        self.label_error = QtWidgets.QLabel(self)
        self.label_error.setObjectName('label_error')
        self.label_error.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.grid.addWidget(self.label_error, 4, 1, 1, 3)

        #----------------------------------------------------------------
        v_spacer = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.grid.addItem(v_spacer, 5, 2, 1, 3)

        #------------------ Sava anc Cancel  ----------------------------
        self.btn_ok = QtWidgets.QPushButton(self)
        self.btn_ok.setText('Сохранить')
        self.btn_ok.clicked.connect(self.__click_save)
        self.grid.addWidget(self.btn_ok, 6, 2, 1, 1)

        self.btn_cancel = QtWidgets.QPushButton(self)
        self.btn_cancel.setText('Отмена')
        self.btn_cancel.clicked.connect(self.close)
        self.grid.addWidget(self.btn_cancel, 6, 3, 1, 1)
    
    def choose_path_assembly(self) -> None:
        dlg = QtWidgets.QFileDialog()
        dlg.setWindowTitle('Выберете файл')
        dlg.setNameFilter('Inventor (*.iam)')
        dlg.selectNameFilter('Inventor (*.iam)')
        dlg.exec_()
        filepath = dlg.selectedFiles()

        if filepath:
            self.btn_load_image.setEnabled(True)
            path_filepath = pathlib.Path(filepath[0])
            self.line_edit_choose_folder.setText(str(path_filepath))
            self.line_edit_name_assembly.setText(path_filepath.stem)

            png_bytes = get_bytes_png_from_inventor_file(str(path_filepath))

            self.label_preview.set_pixpam_from_bytes(png_bytes)
    
    def choose_image(self) -> None:
        dlg = QtWidgets.QFileDialog()
        dlg.setWindowTitle('Выберете файл')
        dlg.setNameFilter('Изображение (*.png *.jpg *.jpeg)')
        dlg.selectNameFilter('Изображение (*.png *.jpg *.jpeg)')
        dlg.exec_()
        filepath = dlg.selectedFiles()

        if filepath:
            self.label_preview.set_pixmap_from_image(filepath[0])

    def fill_window(self, naming: str, path_assembly: str, name_assembly: str, search_to: str) -> None:
        self.old_naming = naming
        self.line_edit_naming.setText(naming)
        self.line_edit_choose_folder.setText(path_assembly)
        self.line_edit_name_assembly.setText(name_assembly)
        self.line_edit_search_to.setText(search_to)
        self.label_preview.set_pixmap_from_image(os.path.join(PATH_PDM_RESOURCES, 'prepared_assembly\\image', f'{name_assembly}.png'))
        self.label_preview.vh_align_image()
        
    def clear_window(self) -> None:
        self.old_naming = None
        self.line_edit_naming.setText('')
        self.line_edit_choose_folder.setText('')
        self.line_edit_name_assembly.setText('')
        self.line_edit_search_to.setText('')
        self.label_preview.clear_image()

    def __show_error(self, error_code: Union[str, ErrorCode]) -> None:
        if isinstance(error_code, str):
            self.label_error.setText(error_code)
        else:
            self.label_error.setText(error_code.message)
        self.label_error.setStyleSheet('#label_error {border: 1px solid red}')

    def __clear_error(self) -> None:
        self.label_error.setText('')
        self.label_error.setStyleSheet('#label_error {border: none}')

    def __check_fill_field(self) -> ErrorCode:
        if not self.line_edit_choose_folder.text():
            set_alarm_border(self.line_edit_choose_folder, self.label_error)
            return ErrorCode.EMPTY_FIELD
        elif not self.line_edit_naming.text():
            set_alarm_border(self.line_edit_naming, self.label_error)
            return ErrorCode.EMPTY_FIELD
        elif not self.line_edit_search_to.text():
            set_alarm_border(self.line_edit_search_to, self.label_error)
            return ErrorCode.EMPTY_FIELD
        return ErrorCode.SUCCESS
    
    def __check_occurrence_search_to(self) -> bool:
        if not self.line_edit_search_to.text() in self.line_edit_name_assembly.text():
            set_alarm_border(self.line_edit_name_assembly)
            self.__show_error('Строчка для поиска должна содержаться в имени сборки')
            return False
        return  True

    def __save_preview_image(self) -> None:
        path_image = os.path.join(PATH_PDM_RESOURCES, 'prepared_assembly', 'image', f'{self.line_edit_name_assembly.text()}.png')
        self.label_preview.save_to_image(path_image)
    
    def __click_save(self) -> None:
        self.__clear_error()
        
        error_code = self.__check_fill_field()
        if  error_code != ErrorCode.SUCCESS:
            self.__show_error(error_code)
        else:
            if self.__check_occurrence_search_to():
                data = {
                    'old_naming': self.old_naming,
                    'naming': self.line_edit_naming.text(),
                    'new_naming': 
                        {self.line_edit_naming.text(): {
                            "path_assembly": self.line_edit_choose_folder.text(),
                            "name_assembly": self.line_edit_name_assembly.text(),
                            "search_to": self.line_edit_search_to.text()
                        }
                    }
                }
                self.__save_preview_image()
                self.signal_data_add_or_edit.emit(data)
                self.close()
    
    def show(self):
        if self.mode == Mode.EDIT_PPREPARED_ASSEMBLY:
            self.btn_load_image.setEnabled(True)
        elif self.mode == Mode.ADD_PPREPARED_ASSEMBLY:
            self.btn_load_image.setEnabled(False)
        return super().show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(event)


class Listwidgets(QtWidgets.QListWidget):
    signal_eidt_assembly= QtCore.pyqtSignal(str)
    signal_open_folder_assebly = QtCore.pyqtSignal(str)
    signal_del_assebly = QtCore.pyqtSignal(str)
    signal_add_assembly = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.parameter_item = (
            ('icon_edit.png', self.__edit_assembly, 'Редактировать'),
            ('icon_folder.png', self.__open_folder_assembly, 'Открыть расположение файла'),
            ('ico_del.png', self.__del_assembly, 'Удалить из списка')
        )

    def add(self, text: str) -> None:
        item = QtWidgets.QListWidgetItem()
        item.text = lambda: text
        widget = QtWidgets.QWidget()
    
        h_layout = QtWidgets.QHBoxLayout(widget)
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(h_layout)

        label = QtWidgets.QLabel()
        label.setText(text)
        h_layout.addWidget(label)

        h_spacer = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        h_layout.addItem(h_spacer)

        for (ico_name, func, tolltip) in self.parameter_item:
            self.__add_button_item(h_layout, ico_name, func, tolltip, text)
            
        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)
            
    def __add_button_item(self, layout, ico_name=None, func=None, tooltip=None, text=None) -> None:
        btn = QtWidgets.QPushButton()
        btn.setToolTip(tooltip)
        btn.setObjectName('btn_control_list_box')
        btn.setMinimumSize(20, 20)
        btn.setMaximumSize(20, 20)
        btn.clicked.connect(lambda: func(text))
        if ico_name:
            icon = QtGui.QIcon()
            pixmap = QtGui.QPixmap(os.path.join(ICO_FOLDER, ico_name))
            icon.addPixmap(pixmap)
            btn.setStyleSheet("""
                              #btn_control_list_box {
                                background-color: rgba(0, 0, 0, 0); 
                                border: none;
                              }
                              #btn_control_list_box:hover {
                                background-color: #6ac0ea;
                              }
                              """)
            btn.setIcon(icon)
        
        layout.addWidget(btn)
    
    def __edit_assembly(self, text) -> None:
        self.signal_eidt_assembly.emit(text)

    def __open_folder_assembly(self, text) -> None:
        self.signal_open_folder_assebly.emit(text)

    def __del_assembly(self, text) -> None:
        self.signal_del_assebly.emit(text)

    def add_last_item(self) -> None:
        item = QtWidgets.QListWidgetItem()
        widget = QtWidgets.QWidget()
        widget.mouseDoubleClickEvent = lambda event: self.signal_add_assembly.emit()
                
        h_layout = QtWidgets.QHBoxLayout(widget)
        h_layout.setSpacing(0)
        h_layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(h_layout)

        label_last_element = QtWidgets.QLabel()
        label_last_element.setObjectName('label_last_element')
        label_last_element.setText('Добавить элемент [Двойное нажатие]')
        label_last_element.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label_last_element.setStyleSheet('#label_last_element {color: gray}')
        h_layout.addWidget(label_last_element)

        item.setSizeHint(widget.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, widget)
    

class PreparedAssemblyWindow(QtWidgets.QWidget):
    signal_get_data = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.parameters = None
        self.current_data_assembly = None
        self.size_mini_viewer = (150, 150)
        self.window_edit_assembly = None
        
        self.initWidgets()
        self.fill_list_box()

    def initWidgets(self) -> None:
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ICO_FOLDER, 'CopyAssembly.png')))
        self.setWindowTitle('Стандартные сборки')
        self.setFixedSize(500, 300)

        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.v_layout)

        self.frame_main = QtWidgets.QFrame(self)
        self.v_layout.addWidget(self.frame_main)
        
        self.grid_main = QtWidgets.QGridLayout(self.frame_main)
        self.grid_main.setContentsMargins(0, 0, 0, 0)

        self.mini_viewer = MiniViewer(self.frame_main)
        self.mini_viewer.setMinimumSize(*self.size_mini_viewer)
        self.mini_viewer.setMaximumSize(*self.size_mini_viewer)
        self.mini_viewer.signal_zoom.connect(self.zoom_in_viewer)
        self.grid_main.addWidget(self.mini_viewer, 0, 0)

        # -------------------------- List Box -------------------------------------        
        self.list_box = Listwidgets(self)
        self.list_box.signal_eidt_assembly.connect(self.edit_assembly)
        self.list_box.signal_open_folder_assebly.connect(self.open_folder_assembly)
        self.list_box.signal_del_assebly.connect(self.del_assembly)
        self.list_box.signal_add_assembly.connect(self.add_new_assembly)
        self.list_box.setMaximumSize(99999, self.size_mini_viewer[1])
        self.list_box.clicked.connect(self.select_item_list_box)
        self.grid_main.addWidget(self.list_box, 0, 1)

        # -------------------------- Line Edits -------------------------------------
        self.label_old_name_assembly = QtWidgets.QLabel(self.frame_main)
        self.label_old_name_assembly.setText('Текущее имя сборки')
        self.grid_main.addWidget(self.label_old_name_assembly, 1, 0)

        self.line_edit_old_name_assembly = QtWidgets.QLineEdit(self)
        self.line_edit_old_name_assembly.setObjectName('line_edit_old_name_assembly')
        self.line_edit_old_name_assembly.setReadOnly(True)
        self.line_edit_old_name_assembly.setStyleSheet('#line_edit_old_name_assembly {color: gray}')
        self.grid_main.addWidget(self.line_edit_old_name_assembly, 1, 1)

        self.label_search_to = QtWidgets.QLabel(self.frame_main)
        self.label_search_to.setText('Искать')
        self.grid_main.addWidget(self.label_search_to, 2, 0)

        self.line_edit_search_to = QtWidgets.QLineEdit(self.frame_main)
        self.line_edit_search_to.setObjectName('line_edit_search_to')
        self.line_edit_search_to.setReadOnly(True)
        self.line_edit_search_to.setStyleSheet('#line_edit_search_to {color: gray}')
        self.grid_main.addWidget(self.line_edit_search_to, 2, 1)

        self.label_replace_to = QtWidgets.QLabel(self.frame_main)
        self.label_replace_to.setText('Заменить на')
        self.grid_main.addWidget(self.label_replace_to, 3, 0)

        self.line_edit_replace_to = QtWidgets.QLineEdit(self.frame_main)
        self.line_edit_replace_to.textEdited.connect(self.text_edited_replace_to)
        self.grid_main.addWidget(self.line_edit_replace_to, 3, 1)

        self.label_new_name_assemby = QtWidgets.QLabel(self.frame_main)
        self.label_new_name_assemby.setText('Имя сборки')
        self.grid_main.addWidget(self.label_new_name_assemby, 4, 0)

        self.line_edit_new_assembly_name = QtWidgets.QLineEdit(self.frame_main)
        self.line_edit_new_assembly_name.setObjectName('line_edit_new_assembly_name')
        self.grid_main.addWidget(self.line_edit_new_assembly_name, 4, 1)

        self.btn_ok = QtWidgets.QPushButton(self.frame_main)
        self.btn_ok.setText('Продолжить')
        self.btn_ok.clicked.connect(self.click_btn_ok)
        self.grid_main.addWidget(self.btn_ok, 5, 0, 1, 2)

        self.vertcal_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.grid_main.addItem(self.vertcal_spacer, 6, 0, 1, 2)

        self.full_viewer = FullViewer(self)
        self.full_viewer.signal_zoom.connect(self.zoom_out_viewer)
        self.v_layout.addWidget(self.full_viewer)
        self.full_viewer.hide()

    def load_parameters(self) -> dict:
        try:
            with open(os.path.join(PATH_PDM_RESOURCES, 'prepared_assembly\\prepared_assembly.json'), 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def update_parameters(self) -> dict:
        try:
            with open(os.path.join(PATH_PDM_RESOURCES, 'prepared_assembly\\prepared_assembly.json'), 'w', encoding='utf-8') as file:
                json.dump(self.parameters, file, ensure_ascii=False)
        except FileNotFoundError:
            ...

    def fill_list_box(self) -> None:
        if self.parameters is None:
            self.parameters = self.load_parameters()
        for key in self.parameters.keys():
            self.list_box.add(key)
        self.list_box.add_last_item()
    
    def select_item_list_box(self) -> None:
        current_item = self.list_box.currentItem()
        data = self.parameters.get(current_item.text())
        if data:
            self.fill_window(data)
        
    def fill_window(self, parameter: dict) -> None:
        name_assembly = parameter['name_assembly']
        search = parameter['search_to']
        
        self.line_edit_old_name_assembly.setText(name_assembly)
        self.line_edit_search_to.setText(search)

        self.mini_viewer.set_preview(filename_image=f'{name_assembly}.png')
    
    def text_edited_replace_to(self, text) -> None:
        item = self.list_box.currentItem()
        if item:
            data = self.parameters[item.text()]
            serach = data['search_to']
            name_assembly = data['name_assembly'] 
            self.line_edit_new_assembly_name.setText(name_assembly.replace(serach, text))

    def click_btn_ok(self) -> None:
        if self.line_edit_new_assembly_name.text():
            item = self.list_box.currentItem()
            if item:
                data = self.parameters[item.text()]
                data['replace_to'] = self.line_edit_replace_to.text()
                data['new_name_assembly'] = self.line_edit_new_assembly_name.text()
                self.current_data_assembly = data
                self.signal_get_data.emit(data)
        else:
            set_alarm_border(self.line_edit_new_assembly_name)
            msg = QtWidgets.QMessageBox(self)
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText(ErrorCode.EMPTY_FIELD.message)
            msg.setWindowTitle('Внимание')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()

    def zoom_in_viewer(self) -> None:
        self.setFixedSize(500, 500)
        self.frame_main.hide()
        self.full_viewer.show()
        key = self.parameters.get(self.list_box.currentItem().text())
        if key:
            self.full_viewer.set_image(self.parameters[key]['name_assembly'] + '.png')
        
    def zoom_out_viewer(self) -> None:
        self.setFixedSize(500, 300)
        self.frame_main.show()
        self.full_viewer.hide()
    
    def init_add_edit_assembly_window(self) -> None:
        if self.window_edit_assembly is None:
            self.window_edit_assembly = AddEditAssemblyWindow(self)
            self.window_edit_assembly.signal_data_add_or_edit.connect(self.complite_add_or_edit)

    def open_folder_assembly(self, text) -> None:
        path_assembly = pathlib.Path(self.parameters.get(text)['path_assembly'])
        os.system(f"explorer {path_assembly.parent}")

    def add_new_assembly(self) -> None:
        self.init_add_edit_assembly_window()
        self.window_edit_assembly.clear_window()
        self.window_edit_assembly.mode = Mode.ADD_PPREPARED_ASSEMBLY
        self.window_edit_assembly.label_preview.set_pixmap_from_image(os.path.join(ICO_FOLDER, 'add_image.png'))
        self.window_edit_assembly.setWindowTitle('Добавить новую сборку')
        self.window_edit_assembly.show()

    def edit_assembly(self, text) -> None:
        self.init_add_edit_assembly_window()
        self.window_edit_assembly.mode = Mode.EDIT_PPREPARED_ASSEMBLY
        self.window_edit_assembly.fill_window(naming=text, **self.parameters.get(text))
        self.window_edit_assembly.setWindowTitle('Редактировать сборку')
        self.window_edit_assembly.show()

    def del_assembly(self, text) -> None:
        msg = MessegeBoxQuestion(self, question=f'Удалить элемент {text}')
        if msg.exec() == QtWidgets.QDialog.Accepted:
            try:
                os.remove(os.path.join(PATH_PDM_RESOURCES, r'prepared_assembly\image', f'{self.parameters[text]["name_assembly"]}.png'))
            except Exception:
                loging_try()
            del self.parameters[text]
            self.update_parameters()
            self.list_box.clear()
            self.fill_list_box()

    def complite_add_or_edit(self, data: dict) -> None:
        naming = data['naming']
        old_naming = data['old_naming']

        if self.window_edit_assembly.mode == Mode.ADD_PPREPARED_ASSEMBLY:
            if naming in self.parameters:
                msg = QtWidgets.QMessageBox(self)
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText(f'Сборка с таким наименованием уже существует')
                msg.setWindowTitle('Внимание')
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec()
                return
        elif self.window_edit_assembly.mode == Mode.EDIT_PPREPARED_ASSEMBLY:
            if naming in self.parameters:
                del self.parameters[naming]
            if old_naming in self.parameters:
                del self.parameters[old_naming]
            
        self.parameters.update(data['new_naming'])
        self.update_parameters()
        self.list_box.clear()
        self.fill_list_box()
        self.check_empty_image()
        self.list_box.setCurrentRow(0)
        self.select_item_list_box()

    def check_empty_image(self) -> None:
        path_images = os.path.join(PATH_PDM_RESOURCES, r'prepared_assembly\image')
        list_not_empty_image = tuple(f'{value["name_assembly"]}.png' for value in self.parameters.values())
        for name_image in os.listdir(path_images):
            if name_image not in list_not_empty_image:
                try:
                    os.remove(os.path.join(path_images, name_image))
                except Exception:
                    loging_try()    
    
    def show(self):
        self.zoom_out_viewer()
        self.list_box.setCurrentRow(0)
        self.line_edit_replace_to.setText('')
        self.line_edit_search_to.setText('')
        self.select_item_list_box()        
        return super().show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(event)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setObjectName("centra_lwidget")

        self.vl = QtWidgets.QVBoxLayout(self.central_widget)

        self.btn = QtWidgets.QPushButton(self)
        self.btn.setText('Модальное окно') 
        self.btn.clicked.connect(self.click_btn) 
        self.vl.addWidget(self.btn)

        self.modal_window = None

        self.click_btn()

    def click_btn(self) -> None:
        if self.modal_window is None:
            self.modal_window = PreparedAssemblyWindow(self)
            # self.modal_window = AddEditAssemblyWindow(self)
        self.modal_window.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())
