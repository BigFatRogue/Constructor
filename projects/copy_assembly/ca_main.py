import shutil
import sys
import ctypes
import os
from pathlib import Path
from typing import Optional, Any
from PyQt5 import QtCore, QtGui, QtWidgets

from settings import *

from ca_widgets.h_line_separate import QHLineSeparate
from ca_widgets.messege_box_question import MessegeBoxQuestion
from ca_widgets.helper_interactive import HelperInteractive

from ca_other_window.window_prepared_assembly import PreparedAssemblyWindow
from ca_other_window.window_rules import WindowsViewerRules

from ca_modes.error_code import ErrorCode
from ca_modes.mode_code import Mode

from ca_logging.my_logging import loging_sys, loging_try

from ca_functions.logger_changes_qtree import LoggerChangesQTree, TypeItemQTree
from ca_functions.preprocess_inventor import get_app_inventor, kill_process_for_pid
from ca_functions.copy_and_rename_assembly import move_file_inventor_project, copy_file_assembly, get_tree_assembly, copy_and_rename_file_assembly, replace_reference_file, rename_display_name_and_set_rules, rename_component_name_in_assembly, create_folder_rename_assembly
from ca_functions.my_function import strip_path
from ca_functions.RowCounter import RowCounter


class IThread(QtCore.QObject):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance        

    signal_dict_assembly = QtCore.pyqtSignal(dict)
    signal_text_pb = QtCore.pyqtSignal(str)
    signal_pb = QtCore.pyqtSignal(bool)
    signal_is_prepared = QtCore.pyqtSignal(bool)
    signal_error = QtCore.pyqtSignal(ErrorCode)
    signal_complite_thread = QtCore.pyqtSignal()
    signal_complite_copy_assembly = QtCore.pyqtSignal(str)
    signal_close = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__init_variable()
        
        self._thread = QtCore.QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.run)
        self._thread.start()
        
    def __init_variable(self) -> None:
        self.__mode = None
        self.__app: Optional[Any] = None
        self.pid: Optional[int] = None
        self.__options_open_document: Optional[Any] = None
        self.__current_path_project: Optional[str] = None
        self.__tmp_assembly_path: Optional[str] = None
    
    def __init_app(self) -> None:
        if self.__app is None:
            self.__app, self.pid, error_code = get_app_inventor(self.__is_CoInitialize)
            self.signal_error.emit(error_code)
    
    def __init_options_open_document(self) -> None:
        if self.__app:
            try:
                self.__app.SilentOperation = True
                self.__options_open_document = self.__app.TransientObjects.CreateNameValueMap()
                self.__options_open_document.Add("SkipAllUnresolvedFiles", True)
            except Exception:
                loging_try()
                self.signal_error.emit(ErrorCode.OPEN_INVENTOR_APPLICATION)
                return
        else:
            self.signal_error.emit(ErrorCode.OPEN_INVENTOR_APPLICATION)

    def __open_project(self, path_project: Optional[str]=None) -> None:
        if self.__app:
            if path_project is None:
                path_project = os.path.join(PATH_TMP, PROJECT_INVENTOR_FILENAME)
            try:
                self.__current_path_project = self.__app.DesignProjectManager.ActiveDesignProject.fullFileName
                self.__app.DesignProjectManager.DesignProjects.AddExisting(path_project).Activate()
            except Exception:
                loging_try()
                self.signal_error.emit(ErrorCode.OPEN_INVENTOR_PROJECT)
        else:
            self.signal_error.emit(ErrorCode.OPEN_INVENTOR_APPLICATION)

    @QtCore.pyqtSlot(str, bool, bool, bool)
    def init_open_assembly(self, full_filename_assembly: str, is_update=False, is_prepared=False, is_CoInitialize=False) -> None:
        self.__mode = Mode.OPEN_ASSEMBLY
        self.__full_filename_assembly: Optional[str] = full_filename_assembly
        self.__is_update: Optional[bool] = is_update
        self.__is_prepared: Optional[bool] = is_prepared
        self.__is_CoInitialize: Optional[bool] = is_CoInitialize

    def __clear_variable_open(self) -> None:
        self.__full_filename_assembly = None
        self.__is_update = None
        self.__is_prepared = None
        self.__is_CoInitialize = None

    def __open_assembly(self) -> None:
        move_file_inventor_project()        

        self.signal_text_pb.emit('Запуск Inventor...')
        if not self.__full_filename_assembly:
            return
        
        self.__init_app()
        self.__open_project()
        self.__init_options_open_document()
        
        if self.__app:
            if not self.__is_update:
                self.signal_text_pb.emit(f'Копирование папки {self.__full_filename_assembly}...')
                self.__tmp_assembly_path = copy_file_assembly(full_filename=self.__full_filename_assembly)
            else:
                self.__tmp_assembly_path = self.__full_filename_assembly

            self.signal_text_pb.emit(f'Загрузка и чтение сборки...')
            dict_assembly, document = get_tree_assembly(application=self.__app, options_open_document=self.__options_open_document, full_filename_assembly=self.__tmp_assembly_path)
            
            self.signal_text_pb.emit('Чтение правил...')
            document.Close()

            if DEBUG:
                with open(os.path.join(Path(PROJECT_ROOT).parent, r'DEBUG\data_assembly.txt'), 'w', encoding='utf-8') as file_data_assembly: 
                    file_data_assembly.write(str(dict_assembly))
        else:
            self.signal_error.emit(ErrorCode.OPEN_INVENTOR_APPLICATION)
        
        self.signal_complite_thread.emit()
        self.signal_dict_assembly.emit(dict_assembly)
        self.signal_is_prepared.emit(self.__is_prepared)
        self.__clear_variable_open()

    @QtCore.pyqtSlot(dict)
    def init_copy_assembly(self, dict_assembly: dict) -> None:
        self.__mode = Mode.COPY_ASSEMBLY
        self.__dict_assembly = dict_assembly

        if DEBUG:
            with open(r'DEBUG\data_from_application.txt', 'w', encoding='utf-8') as file_data_assembly: 
                file_data_assembly.write(str(dict_assembly))

    def __claer_variable_copy(self) -> None:
        self.__dict_assembly = None

    def __copy_assembly(self) -> None:
        if not self.__dict_assembly:
            return
        if self.__app:
            self.signal_text_pb.emit('Процесс копирования...')
            copy_and_rename_file_assembly(dict_from_application=self.__dict_assembly)

            new_full_filename_assembly = os.path.join(self.__dict_assembly['new_root_assembly'], self.__dict_assembly['new_name_assembly'])
            self.signal_text_pb.emit(f'Загрузка {new_full_filename_assembly}...')
            doc = self.__app.Documents.OpenWithOptions(new_full_filename_assembly, self.__options_open_document, False)
            
            self.signal_text_pb.emit(f'Замена ссылок файлов...')
            replace_reference_file(application=self.__app, document=doc, options_open_document=self.__options_open_document, dict_from_application=self.__dict_assembly)
            
            self.signal_text_pb.emit(f'Переименовывание названий компонентов...')
            rename_display_name_and_set_rules(application=self.__app, document=doc, options_open_document=self.__options_open_document, dict_from_application=self.__dict_assembly)
            rename_component_name_in_assembly(document=doc, dict_from_application=self.__dict_assembly)

            doc.Save()
            doc.Close()

            self.signal_complite_copy_assembly.emit(self.__dict_assembly['new_root_assembly'])
        else:
            self.signal_error.emit(ErrorCode.CONNECT_INVENTOR_APPLICATION)
        self.__claer_variable_copy()
        self.signal_complite_thread.emit()
    
    def remove_tmp_dir(self) -> None:
        if self.__tmp_assembly_path:
            dir_name = os.path.dirname(self.__tmp_assembly_path)
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)

    @QtCore.pyqtSlot()
    def run(self) -> None:
        if self.__mode == Mode.OPEN_ASSEMBLY:
            self.signal_pb.emit(True)
            self.__open_assembly()
        elif self.__mode == Mode.COPY_ASSEMBLY:
            self.signal_pb.emit(True)
            self.__copy_assembly()
        self.signal_pb.emit(False)

    @QtCore.pyqtSlot()
    def close(self) -> None:
        if self.__current_path_project:
            try:
                self.__app.Documents.CloseAll()
                self.__app.DesignProjectManager.DesignProjects.AddExisting(self.__current_path_project).Activate()
            except Exception as error:
                loging_try()
        self.signal_close.emit()


