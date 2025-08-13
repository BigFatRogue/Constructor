import os
import sys
import ctypes
from PyQt5 import QtCore, QtGui, QtWidgets

from function import *


class MeLineEdit(QtWidgets.QLineEdit):
    signal_text = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)
        self.signal_text.emit(self.text())


class Window(QtWidgets.QMainWindow):
    signal_pb = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.initWindow()
        self.get_variable()
        self.initWidgets()

    def get_variable(self):
        self.name_tmp_assembly, self.path_tmp_copy_to, self.path_from_copy, self.search = get_filepath()

    def initWindow(self):
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(r'resources\icon\ico_bg.png'))

        # self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(400, 190)
        self.setWindowTitle('Дренажный лоток')

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.gridLayoutCentral = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayoutCentral.setContentsMargins(5, 0, 5, 0)
        self.gridLayoutCentral.setObjectName("gridLayoutCentral")

        self.setCentralWidget(self.centralwidget)

    def initWidgets(self):
        self.vLayout = QtWidgets.QGridLayout(self)
        self.vLayout.setContentsMargins(5, 5, 5, 15)
        self.vLayout.setSpacing(5)

        self.label_search = QtWidgets.QLabel(self)
        self.label_search.setText('Текущее имя сборки:')
        self.gridLayoutCentral.addWidget(self.label_search, 0, 0)
        #
        self.lineedit_assembly_name = MeLineEdit(self)
        self.lineedit_assembly_name.setText(self.name_tmp_assembly)
        self.lineedit_assembly_name.setReadOnly(True)
        self.lineedit_assembly_name.setStyleSheet('QLineEdit {color: gray}')
        self.gridLayoutCentral.addWidget(self.lineedit_assembly_name, 0, 1, 1, 2)

        self.label_search = QtWidgets.QLabel(self)
        self.label_search.setText('Искать')
        self.gridLayoutCentral.addWidget(self.label_search, 1, 0)

        self.lineedit_search = MeLineEdit(self)
        self.lineedit_search.setText(self.search)
        self.lineedit_search.setReadOnly(True)
        self.lineedit_search.setStyleSheet('QLineEdit {color: gray}')
        self.gridLayoutCentral.addWidget(self.lineedit_search, 1, 1)

        self.checkbox_edit = QtWidgets.QCheckBox(self)
        self.checkbox_edit.setText('Изменить')
        self.checkbox_edit.setCheckState(QtCore.Qt.CheckState.Unchecked)
        self.checkbox_edit.clicked.connect(self.state_lineedit_search)
        self.gridLayoutCentral.addWidget(self.checkbox_edit, 1, 2)

        self.label_replace_to = QtWidgets.QLabel(self)
        self.label_replace_to.setText('Заменить на')
        self.gridLayoutCentral.addWidget(self.label_replace_to, 2, 0)

        self.lineedit_replace_to = MeLineEdit(self)
        self.lineedit_replace_to.signal_text.connect(self.get_text_lineedit)
        self.gridLayoutCentral.addWidget(self.lineedit_replace_to, 2, 1, 1, 2)

        self.label_new_name_assembly = QtWidgets.QLabel(self)
        self.label_new_name_assembly.setText('Имя сборки')
        self.gridLayoutCentral.addWidget(self.label_new_name_assembly, 3, 0)

        self.lineedit_name_assembly = MeLineEdit(self)
        self.lineedit_name_assembly.setText(self.name_tmp_assembly)
        self.gridLayoutCentral.addWidget(self.lineedit_name_assembly, 3, 1, 1, 2)

        self.pb = QtWidgets.QProgressBar(self)
        self.pb.setAlignment(QtCore.Qt.AlignCenter)
        self.pb.setMaximumSize(10000, 15)
        self.gridLayoutCentral.addWidget(self.pb, 4, 1, 1, 2)

        self.btn_change_folder = QtWidgets.QPushButton(self)
        self.btn_change_folder.setText('Выберите папку')
        self.btn_change_folder.clicked.connect(self.change_folder)
        self.gridLayoutCentral.addWidget(self.btn_change_folder, 5, 1, 1, 2)

    def state_lineedit_search(self):
        if self.checkbox_edit.checkState() == 0:
            self.lineedit_search.setReadOnly(True)
            self.lineedit_search.setStyleSheet('QLineEdit {color: gray}')
        else:
            self.lineedit_search.setReadOnly(False)
            self.lineedit_search.setStyleSheet('QLineEdit {color: black}')

    def get_text_lineedit(self, text: str) -> None:
        new_name = self.name_tmp_assembly.replace(self.lineedit_search.text(), text)
        self.lineedit_name_assembly.setText(new_name)

    def change_folder(self):
        if self.btn_change_folder.text() == 'Готово':
            self.btn_change_folder.setText('Выберите папку')
            self.pb.setValue(0)
            return

        replace_ = self.lineedit_replace_to.text()
        search = self.lineedit_search.text()

        dlg = QtWidgets.QFileDialog()

        filepath = dlg.getExistingDirectory(self, 'Выберете файл')
        if filepath:
            filepath = filepath.replace('/', '\\')

            new_name_assembly, dct_filepath = copy_tmp_assembly_file(path_from_copy=self.path_from_copy,
                                                                     path_tmp_copy_to=self.path_tmp_copy_to,
                                                                     search=self.search,
                                                                     replace_=replace_)
            self.pb.setValue(25)
            dct_filepath = set_dct_filepath(dct_filepath=dct_filepath,
                                            copy_to=filepath,
                                            search=search,
                                            replace_=replace_)

            self.pb.setValue(50)
            new_path_assembly = copy_assembly_inventor(
                path_tmp_assembly=os.path.join(self.path_tmp_copy_to, self.name_tmp_assembly + '.iam'),
                copy_to=filepath,
                new_name_assembly=new_name_assembly,
                dct_filepath=dct_filepath,
                search=search,
                replace_=replace_)

            self.pb.setValue(75)
            copy_assembly_inventor_end(new_path_assembly=new_path_assembly,
                                       search=search, replace_=replace_, copy_to=filepath,
                                       new_name_assembly=new_name_assembly)

            self.pb.setValue(100)
            self.btn_change_folder.setText('Готово')


def my_excepthook(type, value, tback):
    QtWidgets.QMessageBox.critical(
        window, "CRITICAL ERROR", str(value),
        QtWidgets.QMessageBox.Cancel
    )


if __name__ == '__main__':
    sys.excepthook = my_excepthook
    app = QtWidgets.QApplication(sys.argv)

    window = Window()
    window.show()
    sys.exit(app.exec_())
