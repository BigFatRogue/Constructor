import sys
import os 
from pathlib import Path
from collections import OrderedDict
from datetime import datetime
from typing import Union
import json
from PyQt5 import QtCore, QtGui, QtWidgets

if __name__ == '__main__':
    # Для запуска через IDE
    test_path = str(Path(__file__).parent.parent.parent)
    sys.path.append(test_path)

from projects.tools.settings import LAST_FILE_GEN_CONFIG
from projects.tools.widget_record_gif_from_app import WidgetRecordGifFromApp
from projects.tools.custom_qwidget.custom_combo_box import CustomComboBox
from projects.tools.row_counter import RowCounter
from projects.tools.custom_qwidget.h_line_separate import QHLineSeparate
from projects.tools.custom_qwidget.messege_box_question import MessegeBoxQuestion

# Добавлене путей к приложению, которое необходимо запустить 
PATH_PROJCETS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_APPLICATION = os.path.join(PATH_PROJCETS, 'copy_assembly')
PATH_APPLICATION_RESOURCES = os.path.join(PATH_PROJCETS, 'resources\\ca_resources')
PATH_SAVE_CONTENT_GIF = os.path.join(PATH_APPLICATION_RESOURCES, 'gif')
PATH_SAVE_CONTENT_IMAGE = os.path.join(PATH_APPLICATION_RESOURCES, 'image')

sys.path.append(PATH_PROJCETS)
sys.path.append(PATH_APPLICATION)

from copy_assembly.ca_main import WindowCopyAssembly
from projects.tools.helper_interactive import HelperInteractive


class ToolTipMessage(QtWidgets.QWidget): 
    signal_next_step = QtCore.pyqtSignal()
    signal_end = QtCore.pyqtSignal()

    TEXT_BTN_NEXT_STEP = 'Следующий шаг'
    TEXT_BTN_WAIT = 'Пожалуйста, подождите...'
    TEXT_BTN_END = 'Завершить'

    def __init__(self, parent):
        super().__init__(parent)

        self.old_pos: QtCore.QPoint = None
        self.new_pos: QtCore.QPoint = None
        self.flag_move = False

        self.installEventFilter(self)
        self.init_widgets()
    
    def init_widgets(self) -> None:
        self.setMinimumSize(100, 100)
        self.setStyleSheet('''
                   ToolTipMessage {
                   background-color: white;
                   padding: 5px;
                   }''')
        self.v_layout = QtWidgets.QGridLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.v_layout)

        self.frame_tool_tip = QtWidgets.QFrame(self)
        self.frame_tool_tip.setObjectName('frame_tool_tip')
        self.frame_tool_tip.setStyleSheet('''
                           #frame_tool_tip {
                           background-color: white;
                           border: 3px solid #0078d4;
                           padding: 5px;
                           }''')
        self.v_layout.addWidget(self.frame_tool_tip)
        
        self.grid_layout = QtWidgets.QGridLayout(self.frame_tool_tip)
        self.grid_layout.setSpacing(2)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        
        row_counter = RowCounter()

        self.label_title = QtWidgets.QLabel(self.frame_tool_tip)
        self.label_title.setMaximumHeight(20)
        self.label_title.setObjectName('label_title')
        self.label_title.setStyleSheet('#label_title {}')
        self.label_title.setText('Шаг 1')
        self.grid_layout.addWidget(self.label_title, row_counter.value, 0, 1, 1)

        self.btn_end_tour = QtWidgets.QPushButton(self.frame_tool_tip)
        self.btn_end_tour.setObjectName('btn_end_tour')
        self.btn_end_tour.setMaximumSize(20, 20)
        self.btn_end_tour.setToolTip('Завершить')
        self.btn_end_tour.setText('x')
        self.btn_end_tour.setStyleSheet('''
                                        #btn_end_tour {
                                        border: none;
                                        border-radius: 5px;
                                        padding: 7px;
                                        }
                                        #btn_end_tour:hover {
                                        background-color: rgb(209, 235, 255);
                                        }
                                        ''')
        self.btn_end_tour.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.grid_layout.addWidget(self.btn_end_tour, row_counter.value, 1, 1, 1)

        self.line_separate = QHLineSeparate(self.frame_tool_tip)
        self.grid_layout.addWidget(self.line_separate, row_counter.next(), 0, 1, 2)

        self.label_message = QtWidgets.QLabel(self.frame_tool_tip)
        self.label_message.setObjectName('label_message')
        self.label_message.setWordWrap(True)
        self.label_message.setStyleSheet('''
                                        #label_message {
                                        font-size: 12pt; 
                                        }
                                        ''')
        self.label_message.setMinimumWidth(250)
        self.grid_layout.addWidget(self.label_message, row_counter.next(), 0, 1, 2)

        self.label_content = QtWidgets.QLabel(self.frame_tool_tip)
        self.grid_layout.addWidget(self.label_content, row_counter.next(), 0, 1, 2)

        self.btn_next_step = QtWidgets.QPushButton(self)
        self.btn_next_step.setText(self.TEXT_BTN_NEXT_STEP)
        self.btn_next_step.setObjectName('btn_next_step')
        self.grid_layout.addWidget(self.btn_next_step, row_counter.next(), 0, 1, 2)

    def set_title(self, text: str) -> None:
        self.label_title.setText(text)

    def set_text(self, text: str) -> None:
        self.label_message.setText(text)
        QtCore.QTimer.singleShot(10, self.adjustSize)

    def set_content(self, content_path: str) -> None:
        if content_path:
            gif = QtGui.QMovie(content_path)
            self.label_content.setMovie(gif)
            gif.start()
        else:
            self.label_content.clear()
        QtCore.QTimer.singleShot(10, self.adjustSize)
        
    def set_button_is_wait(self, value: bool=False) -> None:
        if value:
            self.btn_next_step.setEnabled(False)
            self.btn_next_step.setText(self.TEXT_BTN_WAIT)
        else:
            self.btn_next_step.setEnabled(True)
            self.btn_next_step.setText(self.TEXT_BTN_NEXT_STEP)


