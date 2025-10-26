import sys
import os 
import shutil
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from widget_record_gif_from_app import WidgetRecordGifFromApp

# Добавлене путей к приложению, которое необходимо запустить 
PATH_PROJCETS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_APPLICATION = os.path.join(PATH_PROJCETS, 'copy_assembly')
PATH_SAVE_CONTENT_GIF = os.path.join(PATH_APPLICATION, 'resources', 'gif')
PATH_SAVE_CONTENT_IMAGE = os.path.join(PATH_APPLICATION, 'resources', 'image')

sys.path.append(PATH_PROJCETS)
sys.path.append(PATH_APPLICATION)

from copy_assembly.ca_main import Window
from copy_assembly.ca_widgets.helper_interactive import HelperInteractive



class RowCounter:
    def __init__(self, start=0):
        self.__value = 0
    
    def next(self) -> int:
        self.__value += 1
        return self.value
    
    def __call__(self) -> int:
        return self.next()
    
    @property
    def value(self) -> int:
        return self.__value


class QHLineSeparate(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class MessegeBoxQuestion(QtWidgets.QDialog):
    def __init__(self, parent, question=None, answer_accept=None, answer_reject=None, title='Сохранения изменений'):
        super().__init__(parent)
        self.question = 'Сохранить изменения?' if question is None else question
        self.text_answer_accept = 'Да' if answer_accept is None else answer_accept
        self.text_answer_reject = 'Нет' if answer_reject is None else answer_reject
        
        self.setWindowTitle(title)
        self.resize(300, 50)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addSpacing(20)

        label_dialog = QtWidgets.QLabel()
        label_dialog.setText(self.question)
        vbox.addWidget(label_dialog)
        
        layout = QtWidgets.QHBoxLayout()
        vbox.addLayout(layout)

        button_accept = QtWidgets.QPushButton(self)
        button_accept.setText(self.text_answer_accept)
        button_accept.clicked.connect(self.__accept)
        layout.addWidget(button_accept)

        button_reject = QtWidgets.QPushButton(self)
        button_reject.setText(self.text_answer_reject)
        button_reject.clicked.connect(self.__reject)
        layout.addWidget(button_reject)

        self.setLayout(vbox)

    def __accept(self) -> None:
        self.accept()
    
    def __reject(self) -> None:
        self.reject()


class ToolTipMessage(QtWidgets.QWidget): 
    signal_next_step = QtCore.pyqtSignal()
    signal_end = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.old_pos: QtCore.QPoint = None
        self.new_pos: QtCore.QPoint = None
        self.flag_move = False

        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

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
        self.btn_next_step.setText('Продолжить')
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
            self.btn_next_step.setText('Ожидание..')
        else:
            self.btn_next_step.setEnabled(True)
            self.btn_next_step.setText('Продолжить')


class WindowCreaterConfigHelpTour(QtWidgets.QMainWindow):
    def __init__(self, application):
        super().__init__()
        self.application = application
        self.helper = None
        self.current_path_content = ""
        self.current_number_step = 0
        self.dict_step = {}
        self.widget_record_gif_from_app = None
        self.filepath_config = None

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

    def init_widgets(self) -> None:
        row_counter = RowCounter()

        #--------------------------- Меню  -------------------------------
        menuBar = self.menuBar()

        file_menu = menuBar.addMenu('&Файл')

        file_open = QtWidgets.QAction("&📁 Открыть", self)
        file_open.setShortcut('Ctrl+O')
        file_open.triggered.connect(self.load_config)
        file_menu.addAction(file_open)

        file_save = QtWidgets.QAction("&💾 Сохранить", self)
        file_save.setShortcut('Ctrl+S')
        file_save.triggered.connect(self.save_config)
        file_menu.addAction(file_save)

        file_save_as = QtWidgets.QAction("&💾 Сохранить как", self)
        file_save_as.setShortcut(QtGui.QKeySequence('Ctrl+Alt+S'))
        file_save_as.triggered.connect(self.save_as_config)
        file_menu.addAction(file_save_as)

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

        self.combo_box_choose_step = QtWidgets.QComboBox(self.frame_control_step)
        self.combo_box_choose_step.addItem(f'Шаг 1')
        self.combo_box_choose_step.view().pressed.connect(self.choose_step_from_index)
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
        self.btn_add_value_in_config.clicked.connect(self.add_value_in_config)
        self.gird_frame_control_step.addWidget(self.btn_add_value_in_config, 3, 0, 1, 2)

        self.btn_del_value_in_config = QtWidgets.QPushButton(self)
        self.btn_del_value_in_config.setText('🗑️')
        self.btn_del_value_in_config.setToolTip('Удалить шаг')
        self.btn_del_value_in_config.setMaximumSize(25, 25)
        self.btn_del_value_in_config.clicked.connect(self.del_value_in_config)
        self.gird_frame_control_step.addWidget(self.btn_del_value_in_config, 3, 2, 1, 1)
        
    def text_change(self) -> None:
        text = self.text_edit.toPlainText()
        self.tool_tip_widget.set_text(text)

    def run_application(self) -> None:
        self.application = self.application()
        self.desable_event_widgets(self.application)
        self.install_event_filters(self.application) 
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
        if self.dict_step:
            self.combo_box_choose_step.setCurrentIndex(self.current_number_step)
            step = self.dict_step[str(self.current_number_step)]
            self.lineedit_list_object_name.setText(*step['object_names'])
            self.text_edit.setPlainText(step['message'])
            self.current_path_content = step['content_path']
            self.tool_tip_widget.set_content(self.current_path_content)
            self.tool_tip_widget.set_title(f'Шаг {self.current_number_step + 1}')

    def prev_step(self) -> None:
        if self.current_number_step - 1 >= 0:
            self.current_number_step -= 1
            self.show_step()
    
    def next_step(self) -> None:
        if self.current_number_step < len(self.dict_step) - 1:
            self.current_number_step += 1
            self.show_step()
    
    def choose_step_from_index(self, index) -> None:
        row = self.combo_box_choose_step.model().itemFromIndex(index).row()
        self.current_number_step = row
        self.show_step()

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
            name = f'helper_inter_step_{self.current_number_step}.gif'
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
        self.tool_tip_widget.set_content(full_file_name)
        self.current_path_content = full_file_name

    def close_widget_mp4_to_gif(self) -> None:
        self.widget_record_gif_from_app = None

    def show_step_in_application(self) -> None:
        self.delete_helper()
        object_name = self.lineedit_list_object_name.text()
        self.helper = HelperInteractive(self.application)
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

    def add_value_in_config(self) -> None:
        self.dict_step[str(self.current_number_step)] = {
            "object_names": [*[i.strip() for i in self.lineedit_list_object_name.text().split(',')]],
            "message": self.tool_tip_widget.label_message.text(),
            "content_path": self.current_path_content,
            "button_is_wait": self.check_box_is_wait.isChecked(),
        }
        
        self.current_number_step += 1
        self.add_empty_step()
        self.tool_tip_widget.set_title(f'Шаг {self.current_number_step + 1}')
    
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

    def click_check_box_is_wait(self) -> None:
        self.tool_tip_widget.set_button_is_wait(self.check_box_is_wait.isChecked())

    def save_config(self) -> None:
        if self.filepath_config is None:
            self.save_as_config()
        else:
            self.__save_config(filename=self.filepath_config)

    def save_as_config(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getSaveFileName(self, 'Сохранить файл', 'config_helper_interactive', filter='JSON файл (*.json)')
        if filename[0]:
            self.filepath_config = filename[0]
            self.__save_config(filename=self.filepath_config )

    def __save_config(self, filename) -> None:
        dict_step = {'steps': self.dict_step}
        with open(filename, 'w', encoding='utf-8') as config_file:
            json.dump(dict_step, config_file, ensure_ascii=False)

    def load_config(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getOpenFileName(self, 'Выбрать файл', filter='JSON файл (*.json)')
        if filename[0]:
            with open(filename[0], 'r', encoding='utf-8') as config_file:
                dict_step: dict = json.load(config_file) 
            if dict_step:
                self.dict_step = dict_step.get('steps')
                self.combo_box_choose_step.clear()
                for i in self.dict_step.keys():
                    self.combo_box_choose_step.addItem(f'Шаг {int(i) + 1}')
            self.current_number_step = 0
            self.show_step()

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
            event: QtGui.QMouseEvent
            global_pos = event.globalPos()
            
            deepest_widget = self.get_deepest_widget_at(parent=self.application, pos=global_pos)
            if deepest_widget:
                widget = deepest_widget[-1]
                
                if self.helper is None:
                    self.lineedit_list_object_name.setText(self.lineedit_list_object_name.text() + "," + widget.objectName())
                    self.lineedit_list_object_name.setText(self.lineedit_list_object_name.text().strip(','))
                    
            return True

        return super().eventFilter(obj, event)

    def get_deepest_widget_at(self, parent, pos, widgets=[]):
        for child in parent.children():
            if isinstance(child, QtWidgets.QWidget):
                if hasattr(child, 'mapToGlobal'):
                    point = child.mapToGlobal(QtCore.QPoint(0, 0))
                    rect = child.rect()
                    global_rect = QtCore.QRect(point.x(), point.y(), rect.width(), rect.height())
                    if global_rect.contains(pos):
                        widgets.append(child)
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
        try:
            if self.application:
                self.application.close()
        except Exception:
            pass
        return super().closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = WindowCreaterConfigHelpTour(application=Window)
    window.show()
    sys.exit(app.exec_())