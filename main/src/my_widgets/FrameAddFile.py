from PyQt5 import QtCore, QtGui, QtWidgets, Qt


class FrameAddFile(QtWidgets.QFrame):
    signal_selected_file_label = QtCore.pyqtSignal(str)
    signal_exit = QtCore.pyqtSignal(bool)

    def __init__(self, parent, format_file: tuple, default_directory: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.setAcceptDrops(True)
        self.__directory = default_directory
        self.__file_format_filter = format_file
        self.file_path = ''

        self.init()

    def init(self):
        self.setAcceptDrops(True)
        self.setObjectName('frame')
        self.setStyleSheet("""
        #frame {
        background-color:rgb(59, 68, 83);
        border-radius: 15px;
        border:  2px dashed black;
        color: white;}

        #frame:hover {background-color:rgba(46, 52, 64, 150)}
        """)

        self.centralGridLayout = QtWidgets.QGridLayout(self)

        self.horizont_spacer = QtWidgets.QSpacerItem(20, 40, Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Minimum)
        self.centralGridLayout.addItem(self.horizont_spacer, 0, 0, 1, 1)

        self.btn_exit = QtWidgets.QPushButton(self)
        self.btn_exit.setText('x')
        self.btn_exit.setMinimumSize(20, 20)
        self.btn_exit.setMaximumSize(20, 20)
        self.btn_exit.setObjectName('btn_cancel')
        self.btn_exit.setStyleSheet("""
        #btn_cancel {
        border: 0px;
        color: white;
        padding-bottom: 2px;
        }
        #btn_cancel:hover {
        background-color: rgb(255, 0, 0);
        border: 1px solid black;
        border-radius: 4px;
        }
        """)
        self.btn_exit.clicked.connect(self.exit_widget)
        self.centralGridLayout.addWidget(self.btn_exit, 0, 1, 1, 1)

        self.label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label.setText(f"Выберете или перетащите файл\n({', '.join(self.__file_format_filter)})")
        self.centralGridLayout.addWidget(self.label, 1, 0, 1, 2)

    def exit_widget(self):
        self.signal_exit.emit(True)
        self.hide()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            lst_files = event.mimeData().urls()
            if len(lst_files) == 1:
                for url in lst_files:
                    filename = url.fileName()
                    format_file = '.' + filename.split('.')[-1]

                    if format_file in self.__file_format_filter:
                        event.accept()
                    else:
                        event.ignore()

    def dropEvent(self, event: QtGui.QDragEnterEvent):
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()

            self.signal_selected_file_label.emit(filepath)
            event.accept()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        dlg = QtWidgets.QFileDialog()
        dlg.setOption(3)
        file_format_filter = ' '.join(f'*{i}' for i in self.__file_format_filter)
        dlg.setNameFilter(f"Inventor ({file_format_filter})")
        dlg.selectNameFilter(f"Inventor ({file_format_filter})")
        dlg.setDirectory(self.__directory)
        dlg.setWindowTitle('Выберете файл')

        dlg.exec_()

        filepath = dlg.selectedFiles()
        if filepath:
            self.signal_selected_file_label.emit(filepath[0])

