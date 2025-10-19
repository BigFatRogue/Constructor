import os
import pyperclip

from PyQt5 import QtCore, QtGui, QtWidgets, Qt

from ..my_widgets.SearchLine import SearchLine
from ..function.ToInventor import paste_detail_in_inventor
from ..function.HashingArt import my_hash
from ..function.GetFromDB import query_set_db, query_lst_to_str
from ..my_widgets.WindowAddDataBase import WindowAddDB


class TBSearch(SearchLine):
    def __init__(self, parent, default_text: str, *args, **kwargs):
        super().__init__(parent, default_text)


class TBButton(QtWidgets.QWidget):
    signal_view_data = QtCore.pyqtSignal(tuple)
    signal_get_name = QtCore.pyqtSignal(str)

    def __init__(self, parent, folder_icon, title: str, data_acad: dict, data_excel=None, *args, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.title = title
        self.data_acad = data_acad
        self.data_excel = data_excel
        self.icon_folder = folder_icon

        self.init()

    def init(self):
        self.setObjectName(self.title)
        self.setToolTip(self.title)

        self.centralLayout = QtWidgets.QVBoxLayout(self)
        self.centralLayout.setSpacing(1)
        self.centralLayout.setContentsMargins(3, 3, 3, 3)

        self.frame = QtWidgets.QFrame(self)
        self.frame.setMaximumSize(16777215, 25)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.btn_main = QtWidgets.QPushButton(self.frame)
        self.btn_main.setObjectName('btn_main')
        self.btn_main.setText(self.title)
        self.btn_main.setMinimumSize(0, 20)
        self.btn_main.setMaximumSize(16777215, 20)

        self.btn_main.setStyleSheet("""
        #btn_main {
        background-color: rgb(159, 103, 255);
        color: white;
        border-top: 1px solid black;
        border-bottom: 1px solid black;
        border-top-left-radius: 3px;
        border-bottom-left-radius: 3px;
        text-align: left;
        padding-left: 5px;
        }
        
        #btn_main:hover {
        background-color: rgb(139, 83, 235);
        }
        
        #btn_main:pressed {
        background-color: rgb(109, 63, 215);
        }
        """)
        self.btn_main.clicked.connect(self.view_data)
        self.horizontalLayout.addWidget(self.btn_main)

        self.btn_copy = QtWidgets.QPushButton(self.frame)
        self.btn_copy.setObjectName('btn_copy')
        self.btn_copy.setMinimumSize(20, 20)
        self.btn_copy.setMaximumSize(0, 20)
        self.btn_copy.setStyleSheet("""
        #btn_copy {
        background-color: rgb(159, 103, 255);
        border-top: 1px solid black;
        border-right: 1px solid black;
        border-bottom: 1px solid black;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
        }
        
        #btn_copy:hover {background-color: rgb(139, 83, 235);}
        #btn_copy:pressed {"background-color: rgb(119, 63, 215);"}""")
        icon = QtGui.QIcon()
        icon.addFile(f"{self.icon_folder}/copy_ico.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_copy.setIcon(icon)
        self.btn_copy.setToolTip('Копировать')
        self.btn_copy.clicked.connect(self.copy_to_buffer)
        self.horizontalLayout.addWidget(self.btn_copy)

        self.centralLayout.addWidget(self.frame)

    def view_data(self):
        self.signal_view_data.emit((self.objectName(), self.data_acad, self.data_excel))

    def copy_to_buffer(self):
        pyperclip.copy(self.title)
        x = self.parent.mapToGlobal(self.pos()).x()
        y = self.parent.mapToGlobal(self.pos()).y()
        QtWidgets.QToolTip.showText(QtCore.QPoint(x + self.width(), y), 'скопировано')

    def active(self):
        self.btn_main.setStyleSheet("""
        #btn_main {
        background-color: rgb(109, 63, 215);
        color: white;
        border-top: 1px solid black;
        border-left: 1px solid black;
        border-bottom: 1px solid black;
        border-top-left-radius: 3px;
        border-bottom-left-radius: 3px;
        text-align: left;
        padding-left: 5px;}
        """)

    def not_active(self):
        self.btn_main.setStyleSheet("""
        #btn_main {
        background-color: rgb(159, 103, 255);
        color: white;
        border-top: 1px solid black;
        border-left: 1px solid black;
        border-bottom: 1px solid black;
        border-top-left-radius: 3px;
        border-bottom-left-radius: 3px;
        text-align: left;
        padding-left: 5px;
        }
        #btn_main:hover {background-color: rgb(139, 83, 235);}
        #btn_main:pressed {background-color: rgb(109, 63, 215);
        """)


class TBTable(QtWidgets.QTableWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent)

        self.rows = 1
        self.cols = 5
        self.title_h_title = ('Артикул', '№', 'Название', 'Технические характеристики', 'Производитель')
        self.init()

        self.__old_cell = None

    def init(self):
        self.setColumnCount(self.cols)
        self.setRowCount(self.rows)

        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setStretchLastSection(True)

        self.setColumnWidth(1, 30)
        self.setColumnWidth(4, 75)

        for i, title in enumerate(self.title_h_title):
            self.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(title))

        self.setObjectName('table_content')
        self.setStyleSheet("""
        #table_content {
        border: 1px solid black;
        background-color: white;
        }
        #table_content:item{
        border: 1px solid black;
        }
        #table_content:item::selected {
        background-color: rgba(50, 50, 250, 15);
        color: black;
        }
        """)

    def fill(self, data):
        def fill_sector(t: str, dt: dict, start: int):
            qItemTitle = QtWidgets.QTableWidgetItem(t)
            qItemTitle.setTextAlignment(QtCore.Qt.AlignCenter)
            font = QtGui.QFont()
            font.setBold(True)
            qItemTitle.setFont(font)
            self.setItem(start, 0, qItemTitle)

            dt_keys = sorted(j for j in dt.keys() if j != 'filepath')
            for y, art in enumerate(dt_keys, start + 1):
                value = dt[art]
                for i, item in enumerate((art, *value)):
                    item_str = str(item)
                    qItem = QtWidgets.QTableWidgetItem(item_str)
                    if item_str != 'None':
                        self.setItem(y, i, qItem)
                        self.setSpan(y, i, 1, 1)
                        qItem.setToolTip(item_str)

        data_acad, data_excel = data
        for i, title in enumerate(self.title_h_title):
            self.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(title))

        countRow = len(data_acad) if data_excel is None else len(data_acad) + len(data_excel) + 1
        widthtable = 45 + 25 * len(data_acad) if data_excel is None else 45 + 25 * (len(data_acad) + len(data_excel) + 2)
        self.setRowCount(countRow)
        self.setMinimumSize(16777215, widthtable)

        fill_sector('Autocad', data_acad, 0)
        self.setSpan(0, 0, 1, 5)
        if data_excel:
            fill_sector('Спецификация', data_excel, len(data_acad))
            self.setSpan(len(data_acad), 0, 1, 5)

    def resize_viewport(self):
        w = self.viewport().width()
        ww = w//(self.cols - 1)
        for i in range(2, self.cols - 1):
            self.setColumnWidth(i, ww)

        self.setColumnWidth(1, 30)
        self.setColumnWidth(4, 75)

    def resizeEvent(self, e):
        self.resize_viewport()
        super().resizeEvent(e)