class ToolTipObjectName(QtWidgets.QWidget):
    signal_choose_widget = QtCore.pyqtSignal(str)
    signal_clear  = QtCore.pyqtSignal()
    signal_show_helper = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.data_mark = None
        self.list_label: list[QtWidgets.QLabel] = []
        
        self.is_click = False
        self.is_move = False
        self.old_pos = QtCore.QPoint(0, 0)

        self.init_widgets()
    
    def init_widgets(self) -> None:
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.v_layout)

        self.setStyleSheet('QFrame {border: 1px solid black; border-radius: 3px; background-color: white;}')

        self.frame_label = QtWidgets.QFrame(self)
        self.v_layout.addWidget(self.frame_label)

        self.grid_layout_frame = QtWidgets.QGridLayout(self.frame_label)
        self.grid_layout_frame.setContentsMargins(2, 2, 2, 2)
        self.grid_layout_frame.setSpacing(2)
        
        self.btn_show_helper = QtWidgets.QPushButton(self.frame_label)
        self.btn_show_helper.setText('🔎')
        self.btn_show_helper.setShortcut('Ctrl+R')
        self.btn_show_helper.clicked.connect(self.signal_show_helper.emit)
        self.btn_show_helper.setMaximumSize(25, 25)
        self.grid_layout_frame.addWidget(self.btn_show_helper, 0, 0, 1, 1)

        self.btn_clear = QtWidgets.QPushButton(self.frame_label)
        self.btn_clear.setText('Очистить')
        self.btn_clear.clicked.connect(self.signal_clear.emit)
        self.grid_layout_frame.addWidget(self.btn_clear, 0, 1, 1, 1)

        self.btn_close = QtWidgets.QPushButton(self.frame_label)
        self.btn_close.setText('❌')
        self.btn_close.setStyleSheet('QPushButton {font-size: 8px; padding: 0px; border: none}')
        self.btn_close.setMaximumSize(15, 15)
        self.btn_close.clicked.connect(self.hide)
        self.grid_layout_frame.addWidget(self.btn_close, 0, 2, 1, 1)

    def __clear_labels(self) -> None:
        for label in self.list_label:
            label.setText('')
            label.hide()
            
    def set_object_names(self, object_names: Union[list, set]) -> None:
        if not self.is_click:
            self.__clear_labels()
            for i, obj_name in enumerate(object_names):
                if i < len(self.list_label):
                    label = self.list_label[i]
                    label.setText(obj_name)
                    label.show()
                else:
                    label = QtWidgets.QLabel(self)
                    label.setStyleSheet('QLabel {border: none; padding: 2px;} QLabel:hover {background-color: #bbebff;}')
                    label.setText(obj_name)
                    self.grid_layout_frame.addWidget(label, i + 1, 0, 1, 3)
                    self.list_label.append(label)

    def set_pos(self, x: int, y: int) -> None:
        if not self.is_click:
            x += 10
            y += 10
            if x + self.width() > self.parent().width():
                x = self.parent().width() - self.width() - 10
            if y + self.height()  > self.parent().height():
                y = self.parent().height() - self.height() - 10

            self.setGeometry(x, y, self.width(), self.height())
            QtCore.QTimer.singleShot(30, self.adjustSize)
    
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() == QtCore.Qt.Key_Escape:
            self.hide()
        return super().keyPressEvent(e)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.RightButton:
            self.is_move = True
            self.old_pos = event.pos()
        if event.button() == QtCore.Qt.LeftButton:
            self.is_click = True
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.RightButton:
            self.is_move = False
        if event.button() == QtCore.Qt.LeftButton:
            self.is_click = False
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.is_move:
            pos = self.geometry().topLeft() + (event.pos() - self.old_pos)
            self.setGeometry(pos.x(), pos.y(), self.width(), self.height()) 
        return super().mouseMoveEvent(event)
    
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() == QtCore.Qt.Key_Escape:
            self.hide()
        return super().keyPressEvent(e)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        for label in self.list_label:
                point = label.mapToGlobal(QtCore.QPoint(0, 0))
                rect = label.rect()
                global_rect = QtCore.QRect(point.x(), point.y(), rect.width(), rect.height())
                if global_rect.contains(event.globalPos()):
                    self.signal_choose_widget.emit(label.text())
        return super().mouseDoubleClickEvent(event)


