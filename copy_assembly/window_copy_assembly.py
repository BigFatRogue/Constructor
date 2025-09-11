import shutil
import sys
import ctypes
import os
from copy import deepcopy
from typing import Optional, Any
from PyQt5 import QtCore, QtGui, QtWidgets
from Widgets import MessegeBoxQuestion
from window_prepared_assembly import PreparedAssemblyWindow

from sitting import *
from error_code import ErrorCode
from my_logging import loging_sys, loging_try
from mode_code import Mode
from preprocess_inventor import get_app_inventor, kill_process_for_pid
from copy_and_rename_assembly import move_file_inventor_project, copy_file_assembly, get_tree_assembly, get_rules_assembly, copy_and_rename_file_assembly, replace_reference_file, rename_display_name_file, rename_component_name_in_assembly, create_folder_rename_assembly, set_rulse
from my_function import strip_path, RowCounter


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
                tmp_assembly_path = copy_file_assembly(full_filename=self.__full_filename_assembly)
            else:
                tmp_assembly_path = self.__full_filename_assembly

            self.signal_text_pb.emit(f'Загрузка и чтение сборки...')
            dict_assembly, document = get_tree_assembly(application=self.__app, options_open_document=self.__options_open_document, full_filename_assembly=tmp_assembly_path)
            
            self.signal_text_pb.emit('Чтение правил...')
            document.Close()

            with open(r'DEBUG\data_assembly.txt', 'w', encoding='utf-8') as file_data_assembly: 
                file_data_assembly.write(str(dict_assembly))
        
            self.signal_dict_assembly.emit(dict_assembly)
            self.signal_is_prepared.emit(self.__is_prepared)
        else:
            self.signal_error.emit(ErrorCode.OPEN_INVENTOR_APPLICATION)
        self.__clear_variable_open()
        self.signal_complite_thread.emit()

    @QtCore.pyqtSlot(dict)
    def init_copy_assembly(self, dict_assembly: dict) -> None:
        self.__mode = Mode.COPY_ASSEMBLY
        self.__dict_assembly = dict_assembly

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
            rename_display_name_file(application=self.__app, options_open_document=self.__options_open_document, dict_from_application=self.__dict_assembly)
            rename_component_name_in_assembly(document=doc, dict_from_application=self.__dict_assembly)

            doc.Save()
            doc.Close()

            os.system(f"explorer {self.__dict_assembly['new_root_assembly']}")
        else:
            self.signal_error.emit(ErrorCode.CONNECT_INVENTOR_APPLICATION)
        self.__claer_variable_copy()
        self.signal_complite_thread.emit()
    
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


class QHLine(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


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


class LineEdit(QtWidgets.QLineEdit):
    signal_text = QtCore.pyqtSignal(str)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)
        self.signal_text.emit(self.text())