class LoadRingWidget(QtWidgets.QWidget):
    def __init__(self, parent, color, ring_offset_x, ring_offset_y, max_size):
        super().__init__(parent)
        self.parent = parent

        self.max_size = max_size
        self.setMaximumSize(*max_size)
        self.setMinimumSize(*max_size)

        self.ring_offset_x = ring_offset_x
        self.ring_offset_y = ring_offset_y
        self.color = QtGui.QColor(100, 255, 100, 200) if color is None else QtGui.QColor(*color)

        self.angle = 0
        self.len_arc = 0
        self.flag_direction = False
        self.flag_start = True

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_angle)

    def update_angle(self):
        if self.len_arc in (0, 360):
            self.flag_direction = not self.flag_direction

        self.len_arc += 5 if self.flag_direction else -5
        self.angle += 5 if self.flag_direction else 10

        self.update()  # вызываем перерисовку виджета

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        color = QtGui.QColor(100, 255, 100, 200)
        pen = QtGui.QPen(color, self.width()*0.15, QtCore.Qt.SolidLine)
        bruh = QtGui.QBrush(color)
        painter.setPen(pen)
        painter.setBrush(bruh)

        ring_offset_x = self.max_size[0] * self.ring_offset_x
        ring_offset_y = self.max_size[1] * self.ring_offset_y
        ring_width = self.max_size[0] * (1 - self.ring_offset_x * 2)
        ring_height = self.max_size[1] * (1 - self.ring_offset_y * 2)
        rect_ring = (ring_offset_x, ring_offset_y, ring_width, ring_height)
        painter.drawArc(QtCore.QRectF(*rect_ring), self.angle * 16, self.len_arc * 16)

    def start_load(self):
        self.timer.start(30)  # обновляем каждые 30 миллисекунд для плавной анимации

    def stop_load(self):
        self.timer.stop()


class LoadRing(QtWidgets.QWidget):
    def __init__(self, parent, color=None, ring_offset_x=0.2, ring_offset_y=0.2, max_size=(25, 25)):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setMaximumSize(*max_size)
        self.setMinimumSize(*max_size)

        self.label_icon_ok = QtWidgets.QLabel(self)
        pixpmap = QtGui.QPixmap(os.path.join(ICO_FOLDER, 'load_ok.png'))
        self.label_icon_ok.setPixmap(pixpmap)
        self.label_icon_ok.setScaledContents(True)
        self.label_icon_ok.setMaximumSize(*(int(m * (1 - ring_offset_x)) for m in max_size))
        self.label_icon_ok.setMinimumSize(*(int(m * (1 - ring_offset_y)) for m in max_size))
        self.label_icon_ok.setMargin(2)
        layout.addWidget(self.label_icon_ok)

        self.load_ring_widget = LoadRingWidget(self, color=color,
                                               ring_offset_x=ring_offset_x, ring_offset_y=ring_offset_y,
                                               max_size=max_size)
        self.load_ring_widget.setMaximumSize(*max_size)
        layout.addWidget(self.load_ring_widget)

    def start_load(self):
        self.load_ring_widget.show()
        self.label_icon_ok.hide()
        self.load_ring_widget.start_load()

    def stop_load(self):
        self.load_ring_widget.hide()
        self.label_icon_ok.show()
        self.load_ring_widget.stop_load()


class HighlightDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtWidgets.QTreeView):
        super().__init__(parent)
        self.parent = parent
        self.search_text = ''
        self.mode_register = True

    def paint(self, painter, option, index):
        painter.fillRect(QtCore.QRect(option.rect.x(), option.rect.y(), option.rect.width(),  option.rect.height()), index.data(QtCore.Qt.BackgroundRole))
        text_current: str = index.data()
        text_search: str = self.search_text

        if text_current and text_current:
            if not self.mode_register:
                text_search = text_search.lower()
                text_current = text_current.lower()

            if text_search and text_current and text_search in text_current:
                start = 0
                l = len(text_search)
                indxs = []
                for _ in range(text_current.count(text_search)):
                    indx = text_current[start:].find(text_search)
                    indxs.append((indx + start, indx + l + start))
                    start += indx + 1

                for idx_start, idx_end in indxs:
                    x_offset = option.rect.x() + option.fontMetrics.horizontalAdvance(text_current[: idx_start])
                    width = option.fontMetrics.horizontalAdvance(text_current[idx_start: idx_end + 1])
                    
                    icon_width = option.decorationSize.width() * 1.5 if index.data(QtCore.Qt.DecorationRole) else 0

                    x_offset += icon_width + self.parent.style().pixelMetric(QtWidgets.QStyle.PM_FocusFrameHMargin)
                    rect = QtCore.QRect(x_offset, option.rect.y(), width,  option.rect.height())
                    painter.fillRect(rect, QtGui.QBrush(QtGui.QColor(255, 255, 0)))
        
        super().paint(painter, option, index)

    def setSearchText(self, text):
        self.search_text = text
    
    def setModeRegister(self, value: bool) -> None:
        self.mode_register = value
    

class ButtonShowRules(QtWidgets.QPushButton):
    signal_remove_rule = QtCore.pyqtSignal()

    def __init__(self, parent, item_display_name: QtGui.QStandardItem, item_rules_ilogic: QtGui.QStandardItem):
        super().__init__(parent)

        self.item_display_name = item_display_name
        self.item_rules_ilogic = item_rules_ilogic

        self.setObjectName('ButtonShowRules')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_rules.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setIcon(icon)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.menu = QtWidgets.QMenu(self)
        action = self.menu.addAction('Удалить правило')
        action.triggered.connect(self.remove_rule)

    def show_context_menu(self, point) -> None:
        self.menu.exec(self.mapToGlobal(point))

    def remove_rule(self) -> None:
        msg = MessegeBoxQuestion(self, question='Удалить правило?')
        if msg.exec() == QtWidgets.QDialog.Accepted:
            self.item_rules_ilogic.rules = {}
            self.hide()
            

