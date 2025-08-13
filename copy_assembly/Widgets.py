from PyQt5 import QtWidgets
from error_code import ErrorCode


class MessegeBoxQuestion(QtWidgets.QDialog):
    def __init__(self, parent, question=None, answer_accept=None, answer_reject=None):
        super().__init__(parent)
        self.question = 'Сохранить изменения?' if question is None else question
        self.text_answer_accept = 'Да' if answer_accept is None else answer_accept
        self.text_answer_reject = 'Нет' if answer_reject is None else answer_reject
        
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

class MessageInforation(QtWidgets.QMessageBox):
    def __init__(self):
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setWindowTitle('Внимание')
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        
    def set_error(self, error_code: ErrorCode) -> None:
        self.setText(f'{error_code.message}\n{error_code.description}')