class Tree(QtWidgets.QTreeView):
    def __init__(self, parent, model: QtGui.QStandardItemModel, *args, **kwargs):
        super().__init__(parent)

        self.setObjectName('Tree')

        self.model = model
        self.model.itemChanged.connect(self.on_item_changed)
        self.shift_start_index = None
        self.flag_change_range = False
        self.init()

    def init(self):
        self.setModel(self.model)

    def on_item_changed(self, item, rec=False) -> None:      
        if item.text() not in item.names:
            item.names.append(item.text())

    def populatet_tree(self, children: dict, parent=None, count=0) -> int:
        if parent is None:
            parent = self.model.invisibleRootItem()

        for filepath, value in children.items():
            img = value['image']
            icon = QtGui.QIcon()
            icon_path = os.path.join(ICO_FOLDER, img)
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
         
            component_name = value['component_name']
            item_component_name = QtGui.QStandardItem(component_name)
            item_component_name.setIcon(icon)

            setattr(item_component_name, 'name', component_name)
            setattr(item_component_name, 'count', count)
            setattr(item_component_name, 'names', [component_name])

            display_name = value['display_name']
            item_display_name = QtGui.QStandardItem(display_name)
            setattr(item_display_name, 'name', display_name)
            setattr(item_display_name, 'names', [display_name])
            
            # ALS.000.itp[-4] -> ALS.000 
            short_filename = value['short_filename'][:-4]
            item_short_filename = QtGui.QStandardItem(short_filename)
            setattr(item_short_filename, 'name', short_filename)
            setattr(item_short_filename, 'names', [short_filename])
            setattr(item_short_filename, 'type_file', value['type_file'])

            item_rules_ilogic = QtGui.QStandardItem()
            item_rules_ilogic.setEditable(False)
            setattr(item_rules_ilogic, 'rules', value['rules'])
            
            list_item = [item_component_name, item_display_name, item_short_filename, item_rules_ilogic]
            for item in list_item:
                item.setData(QtGui.QColor(255, 255, 255), QtCore.Qt.BackgroundRole)

            parent.appendRow(list_item)
            count += 1
            
            if value['rules']:
                btn = QtWidgets.QPushButton("Правила")
                btn.clicked.connect(lambda event: print(value['rules']))
                index = self.model.indexFromItem(item_rules_ilogic)
                self.setIndexWidget(index, btn)

            if value['item']:
                count = self.populatet_tree(children=value['item'], parent=item_component_name, count=count)
        return count 

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Z and event.modifiers() == QtCore.Qt.ControlModifier:
            self.return_text()

        if event.key() == QtCore.Qt.Key_Z and event.modifiers() == QtCore.Qt.ShiftModifier:
            self.forward_text()

        super().keyPressEvent(event)

    def return_text(self):
        index = self.currentIndex()
        if index.isValid():
            item = self.model.itemFromIndex(index)
            indx = item.names.index(item.text())

            if indx != 0:
                item.setText(item.names[indx - 1])

    def return_all_text(self, event: bool, item=None):
        if item is None:
            item = self.model.invisibleRootItem()

        for i in range(item.rowCount()):
            for j in range(3):
                child = item.child(i, j)
                indx = child.names.index(child.text())

                if indx != 0:
                    child.setText(child.names[indx - 1])

                self.return_all_text(event=True, item=child)

    def forward_text(self):
        index = self.currentIndex()
        if index.isValid():
            item = self.model.itemFromIndex(index)
            indx = item.names.index(item.text())

            if indx != len(item.names) - 1:
                item.setText(item.names[indx + 1])

    def forward_all_text(self, event: bool, item=None):
        if item is None:
            item = self.model.invisibleRootItem()

        for i in range(item.rowCount()):
            for j in range(3):
                child = item.child(i, j)

                indx = child.names.index(child.text())

                if indx != len(child.names) - 1:
                    child.setText(child.names[indx + 1])

                self.forward_all_text(event=True, item=child)


class QTextBoxWithZoom(QtWidgets.QTextEdit):
    def wheelEvent(self, event: QtGui.QWheelEvent):
        delta = event.angleDelta().y()
        if (event.modifiers() & QtCore.Qt.ControlModifier):
            if delta < 0:
                self.zoomOut(1)
            elif delta > 0:
                self.zoomIn(5)
        else:
            super().wheelEvent(event)


