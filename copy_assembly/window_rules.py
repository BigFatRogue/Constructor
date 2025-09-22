from copy import deepcopy
import sys
from typing import Optional

from my_function import RowCounter
from PyQt5 import QtCore, QtWidgets, QtGui
from Widgets import MessegeBoxQuestion, QHLineSeparate


class QTextBoxWithZoom(QtWidgets.QTextEdit):
    def wheelEvent(self, event: QtGui.QWheelEvent):
        delta = event.angleDelta().y()
        if (event.modifiers() & QtCore.Qt.ControlModifier):
            if delta < 0:
                self.zoomOut(1)
            elif delta > 0:
                self.zoomIn(5)
        else:
            super().wheelEvent(event)
    


class LineEditWithKeyPress(QtWidgets.QLineEdit):
    signal_press_key_enter = QtCore.pyqtSignal()
    signal_press_key_enter_ctrl = QtCore.pyqtSignal()
    
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Return:
            self.signal_press_key_enter.emit()
            
        if event.key() == QtCore.Qt.Key_Return and event.modifiers() == QtCore.Qt.ControlModifier:
            self.signal_press_key_enter_ctrl.emit()

        super().keyPressEvent(event)


class ListBoxWitrhKeyPress(QtWidgets.QListWidget):
    signal_press_key_enter = QtCore.pyqtSignal()
    signal_press_right = QtCore.pyqtSignal()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Return:
            self.signal_press_key_enter.emit()
        if event.key() == QtCore.Qt.Key_Right:
            self.signal_press_right.emit()
        return super().keyPressEvent(event)