class Tree(QtWidgets.QTreeView):
    signal_click_btn_rules = QtCore.pyqtSignal(tuple)

    def __init__(self, parent, model: QtGui.QStandardItemModel, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setObjectName('Tree')
        self.setModel(model)
        self.model().itemChanged.connect(self.on_item_changed)
        self.logger_changes = LoggerChangesQTree()

    def on_item_changed(self, item: QtGui.QStandardItem) -> None:
        self.logger_changes.add_change(item, item.old_value, item.text())
        item.old_value = item.text()      

    def populatet_tree(self, children: dict, parent=None, row=0) -> int:
        if parent is None:
            parent = self.model().invisibleRootItem()

        for filepath, value in children.items():
            img = value['image']
            icon = QtGui.QIcon()
            icon_path = os.path.join(ICO_FOLDER, img)
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
         
            component_name = value['component_name']
            item_component_name = QtGui.QStandardItem(component_name)
            item_component_name.setIcon(icon)
            setattr(item_component_name, 'name', component_name)
            setattr(item_component_name, 'old_value', component_name)

            display_name = value['display_name']
            item_display_name = QtGui.QStandardItem(display_name)
            setattr(item_display_name, 'name', display_name)
            setattr(item_display_name, 'old_value', display_name)
            
            # ALS.000.itp[-4] -> ALS.000 
            short_filename = value['short_filename'][:-4]
            item_short_filename = QtGui.QStandardItem(short_filename)
            setattr(item_short_filename, 'name', short_filename)
            setattr(item_short_filename, 'type_file', value['type_file'])
            setattr(item_short_filename, 'old_value', short_filename)

            item_rules_ilogic = QtGui.QStandardItem('')
            item_rules_ilogic.setEditable(False)
            setattr(item_rules_ilogic, 'rules', value['rules'])

            list_item = [item_component_name, item_display_name, item_short_filename, item_rules_ilogic]
            for item in list_item:
                item.setData(QtGui.QColor(255, 255, 255), QtCore.Qt.BackgroundRole)

            parent.appendRow(list_item)
            row += 1

            if value['rules']:
                btn_get_rules = ButtonShowRules(self, item_display_name, item_rules_ilogic)
                btn_get_rules.clicked.connect(lambda event: self.click_btn_get_rules(btn_get_rules.item_display_name, btn_get_rules.item_rules_ilogic))
                index = self.model().indexFromItem(item_rules_ilogic)
                self.setIndexWidget(index, btn_get_rules)

            if value['item']:
                row = self.populatet_tree(children=value['item'], parent=item_component_name, row=row)
        return row 

    def click_btn_get_rules(self, item_display_name: QtGui.QStandardItem, item_rules_ilogic: QtGui.QStandardItem) -> None:
        name_assembly = item_display_name.text()
        rules = item_rules_ilogic.rules
        self.signal_click_btn_rules.emit((name_assembly, rules))

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Z and event.modifiers() == QtCore.Qt.ControlModifier:
            self.logger_changes.undo()

        if event.key() == QtCore.Qt.Key_Z and event.modifiers() == QtCore.Qt.ShiftModifier:
            self.logger_changes.redo()

        super().keyPressEvent(event)


class FrameTreeFromDict(QtWidgets.QFrame):
    signal_rename = QtCore.pyqtSignal(tuple)
    signal_update_tree = QtCore.pyqtSignal(str)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.dict_rename = None
        self.window_rules = WindowsViewerRules(self)
        self.logger_changes = LoggerChangesQTree()
        self.init()

    def init(self):
        counter_row = RowCounter()

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(5)
        # ------------------------------------------------------------------------------------------------#
        self.label_search_to = QtWidgets.QLabel(self)
        self.label_search_to.setText('Искать в')
        self.grid.addWidget(self.label_search_to, counter_row.value, 0, 1, 1)

        self.lineedit_search_to = QtWidgets.QLineEdit(self)
        self.grid.addWidget(self.lineedit_search_to, counter_row.value, 1, 1, 1)

        self.check_box_register = QtWidgets.QCheckBox(self)
        self.check_box_register.setText('С учётом регистра')
        self.check_box_register.setCheckState(QtCore.Qt.CheckState(2))
        self.check_box_register.clicked.connect(self.click_check_box_register)
        self.grid.addWidget(self.check_box_register, counter_row.value, 2, 1, 1)

        self.label_replace_to = QtWidgets.QLabel(self)
        self.label_replace_to.setText('Заменить на')
        self.grid.addWidget(self.label_replace_to, counter_row.next(), 0, 1, 1)

        self.lineedit_replace_to = QtWidgets.QLineEdit(self)
        self.lineedit_replace_to.returnPressed.connect(self.__click_btn_replace)
        self.grid.addWidget(self.lineedit_replace_to, counter_row.value, 1, 1, 1)

        self.btn_replace = QtWidgets.QPushButton(self)
        self.btn_replace.setObjectName('btn_replace')
        self.btn_replace.setText('Заменить')
        self.btn_replace.clicked.connect(self.__click_btn_replace)
        self.btn_replace.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.grid.addWidget(self.btn_replace, counter_row.value, 2, 1, 1)

        # ------------------------------------------------------------------------------------------------#
        self.frame_check_box = QtWidgets.QFrame(self)
        self.frame_check_box.setObjectName('frame_check_box')
        self.grid.addWidget(self.frame_check_box, counter_row.next(), 1, 1, 3)

        self.hl_frame_check_box = QtWidgets.QHBoxLayout(self.frame_check_box)
        self.hl_frame_check_box.setSpacing(10)
        self.hl_frame_check_box.setContentsMargins(1, 1, 1, 1)
        
        self.check_box_suffix = QtWidgets.QCheckBox(self.frame_check_box)
        self.check_box_suffix.setText('Добавить вначале')
        self.check_box_suffix.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.check_box_suffix.clicked.connect(self.click_check_box_suffix)
        self.hl_frame_check_box.addWidget(self.check_box_suffix)

        self.check_box_preffix = QtWidgets.QCheckBox(self.frame_check_box)
        self.check_box_preffix.setText('Добавить в конец')
        self.check_box_preffix.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.check_box_preffix.clicked.connect(self.click_check_box_preffix)
        self.hl_frame_check_box.addWidget(self.check_box_preffix)

        self.check_box_change_in_rules = QtWidgets.QCheckBox(self.frame_check_box)
        self.check_box_change_in_rules.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.check_box_change_in_rules.setText('Изменять в правилах автоматически')
        self.check_box_change_in_rules.setCheckState(QtCore.Qt.CheckState(2))
        self.hl_frame_check_box.addWidget(self.check_box_change_in_rules)

        self.frame_check_box_horizont_spacer = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hl_frame_check_box.addItem(self.frame_check_box_horizont_spacer)
        
        self.line_3 = QHLineSeparate(self)
        self.grid.addWidget(self.line_3, counter_row.next(), 0, 1, 4)
        # ------------------------------------------------------------------------------------------------#
        self.frame_btn_control =  QtWidgets.QFrame(self)
        self.frame_btn_control.setObjectName("frame_btn_control")
        self.grid.addWidget(self.frame_btn_control, counter_row.next(), 0, 1, 3)

        self.hl_frame_frame_btn_control = QtWidgets.QHBoxLayout(self.frame_btn_control)
        self.hl_frame_frame_btn_control.setSpacing(1)
        self.hl_frame_frame_btn_control.setContentsMargins(1, 1, 1, 1)

        self.btn_return_back = QtWidgets.QPushButton(self.frame_btn_control)
        icon = QtGui.QIcon()
        self.btn_return_back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_return_back.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_return_back.setIconSize(QtCore.QSize(12, 12))
        self.btn_return_back.setIcon(icon)
        self.btn_return_back.setToolTip('Отменить изменения выбранного  элемента\nCtr + Z')
        self.btn_return_back.setObjectName('btn_return_back')
        self.hl_frame_frame_btn_control.addWidget(self.btn_return_back)

        self.btn_return_forward = QtWidgets.QPushButton(self.frame_btn_control)
        self.btn_return_forward.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_return_forward.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_return_forward.setIconSize(QtCore.QSize(12, 12))
        self.btn_return_forward.setIcon(icon)
        self.btn_return_forward.setToolTip('Вернуть изменения выбранного  элемента\nShift + Z')
        self.btn_return_forward.setObjectName('btn_return_forward')
        self.hl_frame_frame_btn_control.addWidget(self.btn_return_forward)
        # ------------------------------------------------------------------------------------------------#
        self.btn_update_tree = QtWidgets.QPushButton(self)
        self.btn_update_tree.setObjectName('btn_update_tree')
        self.btn_update_tree.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_update.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_update_tree.setIcon(icon)
        self.btn_update_tree.setIconSize(QtCore.QSize(17, 17))
        self.btn_update_tree.setToolTip('Обновить дерево файлов')
        self.btn_update_tree.clicked.connect(self.update_tree)
        self.hl_frame_frame_btn_control.addWidget(self.btn_update_tree)
        # ------------------------------------------------------------------------------------------------#
        self.btn_open_tmp_folder = QtWidgets.QPushButton(self)
        self.btn_open_tmp_folder.setObjectName('btn_open_tmp_folder')
        self.btn_open_tmp_folder.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_folder.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_open_tmp_folder.setIcon(icon)
        self.btn_open_tmp_folder.setIconSize(QtCore.QSize(19, 19))
        self.btn_open_tmp_folder.setToolTip('Открыть папку с временными сборками')
        self.btn_open_tmp_folder.clicked.connect(self.open_tmp_folder)
        self.hl_frame_frame_btn_control.addWidget(self.btn_open_tmp_folder)
        # ------------------------------------------------------------------------------------------------#
        self.horizont_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hl_frame_frame_btn_control.addItem(self.horizont_spacer)
        # ------------------------------------------------------------------------------------------------#
        self.model = QtGui.QStandardItemModel()
        self.tree = Tree(self, self.model)
        self.tree.signal_click_btn_rules.connect(self.open_window_rules)
        self.grid.addWidget(self.tree, counter_row.next(), 0, 1, 4)

        # ------------------------------------------------------------------------------------------------#
        self.btn_return_back.clicked.connect(self.logger_changes.undo)
        self.btn_return_forward.clicked.connect(self.logger_changes.redo)

        self.delegate = HighlightDelegate(self.tree)
        self.tree.setItemDelegate(self.delegate)
        self.lineedit_search_to.textChanged.connect(self.delegate.setSearchText)
        self.lineedit_search_to.textChanged.connect(self.tree.viewport().update)

    def fill_tree(self, dict_from_assembly: dict):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Имя компонента в сборке', 'Имя компонента в файле', 'Относительный путь', 'Правила Ilogic'])
        
        self.dict_rename = {
            'root_assembly': dict_from_assembly['root_assembly'],
            'name_assembly': dict_from_assembly['name_assembly'],
            'new_root_assembly': '',
            'new_name_assembly': '',
            'rules': {},
            'item': {}
        }

        self.tree.populatet_tree(dict_from_assembly['item'])
        self.tree.expandAll()

        width = 0
        for col in range(self.model.columnCount()):
            self.tree.header().setSectionResizeMode(col, self.tree.header().ResizeToContents)
            content_width = self.tree.sizeHintForColumn(col)
            self.tree.setColumnWidth(col, int(content_width * 1.05))
            self.tree.header().setSectionResizeMode(col, self.tree.header().Interactive)
            width += content_width
        self.tree.setColumnWidth(3, 100)
        self.tree.header().setSectionResizeMode(3, self.tree.header().Fixed)
        self.tree.header().setStretchLastSection(False)

        main_window = self.parent().parent()
        main_window_geom = main_window.geometry()
        main_window.setGeometry(main_window_geom.x(), main_window_geom.y(), int(width * 1.1), 600)

    def __click_btn_replace(self) -> None:
        self.logger_changes.start_transaction()
        if self.btn_replace.text() == 'Заменить':
            if self.lineedit_search_to.text():
                self.__rename_one_item(item=self.model.invisibleRootItem())
        else:
            if self.lineedit_replace_to.text():
                self.__item_add_text_preffix_or_suffix()
        self.logger_changes.end_transaction()

    def __rename_one_item(self, item) -> None:
        for i in range(item.rowCount()):
            item_component_name = item.child(i, 0)
            text_component = item_component_name.text()

            item_display_name = item.child(i, 1)
            text_display_name = item_display_name.text()

            item_short_filename = item.child(i, 2)
            text_short_filename = item_short_filename.text()
            
            item_rules = item.child(i, 3)
            dict_rules: dict = item_rules.rules

            text_search_to = self.lineedit_search_to.text()
            text_replace_to = self.lineedit_replace_to.text()

            if not self.check_box_register.checkState():
                text_component = text_component.lower()
                text_display_name = text_display_name.lower()
                text_short_filename = text_short_filename.lower()
                text_search_to = text_search_to.lower()
                text_replace_to = text_replace_to.lower()

            item_component_name.setText(text_component.replace(text_search_to, text_replace_to))
            item_display_name.setText(text_display_name.replace(text_search_to, text_replace_to))
            item_short_filename.setText(text_short_filename.replace(text_search_to, text_replace_to))

            if self.check_box_change_in_rules.checkState():
                new_dict_rules = {}
                for name, text_rules in dict_rules.items():
                    new_dict_rules[name] = text_rules.replace(text_search_to, text_replace_to)
                item_rules.rules = new_dict_rules
                self.logger_changes.add_change(item_rules, dict_rules, new_dict_rules, TypeItemQTree.rules)

            self.__rename_one_item(item=item.child(i, 0)) 

    def __item_add_text_preffix_or_suffix(self, item=None, text=None) -> None:
        if item is None:
            item = self.model.invisibleRootItem()
            text = self.lineedit_replace_to.text()
        
        for i in range(item.rowCount()):
            item_component_name = item.child(i, 0)
            item_display_name = item.child(i, 1)
            item_short_filename = item.child(i, 2)

            text_short_filename = item_short_filename.text()
            list_short_filename = text_short_filename.split('\\')
            
            if not self.check_box_preffix.checkState():
                new_text_component_name = text + item_component_name.text()
                new_text_display_name = text + item_display_name.text()
                list_short_filename[-1] = text + list_short_filename[-1]
                new_text_short_filename = '\\'.join(list_short_filename)
            elif not self.check_box_suffix.checkState():
                new_text_component_name = item_component_name.text() + text
                new_text_display_name = item_display_name.text() + text
                list_short_filename[-1] = list_short_filename[-1] + text
                new_text_short_filename = '\\'.join(list_short_filename)
            
            item_component_name.setText(new_text_component_name)
            item_display_name.setText(new_text_display_name)
            item_short_filename.setText(new_text_short_filename)

            self.__item_add_text_preffix_or_suffix(item=item.child(i, 0), text=text) 

    def rename_item_from_dict(self, data: dict) -> None:
        """
        Переименование из словаря компонентов сборки, а также в правилах. Для подготовленных сборок из окна PreparedAssemblyWindow
        """
        search_to = data['search_to']
        replace_to = data['replace_to']

        self.lineedit_search_to.setText(search_to)
        self.lineedit_replace_to.setText(replace_to)
        
        self.__rename_one_item(item=self.model.invisibleRootItem())
    
    def __change_check_box(self, item: QtGui.QStandardItem, item_rec=None) -> None:
        if item_rec is None:
            item_rec = self.model.invisibleRootItem()
            
        color = QtGui.QColor('#93d1ff') if item.checkState() else QtGui.QColor(255, 255, 255)
        for i in range(item_rec.rowCount()):
            item_1 = item_rec.child(i, 0)
            item_2 = item_rec.child(i, 1)
            item_3 = item_rec.child(i, 2)          
            
            if item == item_1:
                item_1.setData(color, QtCore.Qt.BackgroundRole)
                item_2.setData(color, QtCore.Qt.BackgroundRole)
                item_3.setData(color, QtCore.Qt.BackgroundRole)

            self.__change_check_box(item=item, item_rec=item_1)

    def click_check_box_register(self, value: bool) -> None:
        self.check_box_register.setCheckState
        self.delegate.setModeRegister(value)
        text = self.lineedit_search_to.text()
        self.lineedit_search_to.setText(text[1:])
        self.lineedit_search_to.setText(text)

    def click_check_box_preffix(self, value: bool) -> None:
        self.lineedit_search_to.setEnabled(not value)
        self.check_box_register.setEnabled(not value)
        self.check_box_suffix.setEnabled(not value)
        self.btn_replace.setText('Добавить' if value else 'Заменить')

    def click_check_box_suffix(self, value: bool) -> None:
        self.lineedit_search_to.setEnabled(not value)
        self.check_box_register.setEnabled(not value)
        self.check_box_preffix.setEnabled(not value)
        self.btn_replace.setText('Добавить' if value else 'Заменить')

    def get_dict(self) -> dict:
        if self.dict_rename:
            self.dict_rename['new_root_assembly'] = ''
            self.dict_rename['new_name_assembly'] = ''
            self.dict_rename['rules'] = {}
            self.dict_rename['item'].clear()

            self.__get_dict(self.model.invisibleRootItem())
            return self.dict_rename

    def __get_dict(self, item):
        for i in range(item.rowCount()):
            item_component_name = item.child(i, 0)
            item_display_name = item.child(i, 1)
            item_short_filename = item.child(i, 2)
            item_rules = item.child(i, 3)

            if not self.dict_rename['new_name_assembly']:
                self.dict_rename['new_name_assembly'] = item_component_name.text() + '.iam'
                self.dict_rename['rules'] = item_rules.rules
            else:
                # item_short_filename.name[1:] --> '\dir1\dir2\file1.ipt' -->  убирает слэш вначале
                full_file_path = os.path.join(self.dict_rename['root_assembly'], item_short_filename.name[1:] + item_short_filename.type_file)

                self.dict_rename['item'][full_file_path] = {
                    'component_name': (item_component_name.name, item_component_name.text()),
                    'display_name': (item_display_name.name, item_display_name.text()),
                    'short_filename': (item_short_filename.name + item_short_filename.type_file, strip_path(item_short_filename.text()) + item_short_filename.type_file),
                    'rules': item_rules.rules
                }
            self.__get_dict(item_component_name)

    def open_window_rules(self, value: tuple) -> None:
        name_assembly, rules = value
        self.window_rules.clear()
        self.window_rules.set_name_assembly(name_assembly)
        self.window_rules.fill_data(rules)
        self.window_rules.show()
        
    def update_tree(self) -> None:
        if self.dict_rename:
            self.signal_update_tree.emit(os.path.join(self.dict_rename['root_assembly'], self.dict_rename['name_assembly']))


    def switch_enabled_widgets(self, value: bool) -> None:
        for widgets in self.children():
            if isinstance(widgets, QtWidgets.QPushButton) or isinstance(widgets, QtWidgets.QLineEdit) or isinstance(widgets, QtWidgets.QFrame):
                widgets.setEnabled(value)
    
    def open_tmp_folder(self) -> None:
        if self.dict_rename:
            root_assmbly = self.dict_rename['root_assembly']
            if os.path.exists(root_assmbly):
                os.system(f"explorer {root_assmbly}")
                return
        os.system(f"explorer {PATH_TMP}")


class ElidedLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_text = ''

    def sizeHint(self):
        return QtCore.QSize(100, 50)
        
    def minimumSizeHint(self):
        return QtCore.QSize(0, 0)
    

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.tmp_assembly_path: Optional[str] = None

        self.prepared_assembly_window = PreparedAssemblyWindow(self)
        self.prepared_assembly_window.signal_get_data.connect(self.get_data_from_prepared_assembly)
        self.thread_inventor = IThread()
        self.interactive_helper = None

        self.initWindow()
        self.initWidgets()
        self.initThread()
        # self.initHelper()
                
        if DEBUG:
            self.label_load_ring.setText(r'\\pdm\pkodocs\Inventor Project\ООО ЛебедяньМолоко\1642_24\5.3.X5. Порошковый миксер Inoxpa ME-4105_ME-4110\05 проект INVENTOR\ALS.1642.5.3.06.01-Рама\ALS.1642.5.3.06.01.00.000 СБ\Frame')

            with open(os.path.join(Path(PROJECT_ROOT).parent, 'DEBUG\data_assembly.txt'), 'r', encoding='utf-8') as file_data_assembly: 
                self.fill_trees(eval(file_data_assembly.read()))

    def initWindow(self):
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ICO_FOLDER, 'CopyAssembly.png')))
        
        with open(os.path.join(PROJECT_ROOT, r'resources\\style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        self.resize(600, 500)
        self.setWindowTitle('CopyAssembly')

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.grid = QtWidgets.QGridLayout(self.centralwidget)
        self.grid.setContentsMargins(5, 0, 5, 0)
        self.grid.setObjectName("gridLayoutCentral")

        self.setCentralWidget(self.centralwidget)

        menuBar = self.menuBar()
        
        prepared_action = QtWidgets.QAction("&Готовые сборки", self)
        prepared_action.triggered.connect(self.show_window_prepared_assembly)
        menuBar.addAction(prepared_action)

        help_menu = menuBar.addMenu('&Помощь')

        help_action_doc = QtWidgets.QAction("&Справка", self)
        help_action_doc.triggered.connect(self.open_instruction)
        help_menu.addAction(help_action_doc)

        help_action_interactive = QtWidgets.QAction("&Интерактивная справка", self)
        help_action_interactive.setShortcut('F2')
        help_action_interactive.triggered.connect(self.start_help_interective)
        help_menu.addAction(help_action_interactive)

        self.shortcut_search_focus = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+F'), self)
        self.shortcut_search_focus.activated.connect(self.set_focus_search_line_edit)

    def initWidgets(self):
        # ------------------------------------------------------------------------------------------------#
        self.label_choose_assembly = QtWidgets.QLabel(self)
        self.label_choose_assembly.setText('Выберите сборку')
        self.grid.addWidget(self.label_choose_assembly, 0, 0, 1, 1)

        self.lineedit_choose_assembly = QtWidgets.QLineEdit(self)
        self.lineedit_choose_assembly.setObjectName('lineedit_choose_assembly')
        self.lineedit_choose_assembly.textChanged.connect(lambda event: self.lineedit_choose_assembly.setStyleSheet("#lineedit_choose_assembly {border: 1px solid gray;}"))
        self.grid.addWidget(self.lineedit_choose_assembly, 0, 1, 1, 1)
        self.lineedit_choose_assembly.setEnabled(False)

        self.btn_choose_path_assembly = QtWidgets.QPushButton(self)
        self.btn_choose_path_assembly.setObjectName('btn_choose_path_assembly')
        self.btn_choose_path_assembly.setMinimumSize(50, 20)
        self.btn_choose_path_assembly.setText('Выбрать')
        self.btn_choose_path_assembly.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_choose_path_assembly.clicked.connect(self.click_choose_assembly)
        self.grid.addWidget(self.btn_choose_path_assembly, 0, 2, 1, 1)
        # ------------------------------------------------------------------------------------------------#
        self.line_1 = QHLineSeparate(self)
        self.grid.addWidget(self.line_1, 2, 0, 1, 3)
        # ------------------------------------------------------------------------------------------------#
        self.frame_tree_assembly = FrameTreeFromDict(self)
        self.frame_tree_assembly.setObjectName('frame_tree_assembly')
        self.frame_tree_assembly.signal_update_tree.connect(self.update_tree)
        self.grid.addWidget(self.frame_tree_assembly, 3, 0, 1, 3)
        # ------------------------------------------------------------------------------------------------#
        self.btn_continue = QtWidgets.QPushButton(self)
        self.btn_continue.setObjectName('btn_ok')
        self.btn_continue.setText('Продолжить')
        self.btn_continue.setMinimumHeight(20)
        self.btn_continue.clicked.connect(self.click_continue)
        self.btn_continue.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.grid.addWidget(self.btn_continue, 4, 0, 1, 3)
        # ------------------------------------------------------------------------------------------------#
        self.frame_load = QtWidgets.QFrame(self)
        self.frame_load.setMaximumSize(160000, 25)
        self.frame_load.setObjectName('frame_load')
        self.grid.addWidget(self.frame_load, 5, 0, 1, 3)

        self.layout_frame_load = QtWidgets.QHBoxLayout(self.frame_load)
        self.layout_frame_load.setContentsMargins(0, 0, 0, 0)

        self.pb_ring = LoadRing(self.frame_load)
        self.layout_frame_load.addWidget(self.pb_ring)

        self.label_load_ring = ElidedLabel()
        self.label_load_ring.setObjectName('label_load_ring')
        self.label_load_ring.setText('Готово')
        self.layout_frame_load.addWidget(self.label_load_ring)

    def initThread(self):
        self.thread_inventor.signal_text_pb.connect(self.change_text_pb)
        self.thread_inventor.signal_pb.connect(self.set_state_pb)
        self.thread_inventor.signal_dict_assembly.connect(self.fill_trees)
        self.thread_inventor.signal_error.connect(self.thread_inventor_error)
        self.thread_inventor.signal_complite_thread.connect(self.thread_inventor_complite)
        self.thread_inventor.signal_complite_copy_assembly.connect(self.move_complite_assembly)
        self.thread_inventor.signal_is_prepared.connect(self.__full_rename_assembly)

    def initHelper(self) -> None:
        ...
        # self.interactive_helper.add_step([self.frame_load], 'В данной части приложения отображается процесс выполнения', False)

        # self.interactive_helper.add_step([
        #     get_rect_tree_header(0)
        # ], 'Данный столбец содержит имя компонента внутри сборки')

        # self.interactive_helper.add_step([
        #     get_rect_tree_header(1)
        # ], 'Данный столбец содержит имя компонента внутри файла компонента')

        # self.interactive_helper.add_step([
        #     get_rect_tree_header(2)
        # ], 'Данный столбец содержит путь относительно копируемой сборки')

        # self.interactive_helper.add_step([
        #     get_rect_tree_header(2)
        # ], 'Можно создать новую папку')

    
        # self.interactive_helper.add_step([
        #     get_rect_tree_header(2)
        # ], '"\\" вначале можно удалить, это не повлияет на процесс')

        # self.interactive_helper.add_step([
        #     get_rect_tree_header(3)
        # ], 'Данный столбец содержит правила компонента')

        # self.interactive_helper.add_step([
        #     self.frame_tree_assembly.tree
        # ], 'Вы можете переименовать любое имя или ')

        # self.interactive_helper.add_step([self.frame_tree_assembly.label_replace_to, 
        #                       self.frame_tree_assembly.lineedit_replace_to, 
        #                       self.frame_tree_assembly.label_search_to, 
        #                       self.frame_tree_assembly.lineedit_search_to, 
        #                       self.frame_tree_assembly.btn_replace, 
        #                       self.frame_tree_assembly.check_box_register], 
        #                       'Шаг 2')       

    def start_help_interective(self) -> None:
        if self.interactive_helper is None:
            self.interactive_helper = HelperInteractive(self)
            self.interactive_helper.load_config(os.path.join(PROJECT_ROOT, 'resources\\config_helper_interactive.json'))
        # self.initHelper()
        self.interactive_helper.show()

    def thread_inventor_error(self, error_code: ErrorCode) -> None:
        if error_code == ErrorCode.SUCCESS:
            return
        
        self.lineedit_choose_assembly.setText('')
        self.change_text_pb('Готово')
        
        if error_code == ErrorCode.OPEN_INVENTOR_APPLICATION or error_code == ErrorCode.OPEN_INVENTOR_PROJECT:
            self.close_application()

        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(f'{error_code.message}\n{error_code.description}')
        msg.setWindowTitle('Внимание')
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

        self.switch_enabled_widgets(True)
        self.frame_tree_assembly.switch_enabled_widgets(True)

    def open_instruction(self, event):
        os.startfile(os.path.join(PROJECT_ROOT, URL_INSTRUCTION_OFFLINE))

    def show_window_prepared_assembly(self):
        self.prepared_assembly_window.show()
    
    def get_data_from_prepared_assembly(self, data: dict) -> None:
        self.prepared_assembly_window.close()     
        self.__load_assembly(filepath=data['path_assembly'], is_prepared=True, is_CoInitialize=True)

    def click_choose_assembly(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setWindowTitle('Выберете файл')
        dlg.setNameFilter('Inventor (*.iam)')
        dlg.selectNameFilter('Inventor (*.iam)')
        dlg.setDirectory(DEFAULT_PATH_DIALOG_WINDOW)
        dlg.exec_()
        filepath = dlg.selectedFiles()

        if filepath:
            self.__load_assembly(filepath[0], is_CoInitialize=False)

        if self.interactive_helper and self.interactive_helper.isVisible():
            self.interactive_helper.next_step()

    def update_tree(self, filepath) -> None:
        if self.thread_inventor.pid:
            self.__load_assembly(filepath=filepath, is_update=True)

    def __load_assembly(self, filepath, is_update=False, is_prepared=False, is_CoInitialize=False) -> None:
        self.switch_enabled_widgets(False)
        self.frame_tree_assembly.switch_enabled_widgets(False)
        
        QtCore.QMetaObject.invokeMethod(
            self.thread_inventor, 
            "init_open_assembly", 
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, filepath),
            QtCore.Q_ARG(bool, is_update),
            QtCore.Q_ARG(bool, is_prepared),
            QtCore.Q_ARG(bool, is_CoInitialize),
            )
        QtCore.QMetaObject.invokeMethod(self.thread_inventor, "run", QtCore.Qt.QueuedConnection)       

    def __full_rename_assembly(self, value: bool) -> None:
        """
        Переименование для готовых сборок. Данные берутся не от пользотеля, а из окна PreparedAssemblyWindow
        """
        if value:
            data = self.prepared_assembly_window.current_data_assembly
            self.lineedit_choose_assembly.setText(data['new_name_assembly'] + '.iam')
            self.frame_tree_assembly.rename_item_from_dict(data)
            self.switch_enabled_widgets(True)
            self.frame_tree_assembly.switch_enabled_widgets(True)
            self.click_continue()
        
    def fill_trees(self, data: dict) -> None:
        self.switch_enabled_widgets(True)
        self.frame_tree_assembly.switch_enabled_widgets(True)
        if data is not None: 
            self.lineedit_choose_assembly.setText(tuple(data['item'].keys())[0])
            self.frame_tree_assembly.fill_tree(data)
            
    def change_text_pb(self, string: str):
        self.label_load_ring.setText(string)

    def set_state_pb(self, value: bool) -> None:
        if value:
            self.pb_ring.start_load()
        else:
            self.pb_ring.stop_load()

    def click_continue(self) -> None:
        dct_assembly = self.frame_tree_assembly.get_dict()

        if not dct_assembly:
            return

        self.btn_continue.setText('Процесс копирования...')
        self.switch_enabled_widgets(False)
        self.frame_tree_assembly.switch_enabled_widgets(False)

        dct_assembly['new_root_assembly'] = create_folder_rename_assembly(assembly_name=dct_assembly['new_name_assembly'])
            
        QtCore.QMetaObject.invokeMethod(
            self.thread_inventor, 
            "init_copy_assembly", 
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(dict, dct_assembly),
        )
        QtCore.QMetaObject.invokeMethod(self.thread_inventor, "run", QtCore.Qt.QueuedConnection)
         
    def thread_inventor_complite(self):
        self.label_load_ring.setText('Готово')
        self.btn_continue.setText('Продолжить')
        self.switch_enabled_widgets(True)
        self.frame_tree_assembly.switch_enabled_widgets(True)
        
        if self.interactive_helper and self.interactive_helper.isVisible():
            self.interactive_helper.next_step()

    def move_complite_assembly(self, path_from_: str) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filepath = dlg.getExistingDirectory(self, 'Выберете папку')
        if filepath:
            filepath = filepath.replace('/', '\\')
            dirpath = os.path.basename(path_from_)
            path_to = os.path.join(filepath, dirpath)
            try:
                shutil.copytree(path_from_, path_to)
                shutil.rmtree(path_from_)
                os.system(f"explorer {path_to}")
            except Exception:
                os.system(f"explorer {path_from_}")
        else:
            os.system(f"explorer {path_from_}")

    def switch_enabled_widgets(self, value: bool) -> None:
        for widgets in self.children():
            if widgets.objectName() == 'centralwidget':
                for w in widgets.children():
                    if isinstance(w, QtWidgets.QPushButton) or isinstance(w, QtWidgets.QLineEdit) or isinstance(w, QtWidgets.QCheckBox):
                        if w.objectName() != 'lineedit_choose_assembly':
                            w.setEnabled(value)

    def set_focus_search_line_edit(self) -> None:
        self.frame_tree_assembly.lineedit_search_to.setFocus()

    def del_tmp_copy_assembly(self) -> None:
        if os.path.exists(PATH_TMP):
            for folder in os.listdir(PATH_TMP):
                if 'copy at' in folder:
                    path = os.path.join(PATH_TMP, folder)
                    if os.path.exists(path):
                        try:
                            shutil.rmtree(path)
                        except Exception as error:
                            for root, folders, files in os.walk(path):
                                for file in files:
                                    try:
                                        os.remove(os.path.join(root, file))
                                    except Exception:
                                        loging_try()
                                                            
                                for folder in folders:
                                    try:
                                        shutil.rmtree(os.path.join(root, folder))
                                    except Exception:
                                        loging_try()
                            loging_try()

    def inventor_application_close(self) -> None:
        self.close_application()

    def close_application(self) -> None:
        if self.thread_inventor.pid:
            kill_process_for_pid(self.thread_inventor.pid)
            self.thread_inventor.pid = None
        self.del_tmp_copy_assembly()
        self.thread_inventor.deleteLater()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.change_text_pb('Закрытие...')
        self.pb_ring.start_load()
        loop = QtCore.QEventLoop()
        self.thread_inventor.signal_close.connect(loop.quit)
        QtCore.QMetaObject.invokeMethod(self.thread_inventor, "close", QtCore.Qt.QueuedConnection)
        loop.exec_()
        self.close_application()
        super().closeEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if key == QtCore.Qt.Key.Key_Escape and self.interactive_helper and self.interactive_helper.isVisible():
            self.interactive_helper.close()
        return super().keyPressEvent(event)

    def resizeEvent(self, event):
        if self.interactive_helper and self.interactive_helper.isVisible():
            self.interactive_helper.resize(self.size())
        return super().resizeEvent(event)


def my_excepthook(type, value, tback):
    global window, app

    loging_sys(type, value, tback)
    window.close_application()
    
    msg = QtWidgets.QMessageBox(window)
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText('Необрабатываемая ошибка')
    msg.setWindowTitle('CRITICAL ERROR')
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec()
    
    app.exit(1)


if __name__ == '__main__':
    sys.excepthook = my_excepthook
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())