class ViewerRules(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.data = None
        self.__copy_data = None
        self.prevIndex = None 

        h_layout = QtWidgets.QHBoxLayout(self)
        h_layout.setContentsMargins(2, 2, 2, 2)

        self.list_box = QtWidgets.QListWidget()
        self.list_box.clicked.connect(self.select_rule)
        h_layout.addWidget(self.list_box)

        self.text_box = QTextBoxWithZoom(self)
        h_layout.addWidget(self.text_box)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.list_box)
        splitter.addWidget(self.text_box)
        splitter.setStretchFactor(1, 1)
        h_layout.addWidget(splitter)

    def fill_data(self, data) -> None:
        if self.data:
            self.data = None
        if data is not None:
            self.data = data

            for title in data.keys():
                self.list_box.addItem(title)

    def check_changes(self, rule_name: str) -> bool:
        """True - есть изменения, False - нет изменений"""
        clear_text = lambda x: [i.strip() for i in x.split()]

        text_tb = clear_text(self.text_box.toPlainText())
        text_dct = clear_text(self.data[rule_name])

        return text_tb != text_dct

    def select_rule(self, event: bool) -> None:
        name_rule = self.list_box.currentIndex().data()
        
        if self.prevIndex != name_rule:
            if self.prevIndex:
                if self.check_changes(self.prevIndex):
                    msg = MessegeBoxQuestion(self)
                    if msg.exec() == QtWidgets.QDialog.Accepted:
                        self.data[self.prevIndex] = self.text_box.toPlainText()

            self.prevIndex = name_rule
            text = self.data[name_rule]
            self.text_box.clear()
            self.text_box.setText(text)

    def rename_text_box(self, search: str, to: str) -> None:
        text = self.text_box.toPlainText()
        text = text.replace(search, to)
        self.text_box.setText(text)

    def all_rename_text_box(self, search: str, to: str) -> None:
        self.rename_text_box(search, to)
        self.__copy_data = deepcopy(self.data)
        for key, value in self.data.items():
            self.data[key] = value.replace(search, to)

    def clear_rules_data(self) -> None:
        self.data = None
        self.text_box.clear()
        self.list_box.clear()
    
    def get_rules(self) -> dict:
        if self.data:
            return self.data        

    def hide(self) -> None:
        rule_name = self.list_box.currentIndex().data()
        if rule_name:
            if self.check_changes(rule_name):
                msg = MessegeBoxQuestion(self)
                if msg.exec() == QtWidgets.QDialog.Accepted:
                    self.data[rule_name] = self.text_box.toPlainText()
                self.text_box.clear()
                self.text_box.setText(self.data[rule_name])
        
        if self.__copy_data is not None:
            msg = MessegeBoxQuestion(self)
            if msg.exec() == QtWidgets.QDialog.Rejected:
                self.data = deepcopy(self.__copy_data)
            self.__copy_data = None
            if rule_name:
                self.text_box.clear()
                self.text_box.setText(self.data[rule_name])

        return super().hide()
                