class WindowCreaterConfigHelpTour(QtWidgets.QMainWindow):
    def __init__(self, application):
        super().__init__()
        self.application = application
        self.helper = None
        self.current_path_content = ""
        self.current_number_step = 0
        self.dict_step = OrderedDict()
        self.widget_record_gif_from_app = None
        self.filepath_config = None
        self.is_autosave = True

        self.init_window()
        self.init_widgets()
        self.run_application()

    def init_window(self) -> None:
        # self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(650, 320)
        self.setWindowTitle('Window Creater Config HelpTour')

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        
        self.grid = QtWidgets.QGridLayout(self.centralwidget)
        self.grid.setContentsMargins(5, 5, 5, 5)
        self.grid.setSpacing(5)
        self.grid.setObjectName("gridLayoutCentral")

        #--------------------------- Меню  -------------------------------
        self.menu_bar = self.menuBar()

        file_menu = self.menu_bar.addMenu('&Файл')

        file_open = QtWidgets.QAction("&📄 Открыть", self)
        file_open.setShortcut('Ctrl+O')
        file_open.triggered.connect(self.load_config)
        file_menu.addAction(file_open)

        load_last_file_menu = file_menu.addMenu("&📄 Последние файлы")
        self.fill_menu_last_file(load_last_file_menu)
        
        file_save = QtWidgets.QAction("&💾 Сохранить", self)
        file_save.setShortcut('Ctrl+S')
        file_save.triggered.connect(self.save_config)
        file_menu.addAction(file_save)

        file_save_as = QtWidgets.QAction("&💾 Сохранить как", self)
        file_save_as.setShortcut(QtGui.QKeySequence('Ctrl+Alt+S'))
        file_save_as.triggered.connect(self.save_as_config)
        file_menu.addAction(file_save_as)

        sitting_menu = self.menu_bar.addMenu('&Инструмены')

        has_autosave = QtWidgets.QAction("&Включить автосхранение", self)
        has_autosave.setCheckable(True)
        has_autosave.setChecked(True)
        has_autosave.triggered.connect(self.toggle_autosave)
        sitting_menu.addAction(has_autosave)

    def init_widgets(self) -> None:
        row_counter = RowCounter()

        #--------------------------- add Object Name -------------------------------
        self.frame_add_object_name = QtWidgets.QFrame(self)
        self.hl_frame_add_object_name = QtWidgets.QHBoxLayout(self.frame_add_object_name)
        self.hl_frame_add_object_name.setContentsMargins(0, 0, 0, 0)
        self.hl_frame_add_object_name.setSpacing(5)
        self.grid.addWidget(self.frame_add_object_name, row_counter.value, 0, 1, 2)
        
        self.label_object_name = QtWidgets.QLabel(self.frame_add_object_name)
        self.label_object_name.setText('objectName:')
        self.label_object_name.setMaximumWidth(75)
        self.hl_frame_add_object_name.addWidget(self.label_object_name)
        
        self.lineedit_list_object_name = QtWidgets.QLineEdit(self.frame_add_object_name)
        self.lineedit_list_object_name.setPlaceholderText('Введите objectName или кликните в дочернем приложении')
        self.lineedit_list_object_name.returnPressed.connect(self.show_step_in_application)
        self.hl_frame_add_object_name.addWidget(self.lineedit_list_object_name)

        self.btn_clear_lineedit_list_object_name = QtWidgets.QPushButton(self.frame_add_object_name)
        self.btn_clear_lineedit_list_object_name.setText('×')
        self.btn_clear_lineedit_list_object_name.clicked.connect(lambda: self.lineedit_list_object_name.setText(''))
        self.btn_clear_lineedit_list_object_name.setMaximumSize(25, 25)
        self.hl_frame_add_object_name.addWidget(self.btn_clear_lineedit_list_object_name)

        self.btn_add_object_name = QtWidgets.QPushButton(self.frame_add_object_name)
        self.btn_add_object_name.setText('🔎')
        self.btn_add_object_name.setToolTip('Выделить widget[objectName]')
        self.btn_add_object_name.setShortcut('Ctrl+R')
        self.btn_add_object_name.clicked.connect(self.show_step_in_application)
        self.btn_add_object_name.setMaximumSize(25, 25)
        self.hl_frame_add_object_name.addWidget(self.btn_add_object_name)
        
        #--------------------------- content Edit  -------------------------------
        self.frame_content_edit = QtWidgets.QFrame(self)
        self.gird_frame_content_edit = QtWidgets.QGridLayout(self.frame_content_edit)
        self.gird_frame_content_edit.setContentsMargins(0, 0, 0, 0)
        self.gird_frame_content_edit.setSpacing(5)
        self.grid.addWidget(self.frame_content_edit, row_counter.next(), 0, 1, 1)
        
        self.text_edit = QtWidgets.QTextEdit(self.frame_content_edit)
        self.text_edit.textChanged.connect(self.text_change)
        self.text_edit.setPlaceholderText('Введите текст')
        self.gird_frame_content_edit.addWidget(self.text_edit, 0, 0, 1, 3)

        self.btn_create_gif = QtWidgets.QPushButton(self.frame_content_edit)
        self.btn_create_gif.setText('Записать файл gif')
        self.btn_create_gif.clicked.connect(self.create_content)
        self.gird_frame_content_edit.addWidget(self.btn_create_gif, 1, 0, 1, 1)

        self.btn_load_content = QtWidgets.QPushButton(self.frame_content_edit)
        self.btn_load_content.setText('📄')
        self.btn_load_content.setToolTip('Добавить .gif')
        self.btn_load_content.setMaximumSize(25, 25)
        self.btn_load_content.clicked.connect(self.load_content)
        self.gird_frame_content_edit.addWidget(self.btn_load_content, 1, 1, 1, 1)
        
        self.btn_del_content = QtWidgets.QPushButton(self.frame_content_edit)
        self.btn_del_content.setText('🗑️')
        self.btn_del_content.setToolTip('Убрать .gif')
        self.btn_del_content.setMaximumSize(25, 25)
        self.btn_del_content.clicked.connect(self.del_content)
        self.gird_frame_content_edit.addWidget(self.btn_del_content, 1, 2, 1, 1)
        
        #--------------------------- Control / View step  -------------------------------
        self.frame_control_step = QtWidgets.QFrame(self)
        self.gird_frame_control_step = QtWidgets.QGridLayout(self.frame_control_step)
        self.gird_frame_control_step.setContentsMargins(0, 0, 0, 0)
        self.gird_frame_control_step.setSpacing(5)
        self.grid.addWidget(self.frame_control_step, row_counter.value, 1, 1, 1)
        
        self.btn_prev_step = QtWidgets.QPushButton(self.frame_control_step)
        self.btn_prev_step.setText('⬅️')
        self.btn_prev_step.setToolTip('Пердыдущий шаг')
        self.btn_prev_step.setMaximumSize(25, 25)
        self.btn_prev_step.clicked.connect(self.prev_step)
        self.gird_frame_control_step.addWidget(self.btn_prev_step, 0, 0, 1, 1)

        self.combo_box_choose_step = CustomComboBox(self.frame_control_step)
        self.combo_box_choose_step.addItem(f'Шаг 1')
        self.combo_box_choose_step.signal_select_item.connect(self.choose_step_from_index)
        self.combo_box_choose_step.signal_is_swap_item.connect(self.swap_step)
        self.gird_frame_control_step.addWidget(self.combo_box_choose_step, 0, 1, 1, 1)

        self.btn_netx_step = QtWidgets.QPushButton(self.frame_control_step)
        self.btn_netx_step.setText('➡️')
        self.btn_prev_step.setToolTip('Следующий шаг')
        self.btn_netx_step.setMaximumSize(25, 25)
        self.btn_netx_step.clicked.connect(self.next_step)
        self.gird_frame_control_step.addWidget(self.btn_netx_step, 0, 2, 1, 1)

        self.tool_tip_widget = ToolTipMessage(self.frame_control_step)
        self.gird_frame_control_step.addWidget(self.tool_tip_widget, 1, 0, 1, 3)
        
        self.check_box_is_wait = QtWidgets.QCheckBox(self.frame_content_edit)
        self.check_box_is_wait.setText('В режиме ожидания')
        self.check_box_is_wait.clicked.connect(self.click_check_box_is_wait)
        self.gird_frame_control_step.addWidget(self.check_box_is_wait, 2, 0, 1, 3)

        self.btn_add_value_in_config = QtWidgets.QPushButton(self)
        self.btn_add_value_in_config.setText('Добавить шаг')
        self.btn_add_value_in_config.clicked.connect(lambda: self.add_value_in_config(True))
        self.gird_frame_control_step.addWidget(self.btn_add_value_in_config, 3, 0, 1, 2)

        self.btn_del_value_in_config = QtWidgets.QPushButton(self)
        self.btn_del_value_in_config.setText('🗑️')
        self.btn_del_value_in_config.setToolTip('Удалить шаг')
        self.btn_del_value_in_config.setMaximumSize(25, 25)
        self.btn_del_value_in_config.clicked.connect(self.del_value_in_config)
        self.gird_frame_control_step.addWidget(self.btn_del_value_in_config, 3, 2, 1, 1)
        
        #--------------------------- Control / View step  -------------------------------
        self.timer_save = QtCore.QTimer()
        self.timer_save.setInterval(1000 * 3 * 60)
        self.timer_save.timeout.connect(self.__auto_save)
        self.timer_save.start()

        self.label_info = QtWidgets.QLabel(self)
        self.label_info.setText('Автосохранение: Вкл')
        self.grid.addWidget(self.label_info, 3, 0, 1, 1)
        
        self.label_info_2 = QtWidgets.QLabel(self)
        self.grid.addWidget(self.label_info_2, 3, 1, 1, 1)

    def fill_menu_last_file(self, submenu: QtWidgets.QMenu) -> None:
        if os.path.exists(LAST_FILE_GEN_CONFIG):
            with open(LAST_FILE_GEN_CONFIG, 'r', encoding='utf-8') as last_files:
                for filepath in last_files.readlines():
                    btn_action = QtWidgets.QAction(filepath, self)
                    if os.path.exists(filepath):
                        btn_action.triggered.connect(lambda: self.__load_config(filepath))
                        submenu.addAction(btn_action)

    def write_last_file(self) -> None:
        if self.filepath_config:
            with open(LAST_FILE_GEN_CONFIG, 'r+', encoding='utf-8') as last_files:
                if self.filepath_config not in last_files.readlines():
                    last_files.write(f'\n{self.filepath_config}')

    def text_change(self) -> None:
        text = self.text_edit.toPlainText()
        self.tool_tip_widget.set_text(text)

    def run_application(self) -> None:
        self.application = self.application()

        for var, value in self.application.__dict__.items():
            if isinstance(value, HelperInteractive):
                setattr(self.application, var, None)
        
        self.desable_event_widgets(self.application)
        self.install_event_filters(self.application) 

        self.tool_tip_choose_widget = ToolTipObjectName(self.application)
        self.tool_tip_choose_widget.signal_choose_widget.connect(self.add_object_name)
        self.tool_tip_choose_widget.signal_clear.connect(lambda: self.lineedit_list_object_name.setText(''))
        self.tool_tip_choose_widget.signal_show_helper.connect(self.show_step_in_application)
        self.tool_tip_choose_widget.hide()

        self.application.show() 

    def clear_step(self) -> None:
        self.lineedit_list_object_name.setText("")
        self.text_edit.setPlainText("")
        self.tool_tip_widget.set_content("")
        self.tool_tip_widget.set_title(f'Шаг {self.current_number_step}')

    def add_empty_step(self) -> None:
        if str(self.current_number_step) not in self.dict_step:
            self.dict_step[str(self.current_number_step)] = {
                "object_names": [""],
                "message": "",
                "content_path": "",
                "button_is_wait": False,
            }
            self.combo_box_choose_step.addItem(f'Шаг {self.current_number_step + 1}')
        self.show_step()

    def show_step(self) -> None:
        if self.dict_step and self.current_number_step is not None:
            if str(self.current_number_step) in self.dict_step:
                self.combo_box_choose_step.setCurrentIndex(self.current_number_step)
                step = self.dict_step[str(self.current_number_step)]
                object_names = step['object_names'] if step['object_names'] else ['']
                if step['content_path']:
                    path_content = os.path.join(PATH_APPLICATION_RESOURCES, step['content_path'])
                else: 
                    path_content = ''
                self.current_path_content = path_content

                self.lineedit_list_object_name.setText(','.join(object_names))
                self.text_edit.setPlainText(step['message'])
                self.tool_tip_widget.set_content(path_content)
                self.tool_tip_widget.set_title(f'Шаг {self.current_number_step + 1}')
                self.check_box_is_wait.setCheckState(step['button_is_wait'])

    def prev_step(self) -> None:
        if self.current_number_step - 1 >= 0:
            self.current_number_step -= 1
            self.show_step()
    
    def next_step(self) -> None:
        if self.current_number_step < len(self.dict_step) - 1:
            self.current_number_step += 1
            self.show_step()
    
    def swap_step(self, data) -> None:
        self.combo_box_choose_step.clear()
        start_index, end_index = data
        steps_value = list(self.dict_step.values())
        start_item = steps_value.pop(start_index)
        steps_value.insert(end_index, start_item)
        
        new_dict = OrderedDict()
        for i, value in enumerate(steps_value):                        
            new_dict[str(i)] = value
            self.combo_box_choose_step.addItem(f'Шаг {i + 1}')
        self.dict_step = new_dict

        self.rename_content_path()

    def rename_content_path(self) -> None:
        dict_queue_rename: dict[str, tuple] = {}
        for step, value in self.dict_step.items():
            if value['content_path']:
                content_path = value['content_path']
                base_name = os.path.basename(content_path)
                stem, suffix = base_name.split('.')

                list_content_path = stem.split('_')
                if list_content_path[-1] != step:
                    new_filename = f'{"_".join(list_content_path[:-1])}_{step}.{suffix}'
                    new_content_path = os.path.join(os.path.dirname(content_path), new_filename)
                    try:
                        self.del_content()
                        os.rename(value['content_path'], new_content_path)
                        value['content_path'] = new_content_path
                    except Exception:
                        dict_queue_rename[step] = (value['content_path'], new_content_path)
        
        if dict_queue_rename:
            for _ in range(len(dict_queue_rename)):
                for step, (old_name, new_name) in dict_queue_rename.items():
                    try:
                        os.rename(old_name, new_name)
                        self.dict_step[step]['content_path'] = new_content_path
                        dict_queue_rename.pop(step)
                        break
                    except Exception:
                        continue

    def choose_step_from_index(self, data) -> None:
        index, text = data
        self.current_number_step = index
        self.show_step()

    def add_object_name(self, value: str) -> None:
        text = self.lineedit_list_object_name.text()
        if not text:
            self.lineedit_list_object_name.setText(value)
        else:
            set_obj_name = set()
            if ',' not in text:
                set_obj_name.add(self.lineedit_list_object_name.text())
            else:
                set_obj_name = set(self.lineedit_list_object_name.text().split(','))
            set_obj_name.add(value)
            self.lineedit_list_object_name.setText(','.join(set_obj_name))

    def load_content(self) -> None:
        dlg = QtWidgets.QFileDialog()
        dlg.setWindowTitle('Выберете файл')
        dlg.setNameFilter('Изображение (*.gif)')
        dlg.selectNameFilter('Изображение (*.gif)')
        dlg.exec_()
        filepath = dlg.selectedFiles()

        self.current_path_content = filepath[0] if filepath else ""
        self.tool_tip_widget.set_content(self.current_path_content)

    def create_content(self) -> None:
        if self.widget_record_gif_from_app is None:
            self.delete_helper()
            name = f'{self.application.__class__.__name__}_helper_inter_step_{self.current_number_step}.gif'
            full_file_name = os.path.join(PATH_SAVE_CONTENT_GIF, name)
            self.widget_record_gif_from_app = WidgetRecordGifFromApp(self, app=self.application, full_file_gif_name=full_file_name)
            self.widget_record_gif_from_app.signal_close.connect(self.close_widget_mp4_to_gif)
            self.widget_record_gif_from_app.signal_get_path_gif.connect(self.set_content_from_widgets)

        self.widget_record_gif_from_app.show()
        x, y = self.widget_record_gif_from_app.x(), self.widget_record_gif_from_app.y()
        w, h = self.widget_record_gif_from_app.width(), self.widget_record_gif_from_app.height()
        self.widget_record_gif_from_app.setGeometry(x + 50, y + 250, w, h)

    def del_content(self) -> None:
        self.tool_tip_widget.set_content("")
        self.current_path_content = ''

    def set_content_from_widgets(self, full_file_name) -> None:
        print(full_file_name)
        self.tool_tip_widget.set_content(full_file_name)
        self.current_path_content = full_file_name

    def close_widget_mp4_to_gif(self) -> None:
        self.widget_record_gif_from_app = None

    def show_step_in_application(self) -> None:
        self.tool_tip_choose_widget.hide()
        self.delete_helper()
        object_name = self.lineedit_list_object_name.text()
        self.helper = HelperInteractive(self.application, PATH_APPLICATION_RESOURCES)
        object_names = [] if not object_name else [i.strip() for i in object_name.split(',')]

        data = {
            f"{self.current_number_step}": {
                "object_names": object_names,           
                "message": self.tool_tip_widget.label_message.text(),
                "content_path": self.current_path_content,
                "button_is_wait":  self.check_box_is_wait.isChecked(),
                }
            }

        self.helper._add_config(data)
        self.helper.curent_index_step = self.current_number_step
        self.helper.show()

    def add_value_in_config(self, is_create_step=True) -> None:
        text = self.lineedit_list_object_name.text()
        object_names = []
        if text:
            object_names = [i.strip() for i in self.lineedit_list_object_name.text().split(',')]
        
        if self.current_path_content:
            content_path = os.path.relpath(self.current_path_content, PATH_APPLICATION)
        else:
            content_path = self.current_path_content

        self.dict_step[str(self.current_number_step)] = {
            "object_names": object_names,
            "message": self.tool_tip_widget.label_message.text(),
            "content_path": content_path,
            "button_is_wait": self.check_box_is_wait.isChecked(),
        }
        
        if is_create_step:
            self.current_number_step += 1
            self.add_empty_step()
            self.tool_tip_widget.set_title(f'Шаг {self.current_number_step + 1}')
            self.show_info_add_step()
    
    def show_info_add_step(self) -> None:
        if not self.label_info_2.text():
            self.label_info_2.setText('Шаг добавлен')
        
        opacity = QtWidgets.QGraphicsOpacityEffect(self)
        opacity.setOpacity(1.0)
        self.label_info_2.setGraphicsEffect(opacity)

        animation = QtCore.QVariantAnimation(self)
        animation.setDuration(3000)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.valueChanged.connect(opacity.setOpacity)
        animation.start()

    def del_value_in_config(self) -> None:
        if str(self.current_number_step) in self.dict_step:
            dlg = MessegeBoxQuestion(self, title='Удалить шаг?')
            if dlg.exec():
                del self.dict_step[str(self.current_number_step)]
                self.combo_box_choose_step.clear()

                new_dict = {}
                for i, value in enumerate(self.dict_step.values()):
                    new_dict[str(i)] = value
                    self.combo_box_choose_step.addItem(f'Шаг {i + 1}')
                self.dict_step = new_dict
                self.clear_step()
                self.current_number_step = len(self.dict_step) - 1
                self.show_step()
        
        self.rename_content_path()

    def click_check_box_is_wait(self) -> None:
        self.tool_tip_widget.set_button_is_wait(self.check_box_is_wait.isChecked())

    def save_config(self) -> None:
        if self.filepath_config is None:
            self.save_as_config()
        else:
            self.__save_config(filename=self.filepath_config)
        self.add_value_in_config(is_create_step=False)
        self.rename_content_path()
        now = datetime.now()
        self.label_info.setText(f'Автосохранение: вкл      💾 Сохранено (в {now.hour}:{now.minute}:{now.second})')
        self.write_last_file()

    def save_as_config(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getSaveFileName(self, 'Сохранить файл', 'config_helper_interactive', filter='JSON файл (*.json)')
        if filename[0]:
            self.filepath_config = filename[0]
            self.__save_config(filename=self.filepath_config )

    def __save_config(self, filename) -> None:
        len_dict_step = str(len(self.dict_step) - 1)
        if len_dict_step in self.dict_step:
            last_step = self.dict_step[len_dict_step]
            if not last_step['message']:
                del self.dict_step[len_dict_step]

        dict_step = {'steps': self.dict_step}
        with open(filename, 'w', encoding='utf-8') as config_file:
            json.dump(dict_step, config_file, ensure_ascii=False)

    def __auto_save(self) -> None:
        if self.is_autosave and self.filepath_config:
            self.save_config()
        
    def load_config(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getOpenFileName(self, 'Выбрать файл', filter='JSON файл (*.json)')
        if filename[0]:
            self.__load_config(filename[0])

    def __load_config(self, filepath: str) -> dict:
        with open(filepath, 'r', encoding='utf-8') as config_file:
            dict_step: dict = json.load(config_file)
        if dict_step:
            self.dict_step = dict_step.get('steps')
            self.filepath_config = filepath
            self.combo_box_choose_step.clear()
            for i in self.dict_step.keys():
                self.combo_box_choose_step.addItem(f'Шаг {int(i) + 1}')
            self.current_number_step = 0
            self.show_step()
        print(self.dict_step)

    def toggle_autosave(self, value: bool) -> None:
        self.is_autosave = value
        self.label_info.setText('Автосохранение: ' + ('Вкл' if value else 'Выкл'))

    def desable_event_widgets(self, parent=None) -> None:
        for child in parent.children():
            if hasattr(child, 'setAttribute'):
                child.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            self.desable_event_widgets(child)
    
    def install_event_filters(self, widget):
        widget.installEventFilter(self)
        for child in widget.findChildren(QtCore.QObject):
            if isinstance(child, QtWidgets.QWidget):
                child.installEventFilter(self)

    def eventFilter(self, obj, event: QtGui.QMouseEvent):
        if event.type() == QtCore.QEvent.Move:
            if self.helper:
                self.application.moveEvent(event)
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                if self.helper is None and self.widget_record_gif_from_app is None:
                    event: QtGui.QMouseEvent
                    global_pos = event.globalPos()
                    
                    deepest_widget = self.get_deepest_widget_at(parent=self.application, pos=global_pos)
                    if deepest_widget:
                        set_object_name = set()
                        for widget in deepest_widget:
                            object_name = widget.objectName()
                            if object_name:
                                set_object_name.add(object_name)

                        self.tool_tip_choose_widget.set_object_names(set_object_name)
                        self.tool_tip_choose_widget.set_pos(event.x(), event.y())
                        self.tool_tip_choose_widget.show()
            return True

        return super().eventFilter(obj, event)

    def get_deepest_widget_at(self, parent, pos, widgets=None):
        if widgets is None:
            widgets = set()
        for child in parent.children():
            if isinstance(child, QtWidgets.QWidget):
                if hasattr(child, 'mapToGlobal'):
                    point = child.mapToGlobal(QtCore.QPoint(0, 0))
                    rect = child.rect()
                    global_rect = QtCore.QRect(point.x(), point.y(), rect.width(), rect.height())
                    if global_rect.contains(pos):
                        widgets.add(child)
            self.get_deepest_widget_at(child, pos, widgets)
        return widgets
    
    def delete_helper(self) -> None:
        if self.helper and self.helper.isVisible():
            self.helper.hide()
            self.helper.widget_background.deleteLater()
            self.helper.widget_tool_tip.deleteLater()
            self.helper = None

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if key == QtCore.Qt.Key.Key_Escape:
            self.delete_helper()
        return super().keyPressEvent(event)

    def showEvent(self, event):
        self.application.setGeometry(self.x() + self.width() + 50, self.y(), self.application.width(), self.application.height())   
        return super().showEvent(event)

    def closeEvent(self, event):
        if self.dict_step:
            dlg = MessegeBoxQuestion(self, 'Сохранить конфиг?')
            if dlg.exec(): 
                self.save_config()
        try:
            if self.application:
                self.application.close()
        except Exception:
            pass
        return super().closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = WindowCreaterConfigHelpTour(application=WindowCopyAssembly)
    window.show()
    sys.exit(app.exec_())