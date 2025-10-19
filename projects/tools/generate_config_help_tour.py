import sys
import os 
from tempfile import TemporaryFile
from PyQt5 import QtCore, QtGui, QtWidgets


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'copy_assembly'))
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


class ToolTipMessage(QtWidgets.QWidget): 
    signal_next_step = QtCore.pyqtSignal()
    signal_end = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.old_pos: QtCore.QPoint = None
        self.new_pos: QtCore.QPoint = None
        self.flag_move = False

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.installEventFilter(self)
        self.initWidgets()
    
    def initWidgets(self) -> None:
        self.setStyleSheet('''
                           ToolTipMessage {
                           background-color: white;
                           border: 3px solid #0078d4;
                           border-radius: 5px;
                           padding: 10px;
                           }''')
        self.setMinimumSize(100, 100)
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.grid_layout)

        row_counter = RowCounter()

        self.label_title = QtWidgets.QLabel(self)
        self.label_title.setMaximumHeight(20)
        self.label_title.setObjectName('label_title')
        self.label_title.setText('Шаг 1')
        self.label_title.setStyleSheet('#label_title {}')
        self.grid_layout.addWidget(self.label_title, row_counter.value, 0, 1, 1)

        self.btn_end_tour = QtWidgets.QPushButton(self)
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

        self.line_separate = QHLineSeparate(self)
        self.grid_layout.addWidget(self.line_separate, row_counter.next(), 0, 1, 2)

        self.label_message = QtWidgets.QLabel(self)
        self.label_message.setWordWrap(True)
        self.label_message.setObjectName('label_message')
        self.label_message.setStyleSheet('''
                                        #label_message {
                                        font-size: 12pt; 
                                        }
                                        ''')
        self.label_message.setMinimumWidth(250)
        self.grid_layout.addWidget(self.label_message, row_counter.next(), 0, 1, 2)

        self.label_content = QtWidgets.QLabel(self)
        self.grid_layout.addWidget(self.label_content, row_counter.next(), 0, 1, 2)

        self.btn_next_step = QtWidgets.QPushButton(self)
        self.btn_next_step.setText('Продолжить')
        self.btn_next_step.setObjectName('btn_next_step')
        self.grid_layout.addWidget(self.btn_next_step, row_counter.next(), 0, 1, 2)

    def set_title(self, text: str) -> None:
        self.label_title.setText(text)

    def set_text(self, text: str) -> None:
        self.label_message.setText(text)
    
    def set_content(self, filepath) -> None:
        if filepath:
            gif = QtGui.QMovie(filepath)
            gif.setScaledSize(QtCore.QSize(100, 100))
            self.label_content.setMovie(gif)
            self.label_content.setMaximumSize(100, 100)
            gif.start()
        else:
            self.label_content.clear()


