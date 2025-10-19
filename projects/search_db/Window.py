import os
import datetime
import traceback
from CustomWindow import CustomWindow
from MyWidgets import LineEdit, IconLabel
from ToInventor import paste_detail_in_inventor
from SearchTextLine import search_text_line
from GetIconFile import get_preview_file
import sys
from PyQt5 import QtCore, QtGui, QtWidgets


def my_excepthook(type, value, tback):
    QtWidgets.QMessageBox.critical(
        window, "CRITICAL ERROR", str(value),
        QtWidgets.QMessageBox.Cancel
    )
    if not os.path.exists('log_files'):
        os.mkdir('log_files')

    lst_log_files = [i for i in os.listdir('log_files')]
    count_log_files = len(lst_log_files)
    if count_log_files > 10:
        for log_file in lst_log_files[: count_log_files - 10]:
            os.remove(f'log_files\\{log_file}')

    now_time = str(datetime.datetime.today()).replace(':', '$').replace('-', '_').replace(' ', 'Z').split('.')[0]
    with open(fr'log_files\log_error_{now_time}.txt', 'w+', encoding='utf-8') as log_error:
        for row in traceback.format_exception(type, value, tback):
            log_error.write(row)


class Thread(QtCore.QThread):
    __instance = None
    _signal_pixmap_label = QtCore.pyqtSignal(dict)

    def __init__(self, lst, dct):
        super().__init__()
        self.lst: FlowContainer = lst
        self.dct = dct

    def run(self):
        self.lst.clear()
        for label, (filepath, filename) in self.dct.items():
            pixmap = QtGui.QPixmap()
            label: DetailFrame
            pixmap.loadFromData(get_preview_file(filepath))
            pixmap = pixmap.scaled(150, 150)
            label.label_image.setPixmap(pixmap)

            self.lst.addDetail(label, filepath, filename)

        # self._signal_pixmap_label.emit(data)


class DetailFrame(QtWidgets.QWidget):
    def __init__(self, filepath, filename):
        super().__init__()

        self.path_lib = r'\\192.168.1.11\PKODocs\Inventor Project\Библиотека оборудования ALS'
        filepath = filepath.replace("\\\\", "\\")
        self.filepath = f'{self.path_lib}\\{filepath}'

        self.setMaximumSize(170, 500)

        self.label_image = QtWidgets.QLabel()
        self.label_image.setObjectName('label_image')

        self.label_image.setMinimumSize(150, 150)
        self.label_image.setMaximumSize(150, 150)

        self.label_text = QtWidgets.QLabel()
        self.label_text.setObjectName('label_text')
        self.label_text.setMaximumSize(170, 200)

        self.label_text.setText(filename)
        self.label_text.setAlignment(QtCore.Qt.AlignCenter)
        self.label_text.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
        layout.addWidget(self.label_image)
        layout.addWidget(self.label_text)

        self.setFixedSize(layout.sizeHint())

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        print(self.filepath)
        paste_detail_in_inventor(self.filepath)


class FlowContainer(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('gridList')

        self.viewport().setBackgroundRole(QtGui.QPalette.Window)
        self.setFlow(self.LeftToRight)
        self.setWrapping(True)
        self.setMovement(self.Static)
        self.setResizeMode(self.Adjust)

        self.setHorizontalScrollMode(self.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setSpacing(4)


    def addDetail(self, frame, filepath, filename):
        item = QtWidgets.QListWidgetItem(filename)
        item.setFlags(item.flags() & ~(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled))
        self.addItem(item)
        item.setSizeHint(frame.sizeHint())
        self.setItemWidget(item, frame)


class Window(CustomWindow):
    def __init__(self, folder_icon, *args,  **kwargs):
        super().__init__(folder_icon, *args,  **kwargs)

        self.thread = None

        self.path_lib = r'\\192.168.1.11\PKODocs\Inventor Project\Библиотека оборудования ALS'
        self.__old_text = None
        self.dct_pixmap = {}

        self.initWindow()
        self.initWidgets()


    def initWindow(self):
        file = QtCore.QFile(r'css/window.css')
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(file)
        self.setStyleSheet(stream.readAll())

    def initWidgets(self):
        self.main_vert_layout = QtWidgets.QVBoxLayout(self.ContentFrame)
        self.main_vert_layout.setContentsMargins(5, 5, 5, 5)
        self.main_vert_layout.setSpacing(5)
        self.main_vert_layout.setObjectName("main_vert_layout")

        self.tab_widgets = QtWidgets.QTabWidget(self.ContentFrame)
        self.main_vert_layout.addWidget(self.tab_widgets)

        self.tab1 = QtWidgets.QWidget(self.tab_widgets)
        self.layout_tab1 = QtWidgets.QVBoxLayout(self.tab1)
        self.layout_tab1.setContentsMargins(5, 5, 5, 5)
        self.layout_tab1.setSpacing(5)
        self.layout_tab1.setObjectName("layout_tab1")

        self.line_edit_search = LineEdit(parent=self.tab1, text_default='Поиск в БД')
        self.line_edit_search.signal_text.connect(self.search_in_db)
        self.layout_tab1.addWidget(self.line_edit_search)

        self.tab_widgets.addTab(self.tab1, 'Поиск деталей')

        self.list = QtWidgets.QListWidget(self.tab1)
        self.list.setObjectName('list_result_search')
        self.list.setMaximumSize(3000, 100)
        self.layout_tab1.addWidget(self.list)

        self.detail_list = FlowContainer()
        self.layout_tab1.addWidget(self.detail_list)

    def search_in_db(self, event_key_lineEdit: tuple):
        text, event = event_key_lineEdit
        event: QtGui.QKeyEvent

        if text != self.__old_text:
            self.__old_text = text
            if len(text) > 2:
                res = search_text_line(text.lower())
                self.set_list(res)
                self.set_grid(res)
        elif text == '':
            # self.detail_list.clear()
            self.detail_list.clear()

    def set_list(self, res_db):
        self.list.clear()
        for fp, fn in res_db:
            self.list.addItem(fn)

    def thread_run(self):
        if self.thread:
           self.thread.terminate()

        self.thread = Thread(self.detail_list, self.dct_pixmap)
        self.thread.start()

    def set_grid(self, res_db):
        self.dct_pixmap = {}

        count = 0
        for (fp, fn) in res_db:
            try:
                label = DetailFrame(fp, fn)
                fp = fp.replace("\\\\", "\\")
                full_path = f'{self.path_lib}\\{fp}'

                self.dct_pixmap[label] = [full_path, fn]
                # self.detail_list.addDetail(label, fp, fn)
                count += 1
            except Exception:
                pass
            if count > 10:
                break

        self.thread_run()


if __name__ == '__main__':
    sys.excepthook = my_excepthook

    app = QtWidgets.QApplication(sys.argv)

    window = Window(folder_icon=r'application\icon')
    window.show()
    sys.exit(app.exec_())