class FrameTreeFromDict(QtWidgets.QFrame):
    signal_rename = QtCore.pyqtSignal(tuple)
    signal_update_tree = QtCore.pyqtSignal(str)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.dct_rename = None
        # True - Активно дерево, False - активно textbox с правилами 
        self.flag_switch_tree = True
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

        self.textedit_search_to = LineEdit(self)
        self.grid.addWidget(self.textedit_search_to, counter_row.value, 1, 1, 1)

        self.check_box_register = QtWidgets.QCheckBox(self)
        self.check_box_register.setText('С учётом регистра')
        self.check_box_register.setCheckState(QtCore.Qt.CheckState(2))
        self.check_box_register.clicked.connect(self.click_check_box_register)
        self.grid.addWidget(self.check_box_register, counter_row.value, 2, 1, 1)

        self.label_replace_to = QtWidgets.QLabel(self)
        self.label_replace_to.setText('Заменить на')
        self.grid.addWidget(self.label_replace_to, counter_row.next(), 0, 1, 1)

        self.textedit_replace_to = LineEdit(self)
        self.textedit_replace_to.returnPressed.connect(self.__click_btn_replace)
        self.grid.addWidget(self.textedit_replace_to, counter_row.value, 1, 1, 1)

        self.btn_replace = QtWidgets.QPushButton(self)
        self.btn_replace.setText('Заменить')
        self.btn_replace.clicked.connect(self.__click_btn_replace)
        self.grid.addWidget(self.btn_replace, counter_row.value, 2, 1, 1)

        # ------------------------------------------------------------------------------------------------#
        self.frame_check_box = QtWidgets.QFrame(self)
        self.grid.addWidget(self.frame_check_box, counter_row.next(), 1, 1, 3)

        self.hl_frame_check_box = QtWidgets.QHBoxLayout(self.frame_check_box)
        self.hl_frame_check_box.setSpacing(1)
        self.hl_frame_check_box.setContentsMargins(1, 1, 1, 1)
        
        self.check_box_suffix = QtWidgets.QCheckBox(self.frame_check_box)
        self.check_box_suffix.setText('Добавить вначале')
        self.check_box_suffix.clicked.connect(self.click_check_box_suffix)
        self.hl_frame_check_box.addWidget(self.check_box_suffix)

        self.check_box_preffix = QtWidgets.QCheckBox(self.frame_check_box)
        self.check_box_preffix.setText('Добавить в конец')
        self.check_box_preffix.clicked.connect(self.click_check_box_preffix)
        self.hl_frame_check_box.addWidget(self.check_box_preffix)

        self.check_box_change_in_rules = QtWidgets.QCheckBox(self.frame_check_box)
        self.check_box_change_in_rules.setText('Изменять в правилах автоматически')
        self.check_box_change_in_rules.setCheckState(QtCore.Qt.CheckState(2))
        # self.check_box_change_in_rules.clicked.connect(self.click_check_box_preffix)
        self.hl_frame_check_box.addWidget(self.check_box_change_in_rules)

        self.frame_check_box_horizont_spacer = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hl_frame_check_box.addItem(self.frame_check_box_horizont_spacer)
        
        self.btn_replace_all = QtWidgets.QPushButton(self)
        self.btn_replace_all.setText('Заменить всё')
        self.grid.addWidget(self.btn_replace_all, counter_row.value, 2, 1, 1)
        self.btn_replace_all.hide()
        # ------------------------------------------------------------------------------------------------#
        self.frame_btn_control =  QtWidgets.QFrame(self)
        self.frame_btn_control.setObjectName("frame_btn_control")
        self.grid.addWidget(self.frame_btn_control, counter_row.next(), 0, 1, 3)

        self.hl_frame_frame_btn_control = QtWidgets.QHBoxLayout(self.frame_btn_control)
        self.hl_frame_frame_btn_control.setSpacing(1)
        self.hl_frame_frame_btn_control.setContentsMargins(1, 1, 1, 1)
        # ------------------------------------------------------------------------------------------------#
        self.frame_forward_return = QtWidgets.QFrame(self)
        self.hl_frame_frame_btn_control.addWidget(self.frame_forward_return)

        self.hl_frame_forward_return = QtWidgets.QHBoxLayout(self.frame_forward_return)
        self.hl_frame_forward_return.setSpacing(1)
        self.hl_frame_forward_return.setContentsMargins(1, 1, 1, 1)

        self.btn_all_return_back = QtWidgets.QPushButton(self.frame_forward_return)
        self.btn_all_return_back.setMinimumSize(20, 20)
        self.btn_all_return_back.setMaximumSize(20, 20)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_return_all_back.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_all_return_back.setIcon(icon)
        self.btn_all_return_back.setToolTip('Отменить все изменения')
        self.btn_all_return_back.setObjectName('btn_all_return_back')
        self.hl_frame_forward_return.addWidget(self.btn_all_return_back)

        self.btn_return_back = QtWidgets.QPushButton(self.frame_forward_return)
        self.btn_return_back.setMinimumSize(20, 20)
        self.btn_return_back.setMaximumSize(20, 20)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_return_back.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_return_back.setIconSize(QtCore.QSize(12, 12))
        self.btn_return_back.setIcon(icon)
        self.btn_return_back.setToolTip('Отменить изменения выбранного  элемента\nCtr + Z')
        self.btn_return_back.setObjectName('btn_return_back')
        self.hl_frame_forward_return.addWidget(self.btn_return_back)

        self.btn_return_forward = QtWidgets.QPushButton(self.frame_forward_return)
        self.btn_return_forward.setMinimumSize(20, 20)
        self.btn_return_forward.setMaximumSize(20, 20)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_return_forward.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_return_forward.setIconSize(QtCore.QSize(12, 12))
        self.btn_return_forward.setIcon(icon)
        self.btn_return_forward.setToolTip('Вернуть изменения выбранного  элемента\nShift + Z')
        self.btn_return_forward.setObjectName('btn_return_forward')
        self.hl_frame_forward_return.addWidget(self.btn_return_forward)

        self.btn_return_all_forward = QtWidgets.QPushButton(self.frame_forward_return)
        self.btn_return_all_forward.setMinimumSize(20, 20)
        self.btn_return_all_forward.setMaximumSize(20, 20)
        self.btn_return_all_forward.setToolTip('Вернуть все изменения')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(ICO_FOLDER, 'icon_return_all_forward.png')), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_return_all_forward.setIcon(icon)
        self.btn_return_all_forward.setToolTip('Вернуть все изменения')
        self.btn_return_all_forward.setObjectName('btn_return_all_forward')
        self.hl_frame_forward_return.addWidget(self.btn_return_all_forward)
        # ------------------------------------------------------------------------------------------------#
        self.btn_update_tree = QtWidgets.QPushButton(self)
        self.btn_update_tree.setObjectName('btn_update_tree')
        self.btn_update_tree.setMaximumSize(120, 22)
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
        self.btn_open_tmp_folder.setMaximumSize(25, 22)
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
        self.grid.addWidget(self.tree, counter_row.next(), 0, 1, 4)

        # ------------------------------------------------------------------------------------------------#
        self.btn_return_back.clicked.connect(self.tree.return_text)
        self.btn_return_forward.clicked.connect(self.tree.forward_text)
        self.btn_all_return_back.clicked.connect(self.tree.return_all_text)
        self.btn_return_all_forward.clicked.connect(self.tree.forward_all_text)

        self.delegate = HighlightDelegate(self.tree)
        self.tree.setItemDelegate(self.delegate)
        self.textedit_search_to.textChanged.connect(self.delegate.setSearchText)
        self.textedit_search_to.textChanged.connect(self.tree.viewport().update)

    def fill_tree(self, dict_from_assembly: dict):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Имя компонента в сборке', 'Имя фалйа', 'Относительный путь', 'Правила Ilogic'])
        
        self.dct_rename = {
            'root_assembly': dict_from_assembly['root_assembly'],
            'name_assembly': dict_from_assembly['name_assembly'],
            'new_root_assembly': '',
            'new_name_assembly': '',
            'item': {}
        }

        self.tree.populatet_tree(dict_from_assembly['item'])
        self.tree.expandAll()

        for col in range(self.model.columnCount()):
            self.tree.header().setSectionResizeMode(col, self.tree.header().ResizeToContents)
            content_width = self.tree.sizeHintForColumn(col)
            self.tree.setColumnWidth(col, int(content_width * 1.05))
            self.tree.header().setSectionResizeMode(col, self.tree.header().Interactive)
        
        self.tree.setModel(self.model)
    
    def __click_btn_replace(self) -> None:
        if self.textedit_search_to.text():
            if self.btn_replace.text() == 'Заменить':
                self.__rename_one_item(item=self.model.invisibleRootItem())
            else:
                self.__item_add_text_preffix_or_suffix()

    def __item_add_text_preffix_or_suffix(self, item=None, text=None) -> None:
        if item is None:
            item = self.model.invisibleRootItem()
            text = self.textedit_replace_to.text()
        
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

        self.textedit_search_to.setText(search_to)
        self.textedit_replace_to.setText(replace_to)
        
        self.__rename_one_item(item=self.model.invisibleRootItem())
    
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

            text_search_to = self.textedit_search_to.text()
            text_replace_to = self.textedit_replace_to.text()

            if not self.check_box_register.checkState():
                text_component = text_component.lower()
                text_display_name = text_display_name.lower()
                text_short_filename = text_short_filename.lower()
                text_search_to = text_search_to.lower()
                text_replace_to = text_replace_to.lower()

            item_component_name.setText(text_component.replace(text_search_to, text_replace_to))
            item_display_name.setText(text_display_name.replace(text_search_to, text_replace_to))
            item_short_filename.setText(text_short_filename.replace(text_search_to, text_replace_to))

            if dict_rules:
                for name, text_rules in dict_rules.items():
                    dict_rules[name] = text_rules.replace(text_search_to, text_replace_to)

            self.__rename_one_item(item=item.child(i, 0)) 
    
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
        text = self.textedit_search_to.text()
        self.textedit_search_to.setText(text[1:])
        self.textedit_search_to.setText(text)

    def click_check_box_preffix(self, value: bool) -> None:
        self.textedit_search_to.setEnabled(not value)
        self.check_box_register.setEnabled(not value)
        self.check_box_suffix.setEnabled(not value)
        self.btn_replace.setText('Добавить' if value else 'Заменить')

    def click_check_box_suffix(self, value: bool) -> None:
        self.textedit_search_to.setEnabled(not value)
        self.check_box_register.setEnabled(not value)
        self.check_box_preffix.setEnabled(not value)
        self.btn_replace.setText('Добавить' if value else 'Заменить')

    def get_dict(self) -> dict:
        if self.dct_rename:
            self.dct_rename['item'].clear()
            self.__get_dict(self.model.invisibleRootItem())
            return self.dct_rename

    def __get_dict(self, item):
        for i in range(item.rowCount()):
            item_component_name = item.child(i, 0)
            item_display_name = item.child(i, 1)
            item_short_filename = item.child(i, 2)
            item_rules = item.child(i, 3)

            if not self.dct_rename['new_name_assembly']:
                self.dct_rename['new_name_assembly'] = item_component_name.text() + '.iam'
                self.dct_rename['rules'] = item_rules.rules
            else:
                # item_short_filename.name --> '\dir1\dir2\file1.ipt' --> [1:] убирает слэш вначале
                full_file_path = os.path.join(self.dct_rename['root_assembly'], item_short_filename.name[1:] + item_short_filename.type_file)

                self.dct_rename['item'][full_file_path] = {
                    'component_name': (item_component_name.name, item_component_name.text()),
                    'display_name': (item_display_name.name, item_display_name.text()),
                    'short_filename': (item_short_filename.name + item_short_filename.type_file, strip_path(item_short_filename.text()) + item_short_filename.type_file),
                    'rules': item_rules.rules
                }
            self.__get_dict(item_component_name)

    def switch_rule_tree(self, event: bool):
        if self.flag_switch_tree:
            self.tree.hide()
            self.btn_replace_all.show()
            self.btn_return_back.hide()
            self.btn_return_forward.hide()
            self.btn_all_return_back.hide()
            self.btn_return_all_forward.hide()
            self.btn_open_tmp_folder.hide()
            self.btn_update_tree.hide()

        else:
            self.tree.show()
            self.btn_replace_all.hide()
            self.btn_return_back.show()
            self.btn_return_forward.show()
            self.btn_all_return_back.show()
            self.btn_return_all_forward.show()
            self.btn_open_tmp_folder.show()
            self.btn_update_tree.show()

        self.flag_switch_tree = not self.flag_switch_tree

    def update_tree(self) -> None:
        if self.dct_rename:
            self.signal_update_tree.emit(os.path.join(self.dct_rename['root_assembly'], self.dct_rename['name_assembly']))

    def clear_date_dict(self) -> None:
        self.dct_rename = None

    def switch_enabled_widgets(self, value: bool) -> None:
        for widgets in self.children():
            if isinstance(widgets, QtWidgets.QPushButton) or isinstance(widgets, QtWidgets.QLineEdit) or isinstance(widgets, QtWidgets.QFrame):
                widgets.setEnabled(value)
    
    def open_tmp_folder(self) -> None:
        if self.dct_rename:
            root_assmbly = self.dct_rename['root_assembly']
            if os.path.exists(root_assmbly):
                os.system(f"explorer {root_assmbly}")
                return
        os.system(f"explorer {PATH_TMP}")


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.app = None
        self.pid = None
        self.options_open_document = None
        self.doc = None

        self.prepared_assembly_window = PreparedAssemblyWindow(self)
        self.prepared_assembly_window.signal_get_data.connect(self.get_data_from_prepared_assembly)
        self.thread_inventor = IThread()

        self.initWindow()
        self.initWidgets()
        self.init_thread()

        with open(r'DEBUG\data_assembly.txt', 'r', encoding='utf-8') as file_data_assembly: 
            self.fill_trees(eval(file_data_assembly.read()))
        
    def initWindow(self):
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ICO_FOLDER, 'CopyAssembly.png')))

        with open(os.path.join(PROJECT_ROOT, r'resources\\style.qss')) as style: 
            self.setStyleSheet(style.read())

        # self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(600, 500)
        self.setWindowTitle('CopyAssembly')

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.grid = QtWidgets.QGridLayout(self.centralwidget)
        self.grid.setContentsMargins(5, 0, 5, 0)
        self.grid.setObjectName("gridLayoutCentral")

        self.setCentralWidget(self.centralwidget)

        menuBar = self.menuBar()
        fileMenu = QtWidgets.QMenu(self)
        
        prepared_action = QtWidgets.QAction("&Готовые сборки", self)
        prepared_action.triggered.connect(self.show_window_prepared_assembly)
        menuBar.addAction(prepared_action)

        help_action = QtWidgets.QAction("&Помощь", self)
        help_action.triggered.connect(self.open_instruction)
        menuBar.addAction(help_action)
        
        menuBar.addMenu(fileMenu)

        self.shortcut_search_focus = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+F'), self)
        self.shortcut_search_focus.activated.connect(self.set_focus_search_line_edit)

    def initWidgets(self):
        # ------------------------------------------------------------------------------------------------#
        self.label_choose_assembly = QtWidgets.QLabel(self)
        self.label_choose_assembly.setText('Выберите сборку')
        self.grid.addWidget(self.label_choose_assembly, 0, 0, 1, 1)

        self.textedit_choose_assembly = LineEdit(self)
        self.textedit_choose_assembly.setObjectName('textedit_choose_assembly')
        self.textedit_choose_assembly.textChanged.connect(lambda event: self.textedit_choose_assembly.setStyleSheet("#textedit_choose_assembly {border: 1px solid gray;}"))
        self.grid.addWidget(self.textedit_choose_assembly, 0, 1, 1, 1)
        self.textedit_choose_assembly.setEnabled(False)

        self.btn_choose_path_assembly = QtWidgets.QPushButton(self)
        self.btn_choose_path_assembly.setText('Выбрать')
        self.btn_choose_path_assembly.clicked.connect(self.click_choose_assembly)
        self.grid.addWidget(self.btn_choose_path_assembly, 0, 2, 1, 1)
        # ------------------------------------------------------------------------------------------------#
        self.line_1 = QHLine(self)
        self.grid.addWidget(self.line_1, 2, 0, 1, 3)
        # ------------------------------------------------------------------------------------------------#
        self.frame_tree_assembly = FrameTreeFromDict(self)
        self.frame_tree_assembly.signal_update_tree.connect(self.update_tree)
        self.grid.addWidget(self.frame_tree_assembly, 3, 0, 1, 3)
        # ------------------------------------------------------------------------------------------------#
        self.btn_ok = QtWidgets.QPushButton(self)
        self.btn_ok.setText('OK')
        self.btn_ok.clicked.connect(self.click_ok)
        self.grid.addWidget(self.btn_ok, 4, 0, 1, 3)
        # ------------------------------------------------------------------------------------------------#
        self.frame_load = QtWidgets.QFrame(self)
        self.frame_load.setMaximumSize(160000, 25)
        self.frame_load.setObjectName('frame_load')
        self.grid.addWidget(self.frame_load, 5, 0, 1, 3)

        self.layout_frame_load = QtWidgets.QHBoxLayout(self.frame_load)
        self.layout_frame_load.setContentsMargins(0, 0, 0, 0)

        self.pb_ring = LoadRing(self.frame_load)
        self.layout_frame_load.addWidget(self.pb_ring)

        self.label_load_ring = QtWidgets.QLabel(self.frame_load)
        self.label_load_ring.setObjectName('label_load_ring')
        self.label_load_ring.setText('Готово')
        self.layout_frame_load.addWidget(self.label_load_ring)

    def init_thread(self):
        self.thread_inventor.signal_text_pb.connect(self.change_text_pb)
        self.thread_inventor.signal_pb.connect(self.set_state_pb)
        self.thread_inventor.signal_dict_assembly.connect(self.fill_trees)
        self.thread_inventor.signal_error.connect(self.thread_inventor_error)
        self.thread_inventor.signal_complite_thread.connect(self.thread_inventor_complite)
        self.thread_inventor.signal_is_prepared.connect(self.__full_rename_assembly)

    def thread_inventor_error(self, error_code: ErrorCode) -> None:
        if error_code == ErrorCode.SUCCESS:
            return
        
        self.textedit_choose_assembly.setText('')
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

    def update_tree(self, filepath) -> None:
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
            QtCore.Q_ARG(bool, is_CoInitialize)
            )
        QtCore.QMetaObject.invokeMethod(self.thread_inventor, "run", QtCore.Qt.QueuedConnection)       

    def __full_rename_assembly(self, value: bool) -> None:
        """
        Переименование для готовых сборок. Данные берутся не от пользотеля, а из окна PreparedAssemblyWindow
        """
        if value:
            data = self.prepared_assembly_window.current_data_assembly
            self.textedit_choose_assembly.setText(data['new_name_assembly'] + '.iam')
            self.frame_tree_assembly.rename_item_from_dict(data)
            self.click_ok()
        
    def fill_trees(self, data: dict) -> None:
        self.switch_enabled_widgets(True)
        self.frame_tree_assembly.switch_enabled_widgets(True)
        if data is not None: 
            self.textedit_choose_assembly.setText(tuple(data['item'].keys())[0])
            self.frame_tree_assembly.fill_tree(data)
            
    def change_text_pb(self, string: str):
        self.label_load_ring.setText(string)

    def set_state_pb(self, value: bool) -> None:
        if value:
            self.pb_ring.start_load()
        else:
            self.pb_ring.stop_load()

    def click_ok(self) -> None:
        if self.frame_tree_assembly.flag_switch_tree:
            dct_assembly = self.frame_tree_assembly.get_dict()
            print(dct_assembly)
            return
            if not dct_assembly:
                return

            self.btn_ok.setText('Процесс копирования...')
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
        self.btn_ok.setText('ОК')
        self.switch_enabled_widgets(True)
        self.frame_tree_assembly.switch_enabled_widgets(True)

    def switch_enabled_widgets(self, value: bool) -> None:
        for widgets in self.children():
            if widgets.objectName() == 'centralwidget':
                for w in widgets.children():
                    if isinstance(w, QtWidgets.QPushButton) or isinstance(w, QtWidgets.QLineEdit) or isinstance(w, QtWidgets.QCheckBox):
                        if w.objectName() != 'textedit_choose_assembly':
                            w.setEnabled(value)

    def set_focus_search_line_edit(self) -> None:
        self.frame_tree_assembly.textedit_search_to.setFocus()

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
        loop = QtCore.QEventLoop()
        self.thread_inventor.signal_close.connect(loop.quit)
        QtCore.QMetaObject.invokeMethod(self.thread_inventor, "close", QtCore.Qt.QueuedConnection)
        loop.exec_()
        self.close_application()
        super().closeEvent(event)


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