class TBFrameControl(QtWidgets.QWidget):
    signal_view_data = QtCore.pyqtSignal(tuple)
    signal_clear_tb = QtCore.pyqtSignal(bool)

    def __init__(self, parent, folder_icon, *args, **kwargs):
        super().__init__(parent)
        self.data = {}
        self.data_acad, self.data_excel = None, None
        self.count_button = 0
        self.folder_icon = folder_icon
        self.init()

    def init(self):
        self.resize(400, 300)
        self.centralGridLayout = QtWidgets.QGridLayout(self)

        self.search_line = TBSearch(self, default_text='Фильтр')
        self.search_line.signal_enter_text.connect(self.filter)
        self.search_line.signal_event_clear.connect(self.show_control)
        self.centralGridLayout.addWidget(self.search_line, 0, 0, 1, 1)

        self.btn_clear_tb = QtWidgets.QPushButton(self)
        icon_clear_tb = QtGui.QIcon()
        icon_clear_tb.addPixmap(QtGui.QPixmap(f"{self.folder_icon}/clear.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_clear_tb.setIcon(icon_clear_tb)
        self.btn_clear_tb.setIconSize(QtCore.QSize(12, 12))
        self.btn_clear_tb.clicked.connect(self.clear_tb)
        self.btn_clear_tb.setObjectName("clear-button")
        self.btn_clear_tb.setStyleSheet("""#clear-button {color: white;background-color: rgba(0, 0, 0, 0);}
        #clear-button:hover {background-color: rgba(250, 220, 220, 255);}""")
        self.centralGridLayout.addWidget(self.btn_clear_tb, 0, 1, 1, 1)

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scrollAreaWidgetContents = QtWidgets.QWidget(self.scroll_area)

        # self.scroll_area.resizeEvent = self.__resizeEvent
        self.scroll_area.setWidget(self.scrollAreaWidgetContents)
        self.scroll_area.setWidgetResizable(True)
        self.centralGridLayout.addWidget(self.scroll_area, 1, 0, 1, 2)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)

    def add_pages(self, data_acad: dict, data_excel=None, update=False) -> None:
        if update:
            data_acad, data_excel = self.data_acad, self.data_excel
        for i, (title, dt_acad) in enumerate(data_acad.items(), self.count_button):
            if title not in self.data:
                title_str = str(title[0]).ljust(15) + '||\t\t' + title[1]
                dt_excel = None
                if data_excel:
                    dt_excel = data_excel.get(title[0])
                btn = TBButton(self.scrollAreaWidgetContents, self.folder_icon, title_str, data_acad=dt_acad, data_excel=dt_excel)
                btn.setObjectName(f'btn_page_{i}')
                btn.signal_view_data.connect(self.view_data)
                self.verticalLayout.addWidget(btn)
                setattr(self, f'btn_page_{i}', btn)
                self.count_button += 1
            else:
                self.count_button += 1
        self.data.update(data_acad)
        self.data_acad, self.data_excel = data_acad, data_excel

        self.verticalLayout.removeItem(self.verticalSpacer)
        # self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Expanding)
        self.verticalLayout.addItem(self.verticalSpacer)

    def clear_tb(self, event) -> None:
        self.data.clear()
        del_lst = []
        for key, obj in self.__dict__.items():
            obj: TBButton
            if 'btn_page' in key:
                self.verticalLayout.removeWidget(obj)
                del_lst.append(key)
        else:
            self.count_button = 0
        for k in del_lst:
            del self.__dict__[k]
        self.signal_clear_tb.emit(True)

    def del_page(self) -> None:
        pass

    def view_data(self, info) -> None:
        obj_name, data_acad, data_excel = info
        for key, obj in self.__dict__.items():
            obj: TBButton
            if 'btn_page' in key:
                if key == obj_name:
                    obj.active()
                else:
                    obj.not_active()

        self.signal_view_data.emit((data_acad, data_excel))

    def filter(self, text: str) -> None:
        for key, value in self.__dict__.items():
            value: TBButton
            if 'btn_page' in key:
                if text.lower() in value.title.lower():
                    value.show()
                else:
                    value.hide()

    def show_control(self):
        for key, value in self.__dict__.items():
            value: QtWidgets.QWidget
            if 'btn_page' in key:
                value.show()
    
    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        for k, v in self.__dict__.items():
            if 'btn_page' in k:
                v.resize(self.scroll_area.geometry().width(), v.geometry().height())

        # self.resize(self.geometry().width(), self.geometry().height())
        super().resizeEvent(event)


class ButtonInContentFrame(QtWidgets.QPushButton):
    def __init__(self, parent, func, tooltip: str, path_icon: str, name: str):
        super().__init__(parent)

        self.setMaximumSize(25, 25)
        self.func = False
        # self.set_function(tooltip=tooltip, path_icon=path_icon, name=name, func=func)

    def set_function(self, func, tooltip, path_icon, name):
        self.setToolTip(tooltip)
        if self.func:
            self.clicked.disconnect()
        else:
            self.func = True
        self.clicked.connect(func)

        icon = QtGui.QIcon()
        icon.addFile(path_icon, QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(23, 23))
        self.setObjectName(name)
        self.setStyleSheet("""
        #{name} {{color: white;background-color: rgba(0, 0, 0, 0);}}
        #{name}:hover {{background-color: rgb(46, 52, 64);}}
        """.format(name=name, color='color'))


class TBContentFrame(QtWidgets.QFrame):
    signal_update_tool_bar = QtCore.pyqtSignal(str)

    def __init__(self, parent, folder_icon, *args, **kwargs):
        super().__init__(parent)
        self.folder_icon = folder_icon
        self.filepath_detail = None
        self.data = None
        self.init()

    def init(self):
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setContentsMargins(1, 1, 1, 1)

        self.setMaximumSize(16777215, 16777215)
        self.setStyleSheet('QFrame {background-color: rgb(128, 128, 128);}')

        self.frame_content = QtWidgets.QFrame(self)
        self.gridLayout.addWidget(self.frame_content, 0, 0, 1, 1)

        self.grid_layout_frame_content = QtWidgets.QGridLayout(self.frame_content)
        self.grid_layout_frame_content.setSpacing(5)
        self.grid_layout_frame_content.setContentsMargins(1, 1, 1, 1)

        self.table = TBTable(self)
        self.grid_layout_frame_content.addWidget(self.table, 1, 0, 1, 3)

        self.config_inv = (self, self.add_to_inventor, 'Добавить компонент в Inventor', f"{self.folder_icon}/inventor.png", 'btn_inventor')
        self.config_folder = (self, self.open_folder, 'Открыть папку с файлом', f"{self.folder_icon}/folder.png", 'btn_open_folder')
        self.config_add_db = (self, self.show_window_add_db, 'Добавить компонент в Inventor', f"{self.folder_icon}/add_database.png", 'btn_add_bd')

        self.btn_inv_db = ButtonInContentFrame(*self.config_inv)
        self.btn_open_folder = ButtonInContentFrame(*self.config_folder)

        self.grid_layout_frame_content.addWidget(self.btn_inv_db, 0, 0, 1, 1)
        self.grid_layout_frame_content.addWidget(self.btn_open_folder, 0, 1, 1, 1)

        self.verticalSpacer = QtWidgets.QSpacerItem(20, 40, Qt.QSizePolicy.Minimum, Qt.QSizePolicy.Expanding)
        self.grid_layout_frame_content.addItem(self.verticalSpacer, 2, 0, 1, 3)

    def init_inventor(self):
        self.btn_inv_db.set_function(*self.config_inv[1:])
        self.btn_open_folder.show()
        self.btn_open_folder.set_function(*self.config_folder[1:])

    def init_add_db(self):
        self.btn_inv_db.set_function(*self.config_add_db[1:])
        self.btn_open_folder.hide()

    def update_content(self, data: tuple):
        filepath = data[0]['filepath']
        self.filepath_detail = filepath if filepath else None
        if self.filepath_detail:
            self.init_inventor()
        else:
            self.init_add_db()

        self.table.clear()
        self.data = data
        self.table.fill(data)

    def add_to_inventor(self, event):
        if self.filepath_detail:
            print(self.filepath_detail[0][0])
            paste_detail_in_inventor(self.filepath_detail[0][0])

    def open_folder(self, event):
        if self.filepath_detail:
            filepath: str = self.filepath_detail[0][0]
            folderpath = '\\'.join(filepath.split('/')[:-1])
            os.system(f'explorer {folderpath}')
            print(folderpath)

    def show_window_add_db(self, event):
        self.frame_content.hide()

        data_acad, data_excel = self.data
        self.attrs = [i for i in data_acad.keys() if i != 'filepath']
        arts_str = '  |  '.join(self.attrs)

        self.window_add_db = WindowAddDB(self, name_model=arts_str)
        self.window_add_db.signal_exit_widgets.connect(self.exit_add_db)
        self.window_add_db.signal_change_detail.connect(self.add_detail_db)
        self.gridLayout.addWidget(self.window_add_db, 0, 0, 1, 1)

    def add_detail_db(self, info):
        filepath, des = info
        hash_name = my_hash(self.attrs)
        values = hash_name, filepath, des
        #
        values = query_lst_to_str(values)
        query_1 = f"INSERT INTO dbo.co_detail (hash, filepath, description) VALUES {values}"
        query_set_db(query_1)

        for art in self.attrs:
            values_2 = query_lst_to_str((hash_name, art))
            query_2 = f"INSERT INTO dbo.co_hashdetail (hash, artikul) VALUES {values_2}"
            query_set_db(query_2)

        self.signal_update_tool_bar.emit(filepath)

    def exit_add_db(self):
        self.window_add_db.hide()
        self.frame_content.show()

    def clear(self):
        self.table.clear()
        self.filepath_detail = ""


class MyToolBar(QtWidgets.QWidget):
    data_acad, data_excel = None, None
    signal_clear = QtCore.pyqtSignal(bool)

    def __init__(self, parent, folder_icon, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.folder_icon = folder_icon
        self.init()

    def init(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.frame_control = TBFrameControl(self, folder_icon=self.folder_icon)
        self.frame_control.signal_view_data.connect(self.update_frame_content)
        self.frame_control.signal_clear_tb.connect(self.clear)
        self.horizontalLayout.addWidget(self.frame_control)

        self.frame_content = TBContentFrame(self, folder_icon=self.folder_icon)
        self.frame_content.signal_update_tool_bar.connect(self.update_tool_bar)
        self.horizontalLayout.addWidget(self.frame_content)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.frame_control)
        splitter.addWidget(self.frame_content)
        splitter.setStretchFactor(1, 1)
        self.horizontalLayout.addWidget(splitter)

    def add_pages(self, data_acad: dict, data_excel=None, update=False) -> None:
        self.frame_control.add_pages(data_acad, data_excel, update)

    def update_frame_content(self, data: tuple):
        self.frame_content.update_content(data)

    def update_tool_bar(self, filepath) -> None:
        self.clear(True)
        self.frame_content.data[0]['filepath'] = ((filepath, ), )
        self.add_pages(self.frame_content.data, None, True)

    def clear(self, signal: bool) -> None:
        self.frame_content.clear()
        self.signal_clear.emit(True)
        self.data_acad, self.data_excel = None, None