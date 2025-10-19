from PyQt5 import QtCore, QtGui, QtWidgets, Qt

from ..my_widgets.WindowAddDataBase import FrameAddFile
from ..my_widgets.CustomWindow import *
from ..my_widgets.PriviewExcel import PreviewExcelFile
import os


class WidgetsAddExcel(QtWidgets.QWidget):
    signal_change_book_sheet = QtCore.pyqtSignal(tuple)
    signal_exit_widgets = QtCore.pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filepath = None

        self.initWindow()
        self.initWidgets()

    def initWindow(self):
        self.preview_file: PreviewExcelFile

        self.centralGrid = QtWidgets.QGridLayout(self)
        self.centralGrid.setContentsMargins(0, 0, 0, 0)
        self.centralGrid.setSpacing(1)
        self.centralGrid.setObjectName("gridLayout")

    def initWidgets(self):
        self.label_dow = FrameAddFile(self, default_directory='', format_file=('.xlsx', ))
        self.label_dow.signal_selected_file_label.connect(self.get_file_path)
        self.label_dow.signal_exit.connect(self.exit_widget)
        self.centralGrid.addWidget(self.label_dow, 0, 0, 1, 2)

    def get_file_path(self, filepath):
        self.filepath = filepath
        self.label_dow.hide()

        self.btn_changesheet = QtWidgets.QPushButton(self)
        self.btn_changesheet.clicked.connect(self.change_sheet)
        self.centralGrid.addWidget(self.btn_changesheet, 0, 0, 1, 1)

        self.btn_cancel = QtWidgets.QPushButton(self)
        self.btn_cancel.setText('Отмена')
        self.btn_cancel.setMaximumSize(45, 20)
        self.btn_cancel.clicked.connect(self.cancel)
        self.centralGrid.addWidget(self.btn_cancel, 0, 1, 1, 1)

        self.preview_file = PreviewExcelFile(parent=self, filepath=filepath)
        self.preview_file.signal_change_tab.connect(self.changeEventTab)
        self.centralGrid.addWidget(self.preview_file, 1, 0, 1, 2)

        self.btn_changesheet.setText(f'<html>Выбрать лист: <b>{self.preview_file.currentTab()}>/b</html>')

    def cancel(self):
        self.btn_changesheet.hide()
        self.btn_cancel.hide()
        self.preview_file.hide()
        self.filepath = None
        self.label_dow.show()

    def change_sheet(self):
        book_sheet = self.preview_file.currentTab()
        self.signal_change_book_sheet.emit((self.filepath, book_sheet))

    def changeEventTab(self, title_tab: str):
        self.btn_changesheet.setText(f'Выбрать лист: {title_tab}')

    def exit_widget(self, signal: bool):
        self.signal_exit_widgets.emit(signal)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        centralWidgets = QtWidgets.QWidget(self)
        self.setCentralWidget(centralWidgets)

        self.layout = QtWidgets.QVBoxLayout(centralWidgets)
        self.setLayout(self.layout)

        self.win_add_excel = WidgetsAddExcel(self)
        self.layout.addWidget(self.win_add_excel)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())