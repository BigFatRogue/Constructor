import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from ..my_widgets.FrameAddFile import FrameAddFile
from ..my_widgets.GetIconFile import get_preview_file


class WindowAddDB(QtWidgets.QWidget):
    signal_change_detail = QtCore.pyqtSignal(tuple)
    signal_exit_widgets = QtCore.pyqtSignal(bool)

    def __init__(self, parent, name_model='Название модели', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.filepath = None
        self.name_model = name_model

        self.initWindow()
        self.initWidgets()

    def initWindow(self):
        self.centralGrid = QtWidgets.QGridLayout(self)
        self.centralGrid.setContentsMargins(0, 0, 0, 0)
        self.centralGrid.setSpacing(1)
        self.centralGrid.setObjectName("gridLayout")

    def initWidgets(self):
        self.label_dow = FrameAddFile(self, default_directory='', format_file=('.ipt', '.iam'))
        self.label_dow.signal_selected_file_label.connect(self.get_file_path)
        self.label_dow.signal_exit.connect(self.exit_widget)
        self.centralGrid.addWidget(self.label_dow, 0, 0, 1, 1)

    def get_file_path(self, filepath: str):
        self.filepath = filepath
        self.label_dow.hide()

        self.frame = QtWidgets.QFrame(self)
        self.centralGrid.addWidget(self.frame, 0, 0, 1, 1)

        self.gridFrame = QtWidgets.QGridLayout(self.frame)
        self.gridFrame.setContentsMargins(0, 0, 0, 0)
        self.gridFrame.setSpacing(5)
        self.gridFrame.setObjectName("gridLayout")

        self.label_preview = QtWidgets.QLabel(self)
        self.label_preview.setObjectName("label_preview")
        self.label_preview.setMaximumSize(QtCore.QSize(150, 150))
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(get_preview_file(self.filepath))

        pixmap = pixmap.scaled(150, 150)
        self.label_preview.setPixmap(pixmap)
        # self.label_preview.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.gridFrame.addWidget(self.label_preview, 0, 0, 7, 1)

        self.label_title = QtWidgets.QLabel(self)
        self.label_title.setObjectName("label_title")
        self.label_title.setMinimumSize(QtCore.QSize(0, 25))
        self.label_title.setStyleSheet("background-color: rgb(0, 0, 0, 0); color: black;")
        self.label_title.setText(self.name_model)
        self.gridFrame.addWidget(self.label_title, 0, 1, 1, 2)

        self.line_1 = QtWidgets.QFrame(self)
        self.line_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_1.setObjectName("line_1")
        self.gridFrame.addWidget(self.line_1, 2, 1, 1, 2)

        self.label_path = QtWidgets.QLabel(self)
        self.label_path.setObjectName("label_path")
        self.label_path.setMinimumSize(QtCore.QSize(0, 25))
        self.label_path.setStyleSheet("background-color: rgb(0, 0, 0, 0); color: black;")
        self.label_path.setWordWrap(True)
        self.label_path.setText(filepath)
        self.gridFrame.addWidget(self.label_path, 3, 1, 1, 2)

        self.line_2 = QtWidgets.QFrame(self)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridFrame.addWidget(self.line_2, 4, 1, 1, 2)

        self.label_description = QtWidgets.QLabel(self)
        self.label_description.setObjectName("label_description")
        self.label_description.setMinimumSize(QtCore.QSize(0, 25))
        self.label_description.setStyleSheet("background-color: rgb(0, 0, 0, 0); color: black;")
        self.label_description.setText('Описание')
        self.gridFrame.addWidget(self.label_description, 5, 1, 1, 2)

        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setStyleSheet("QTextEdit {border-radius: 5px; background-color: white;}")
        self.gridFrame.addWidget(self.textEdit, 6, 1, 1, 2)

        self.pushButton_ok = QtWidgets.QPushButton(self)
        self.pushButton_ok.setObjectName("pushButton_ok")
        self.pushButton_ok.clicked.connect(self.push_add)
        self.pushButton_ok.setText('Добавить')
        self.gridFrame.addWidget(self.pushButton_ok, 7, 1, 1, 1)

        self.pushButton_cancel = QtWidgets.QPushButton(self)
        self.pushButton_cancel.setObjectName("pushButton_cancel")
        self.pushButton_cancel.clicked.connect(self.cancel)
        self.pushButton_cancel.setText('Отмена')
        self.gridFrame.addWidget(self.pushButton_cancel, 7, 2, 1, 1)

    def cancel(self):
        self.frame.hide()
        self.label_dow.show()

    def push_add(self):
        self.signal_change_detail.emit((self.filepath, self.textEdit.toPlainText()))
        self.signal_exit_widgets.emit(True)

    def exit_widget(self, signal: bool):
        self.signal_exit_widgets.emit(signal)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        centralWidgets = QtWidgets.QWidget(self)
        self.setCentralWidget(centralWidgets)

        self.layout = QtWidgets.QVBoxLayout(centralWidgets)
        self.setLayout(self.layout)

        self.win_add_excel = WindowAddDB(self)
        self.layout.addWidget(self.win_add_excel)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
