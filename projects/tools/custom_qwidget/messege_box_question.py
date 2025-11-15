from PyQt5 import QtWidgets


class MessegeBoxQuestion(QtWidgets.QDialog):
    def __init__(self, parent, question='Сохранить изменения?', answer_accept='Да', answer_reject='Нет', title='Сохранения изменений'):
        super().__init__(parent)
        self.question = question
        self.text_answer_accept = answer_accept
        self.text_answer_reject = answer_reject
        
        self.setWindowTitle(title)
        self.resize(300, 50)

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