class WindowsViewerRules(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        # self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowTitle('Правила Ilogic')
        self.data: Optional[dict] = None
        self.__copy_data = None
        self.prevIndex = None 

        self.initWidgets()

    def initWidgets(self) -> None:
        self.resize(900, 400)

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.setContentsMargins(5, 5, 5, 5)
        self.grid.setSpacing(5)

        counter_row = RowCounter()

        self.label_name_assembly = QtWidgets.QLabel(self)
        self.label_name_assembly.setText('[Имя сборки]')
        self.label_name_assembly.setMaximumSize(16666, 14)
        self.grid.addWidget(self.label_name_assembly, counter_row.value, 0, 1, 3)

        self.h_line = QHLineSeparate(self)
        self.grid.addWidget(self.h_line, counter_row.next(), 0, 1, 3)

        self.label_search_to = QtWidgets.QLabel(self)
        self.label_search_to.setText('Искать в')
        self.grid.addWidget(self.label_search_to, counter_row.next(), 0, 1, 1)

        self.lineedit_search_to = QtWidgets.QLineEdit(self)
        self.lineedit_search_to.textChanged.connect(self.highlight_text)
        self.grid.addWidget(self.lineedit_search_to, counter_row.value, 1, 1, 1)

        self.check_box_register = QtWidgets.QCheckBox(self)
        self.check_box_register.setText('С учётом регистра')
        self.check_box_register.setCheckState(QtCore.Qt.CheckState(2))
        self.grid.addWidget(self.check_box_register, counter_row.value, 2, 1, 1)

        self.label_replace_to = QtWidgets.QLabel(self)
        self.label_replace_to.setText('Заменить на')
        self.grid.addWidget(self.label_replace_to, counter_row.next(), 0, 1, 1)

        self.linedit_replace_to = LineEditWithKeyPress(self)
        self.setToolTip('Enter, чтобы заменить в этом правиль\nCtrl+Enter, чтобы заменить во всех правилах')
        self.linedit_replace_to.signal_press_key_enter.connect(self.linedit_replace_to_press_enter)
        self.linedit_replace_to.signal_press_key_enter_ctrl.connect(self.linedit_replace_to_press_enter_ctrl)
        self.grid.addWidget(self.linedit_replace_to, counter_row.value, 1, 1, 1)

        self.btn_replace = QtWidgets.QPushButton(self)
        self.btn_replace.setText('Заменить в этом правиле')
        self.btn_replace.clicked.connect(self.click_btn_replace)
        self.grid.addWidget(self.btn_replace, counter_row.value, 2, 1, 1)

        self.btn_replace_all = QtWidgets.QPushButton(self)
        self.btn_replace_all.setText('Заменить во всех правилах')
        self.btn_replace_all.clicked.connect(self.click_btn_replace_all)
        self.grid.addWidget(self.btn_replace_all, counter_row.next(), 2, 1, 1)

        self.list_box = ListBoxWitrhKeyPress(self)
        self.list_box.signal_press_key_enter.connect(self.select_rule)
        self.list_box.signal_press_right.connect(lambda: self.text_box.setFocus())
        self.list_box.clicked.connect(self.select_rule)

        self.text_box = QTextBoxWithZoom(self)

        self.h_line_2 = QHLineSeparate(self)
        self.grid.addWidget(self.h_line_2, counter_row.next(), 0, 1, 3)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.list_box)
        splitter.addWidget(self.text_box)
        splitter.setStretchFactor(1, 1)
        self.grid.addWidget(splitter, counter_row.next(), 0, 1, 3)

    def highlight_text(self):
        cursor = self.text_box.textCursor()
        cursor.beginEditBlock()

        fmt = QtGui.QTextCharFormat()
        fmt.setBackground(QtGui.QColor("transparent"))

        cursor.movePosition(QtGui.QTextCursor.Start)
        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
        cursor.setCharFormat(fmt)

        cursor.endEditBlock()

        search_term = self.lineedit_search_to.text()
        if not search_term:
            return

        highlight_fmt = QtGui.QTextCharFormat()
        highlight_fmt.setBackground(QtGui.QColor("yellow"))

        cursor = self.text_box.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        
        find_flag = QtGui.QTextDocument.FindCaseSensitively if self.check_box_register.checkState() else QtGui.QTextDocument().FindFlag(0)
        while True:
            cursor = self.text_box.document().find(search_term, cursor, find_flag)
            if cursor.isNull():
                break
            cursor.mergeCharFormat(highlight_fmt)

    def linedit_replace_to_press_enter(self) -> None:
        self.click_btn_replace()
    
    def linedit_replace_to_press_enter_ctrl(self) -> None:
        self.click_btn_replace_all()

    def fill_data(self, data) -> None:
        if self.data:
            self.data = None
        if data is not None:
            self.data = data

            for title in data.keys():
                self.list_box.addItem(title)

    def check_changes(self, rule_name: str) -> bool:
        """True - есть изменения, False - нет изменений"""
        clear_text = lambda x: [i.strip() for i in x.split()]

        text_tb = clear_text(self.text_box.toPlainText())
        text_dct = clear_text(self.data[rule_name])

        return text_tb != text_dct

    def select_rule(self) -> None:
        name_rule = self.list_box.currentIndex().data()
        
        if self.prevIndex != name_rule:
            if self.prevIndex:
                if self.check_changes(self.prevIndex):
                    msg = MessegeBoxQuestion(self)
                    if msg.exec() == QtWidgets.QDialog.Accepted:
                        self.data[self.prevIndex] = self.text_box.toPlainText()

            self.prevIndex = name_rule
            text = self.data[name_rule]
            self.text_box.clear()
            self.text_box.setText(text)

    def click_btn_replace(self) -> None:
        self.rename_text_box(self.lineedit_search_to.text(), self.linedit_replace_to.text())

    def click_btn_replace_all(self) -> None:
        self.all_rename_text_box(self.lineedit_search_to.text(), self.linedit_replace_to.text())

    def rename_text_box(self, search: str, to: str) -> None:
        text = self.text_box.toPlainText()
        text = text.replace(search, to)
        self.text_box.setText(text)

    def all_rename_text_box(self, search: str, to: str) -> None:
        self.rename_text_box(search, to)
        self.__copy_data = deepcopy(self.data)
        for key, value in self.data.items():
            self.data[key] = value.replace(search, to)

    def clear(self) -> None:
        self.data = None
        self.prevIndex = None
        self.text_box.clear()
        self.list_box.clear()
    
    def get_rules(self) -> dict:
        if self.data:
            return self.data        

    def set_name_assembly(self, text: str) -> None:
        self.label_name_assembly.setText(text)

    def show(self):
        if self.data:
            item = self.list_box.item(0)
            self.list_box.setCurrentItem(item)
            self.text_box.setText(self.data[item.text()])

        return super().show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        rule_name = self.list_box.currentIndex().data()
        if rule_name:
            if self.check_changes(rule_name):
                msg = MessegeBoxQuestion(self)
                if msg.exec() == QtWidgets.QDialog.Accepted:
                    self.data[rule_name] = self.text_box.toPlainText()
                self.text_box.clear()
                self.text_box.setText(self.data[rule_name])
        
        if self.__copy_data is not None:
            msg = MessegeBoxQuestion(self)
            if msg.exec() == QtWidgets.QDialog.Rejected:
                self.data = deepcopy(self.__copy_data)
            self.__copy_data = None
            if rule_name:
                self.text_box.clear()
                self.text_box.setText(self.data[rule_name])

        return super().closeEvent(event)
    

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.setObjectName("centra_lwidget")

        self.vl = QtWidgets.QVBoxLayout(self.central_widget)

        self.btn = QtWidgets.QPushButton(self)
        self.btn.setText('Модальное окно') 
        self.btn.clicked.connect(self.click_btn) 
        self.vl.addWidget(self.btn)

        self.modal_window = None

        self.click_btn()

    def click_btn(self) -> None:
        if self.modal_window is None:
            self.modal_window = WindowsViewerRules(self)
        
        with open(r'DEBUG\data_assembly.txt', 'r', encoding='utf-8') as data:
            data_dict: dict = eval(data.read())
        key = 'C:\\tmp\\temp assembly\\v1.6 (copy at 19-09-2025$20-13-02)\\ALS.PROJECT.ZONE.XX.00.00.000.iam'
        self.modal_window.fill_data(data=data_dict['item'][key]['rules'])
        self.modal_window.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = WindowsViewerRules()
    
    with open(r'DEBUG\data_assembly.txt', 'r', encoding='utf-8') as data:
        data_dict: dict = eval(data.read())
    key = 'C:\\tmp\\temp assembly\\v1.6 (copy at 19-09-2025$20-13-02)\\ALS.PROJECT.ZONE.XX.00.00.000.iam'
    window.fill_data(data=data_dict['item'][key]['rules'])


    window.show()
    sys.exit(app.exec_())