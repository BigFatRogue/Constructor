import sys
import pathlib
from dataclasses import dataclass
from PyQt5 import QtCore, QtGui, QtWidgets

from src.my_widgets.SearchLine import SearchLine
from src.my_widgets.MyToolBar import MyToolBar
from src.my_widgets.WidgetsAddExcel import WidgetsAddExcel
from src.my_widgets.ButtonExcel import ButtonExcel

from src.function.GetData import get_from_excel, get_selection_screen, block_dict



@dataclass
class StateWindow:
    excel = 'excel'
    toolbox = 'toolbox'


class Thread(QtCore.QThread):
    blocks = None
    __instance = None

    signal_sellect = QtCore.pyqtSignal(dict)
    signal_progressbar = QtCore.pyqtSignal(int)

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        super().__init__()

    def run(self):
        """Как только будет выполнен скирпт block_dict, то он будет направлен в сигнале"""
        if self.blocks is None:
            self.blocks = get_selection_screen(signal=self.signal_progressbar)
        else:
            self.blocks.update(get_selection_screen(signal=self.signal_progressbar))

        data = block_dict(blocks=self.blocks, signal=self.signal_progressbar)
        self.signal_sellect.emit(data)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        self.folder_icon = f'{pathlib.Path(__file__).parent}\\src\\resources\\icons'
        print(self.folder_icon)

        self.data_acad = None
        self.data_excel = None
        self.thread: Thread
        self.state_window = StateWindow.toolbox
        self.init()
        self.init_widgets()

    def init(self):
        self.resize(900, 300)
        self.setWindowTitle('Constructor')

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayoutCentral = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayoutCentral.setContentsMargins(2, 2, 2, 2)

        self.setCentralWidget(self.centralwidget)

    def init_widgets(self):
        self.btn_from_acad = QtWidgets.QPushButton(self)
        self.btn_from_acad.setText('')
        self.btn_from_acad.setMaximumSize(25, 25)
        icon_acad = QtGui.QIcon()
        icon_acad.addPixmap(QtGui.QPixmap(f"{self.folder_icon}/sellect.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_from_acad.setIcon(icon_acad)
        self.btn_from_acad.setIconSize(QtCore.QSize(20, 20))
        self.btn_from_acad.clicked.connect(self.thread_run_data_from_acad)
        self.gridLayoutCentral.addWidget(self.btn_from_acad, 0, 0, 1, 1)

        self.btn_from_exel = ButtonExcel(self, folder_icon=self.folder_icon)
        self.btn_from_exel.clicked.connect(self.show_window_add_from_excel)
        self.gridLayoutCentral.addWidget(self.btn_from_exel, 0, 1, 1, 1)

        self.line_1 = SearchLine(self, default_text='Поиск в базе данных')
        self.gridLayoutCentral.addWidget(self.line_1, 0, 2, 1, 1)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setValue(0)
        self.gridLayoutCentral.addWidget(self.progress_bar, 1, 0, 1, 3)

        self.tool_bar = MyToolBar(self, folder_icon=self.folder_icon)
        self.tool_bar.signal_clear.connect(self.clear_tb)
        self.gridLayoutCentral.addWidget(self.tool_bar, 2, 0, 1, 3)


        # for tag, data in self.data.items():
        #     self.btn = ButtonToolBar(self, title=tag, data=data)
        #     self.gridLayoutCentral.addWidget(self.btn)

    def thread_run_data_from_acad(self) -> None:
        self.thread = Thread()
        self.thread.signal_sellect.connect(self.get_data_from_acad)
        self.thread.signal_progressbar.connect(self.move_progres_bar)
        self.thread.start()

    def get_data_from_acad(self, data_acad: dict) -> None:
        self.tool_bar.add_pages(data_acad, self.data_excel)

    def move_progres_bar(self, value: int) -> None:
        self.progress_bar.setValue(value)

    def show_window_add_from_excel(self, signal: bool):
        if self.state_window != StateWindow.excel and self.data_excel:
            self.data_excel = None
            self.btn_from_exel.setIconButton()

        elif self.state_window != StateWindow.excel and self.data_excel is None:
            self.tool_bar.hide()

            self.win_add_excel = WidgetsAddExcel()
            self.win_add_excel.signal_change_book_sheet.connect(self.get_data_excel)
            self.win_add_excel.signal_exit_widgets.connect(self.exit_window_add_from_excel)
            self.gridLayoutCentral.addWidget(self.win_add_excel, 2, 0, 1, 3)
            self.state_window = StateWindow.excel

    def exit_window_add_from_excel(self, signal: bool):
        self.state_window = StateWindow.toolbox
        self.win_add_excel.hide()
        self.tool_bar.show()

    def get_data_excel(self, book_sheet: tuple):
        self.win_add_excel.hide()
        self.data_excel = get_from_excel(filepath=book_sheet[0], sheet_name=book_sheet[1])
        self.btn_from_exel.setIconButton()
        self.state_window = StateWindow.toolbox
        self.tool_bar.show()

    def clear_tb(self, signal: bool) -> None:
        try:
            self.thread.blocks.clear()
        except AttributeError:
            pass


def my_excepthook(type, value, tback):
    QtWidgets.QMessageBox.critical(
        window, "CRITICAL ERROR", str(value),
        QtWidgets.QMessageBox.Cancel
    )
    sys.__excepthook__(type, value, tback)


if __name__ == '__main__':
    sys.excepthook = my_excepthook

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())