class WindowCreaterConfigHelpTour(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.application = None
        self.helper = None
        self.current_path_content = ""
        self.current_number_step = 0
        self.dict_step = {}

        self.initWindow()
        self.initWidgets()
        self.run_application()

    def initWindow(self) -> None:
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(650, 320)
        self.setWindowTitle('Window Creater Config HelpTour')

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setCentralWidget(self.centralwidget)
        
        self.grid = QtWidgets.QGridLayout(self.centralwidget)
        self.grid.setContentsMargins(9, 9, 9, 9)
        self.grid.setObjectName("gridLayoutCentral")

    def initWidgets(self) -> None:
        self.line_edit_list_object_name = QtWidgets.QLineEdit(self)
        self.line_edit_list_object_name.returnPressed.connect(self.show_step_in_application)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.textChanged.connect(self.text_change)

        self.btn_add_object_name = QtWidgets.QPushButton(self)
        self.btn_add_object_name.setText('Просмотр')
        self.btn_add_object_name.clicked.connect(self.show_step_in_application)
        
        self.btn_prev_step = QtWidgets.QPushButton(self)
        self.btn_prev_step.setText('Предыдущий шаг')
        self.btn_prev_step.clicked.connect(self.prev_step)

        self.btn_netx_step = QtWidgets.QPushButton(self)
        self.btn_netx_step.setText('Следующий шаг')
        self.btn_netx_step.clicked.connect(self.next_step)

        self.combo_box_choose_step = QtWidgets.QComboBox(self)
        self.combo_box_choose_step.addItem(f'Шаг 1')
        self.combo_box_choose_step.view().pressed.connect(self.choose_step_from_index)
        
        self.tool_tip_widget = ToolTipMessage(self)
        
        self.btn_load_content = QtWidgets.QPushButton(self)
        self.btn_load_content.setText('Загрузить файл gif')
        self.btn_load_content.clicked.connect(self.load_content)

        self.btn_del_content = QtWidgets.QPushButton(self)
        self.btn_del_content.setText('Удалить gif')
        self.btn_del_content.clicked.connect(self.del_content)
        
        self.btn_add_value_in_config = QtWidgets.QPushButton(self)
        self.btn_add_value_in_config.setText('Добавить значение в config')
        self.btn_add_value_in_config.clicked.connect(self.add_value_in_config)

        self.btn_del_value_in_config = QtWidgets.QPushButton(self)
        self.btn_del_value_in_config.setText('Удалить значение из config')
        self.btn_del_value_in_config.clicked.connect(self.del_value_in_config)
        
        self.h_separate_1 = QHLineSeparate(self)
        self.h_separate_2 = QHLineSeparate(self)

        self.btn_generate_config = QtWidgets.QPushButton(self)
        self.btn_generate_config.setText('Сохранить config')
        self.btn_load_content.clicked.connect(self.generate_config)
        
        row_counter = RowCounter()

        self.grid.addWidget(self.line_edit_list_object_name, row_counter.value, 0, 1, 3)
        self.grid.addWidget(self.btn_add_object_name, row_counter.value, 3, 1, 1)

        self.grid.addWidget(self.h_separate_1, row_counter.next(), 0, 1, 4)

        self.grid.addWidget(self.text_edit, row_counter.next(), 0, 3, 2)
        self.grid.addWidget(self.btn_prev_step, row_counter.value, 2, 1, 1)
        self.grid.addWidget(self.btn_netx_step, row_counter.value, 3, 1, 1)
        
        self.grid.addWidget(self.combo_box_choose_step, row_counter.next(), 2, 1, 2)
       
        self.grid.addWidget(self.tool_tip_widget, row_counter.next(), 2, 2, 2)

        self.grid.addWidget(self.btn_load_content, row_counter.next(), 0, 1, 1)
        self.grid.addWidget(self.btn_del_content, row_counter.value, 1, 1, 1)

        self.grid.addWidget(self.btn_add_value_in_config, row_counter.next(), 0, 1, 2)
        self.grid.addWidget(self.btn_del_value_in_config, row_counter.value, 2, 1, 2)
            
        self.grid.addWidget(self.h_separate_2, row_counter.next(), 0, 1, 4)

        self.grid.addWidget(self.btn_generate_config, row_counter.next(), 0, 1, 4)

    def text_change(self) -> None:
        text = self.text_edit.toPlainText()
        self.tool_tip_widget.set_text(text)

    def run_application(self) -> None:
        if self.application is None:
            self.application = Window()
            self.desable_event_widgets(self.application)
            self.install_event_filters(self.application)
            
            self.application.show() 

    def clear_step(self) -> None:
        self.line_edit_list_object_name.setText("")
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
            self.line_edit_list_object_name.setText(*step['object_names'])
            self.text_edit.setPlainText(step['message'])
            self.tool_tip_widget.set_content(step['content_path'])
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

    def del_content(self) -> None:
        self.tool_tip_widget.set_content("")

    def show_step_in_application(self) -> None:
        self.delete_helper()
        object_name = self.line_edit_list_object_name.text()

        self.helper = HelperInteractive(self.application)
        data = {
            "0": {
                "object_names": [*[i.strip() for i in object_name.split(',')]],
                "message": self.tool_tip_widget.label_message.text(),
                "content_path": self.current_path_content,
                "button_is_wait": False,
                }
            }
        self.helper._add_config(data)
        self.helper.show()

    def add_value_in_config(self) -> None:
        self.dict_step[str(self.current_number_step)] = {
            "object_names": [*[i.strip() for i in self.line_edit_list_object_name.text().split(',')]],
            "message": self.tool_tip_widget.label_message.text(),
            "content_path": self.current_path_content,
            "button_is_wait": False,
        }
        
        self.current_number_step += 1
        self.add_empty_step()
        self.tool_tip_widget.set_title(f'Шаг {self.current_number_step + 1}')
    
    def del_value_in_config(self) -> None:
        if str(self.current_number_step) in self.dict_step:
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


    def generate_config(self) -> None:
        ...

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
        if event.type() == QtCore.QEvent.MouseButtonPress:
            event: QtGui.QMouseEvent
            global_pos = event.globalPos()
            
            deepest_widget = self.get_deepest_widget_at(parent=self.application, pos=global_pos)
            if deepest_widget:
                widget = deepest_widget[-1]
                
                if self.helper is None:
                    self.line_edit_list_object_name.setText(self.line_edit_list_object_name.text() + "," + widget.objectName())
                    self.line_edit_list_object_name.setText(self.line_edit_list_object_name.text().strip(','))
                    
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

    def closeEvent(self, event):
        if self.application:
            self.application.close()
        return super().closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = WindowCreaterConfigHelpTour()
    window.show()
    sys.exit(app.exec_())