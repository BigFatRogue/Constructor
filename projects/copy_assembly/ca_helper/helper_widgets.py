import sys
import os
from collections import OrderedDict
from PyQt5 import QtCore, QtWidgets, QtGui
import re

ROOT = os.path.dirname(__file__)


class WindowHelper(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Window)
        # self.setWindowModality(QtCore.Qt.WindowModal)

        self.dict_list_box_item = OrderedDict(
            [
                ('О программе', 'helper_index.html'),
                ('Инструкция', 'helper_instruction.html'),
                ('Готовые сборки', 'helper_preperad_assembly.html'),
                ('Принцип работы программы', 'operating_principle.html')
            ]
        )

        self.dict_html_template = {
            'ROOT': ROOT,
            'item_list_box': '\n'.join([f'<li><a href={page}>{name}</a></li>' for name, page in self.dict_list_box_item.items()])
        }

        self.setWindowTitle('Помощь')
        self.initWidgets()

    def initWidgets(self) -> None:
        self.resize(900, 400)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 5, 5, 5)
        self.v_layout.setSpacing(5)

        self.tmp_btn_update_html = QtWidgets.QPushButton(self)
        self.tmp_btn_update_html.setText('Обновить HTML')
        self.tmp_btn_update_html.clicked.connect(self.update_html)
        self.v_layout.addWidget(self.tmp_btn_update_html)

        self.list_box = QtWidgets.QListWidget(self)
        
        for (item_name, _) in self.dict_list_box_item.items():
            self.list_box.addItem(item_name)
        self.list_box.clicked.connect(self.seltct_item_list_box)

        self.text_box_html = QtWidgets.QTextBrowser(self)
        self.text_box_html.setReadOnly(True)
        self.text_box_html.anchorClicked.connect(self.on_anchor_clicked)
        self.update_html('helper_index.html')

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.list_box)
        splitter.addWidget(self.text_box_html)
        splitter.setStretchFactor(1, 1)
        self.v_layout.addWidget(splitter)
    
    def update_html(self, filename: str) -> None:
        filename = filename if isinstance(filename, str) else 'helper_index.html'
        with open(os.path.join(ROOT, filename), 'r', encoding='utf-8') as html_file:
            html_code = html_file.read()

            for temp in re.findall(r'{{ (.+) }}', html_code):
                html_code = html_code.replace('{{ ' + temp + ' }}', self.dict_html_template.get(temp))
            # list_box_item_thml = '\n'.join([f'<li><a href={page}>{name}</a></li>' for name, page in self.dict_list_box_item.items()])
            # html_code = html_code.replace('{{ item_list_box }}', list_box_item_thml)

            self.text_box_html.setHtml(html_code)

    def seltct_item_list_box(self) -> None:
        item_data = self.list_box.currentIndex().data()
        page_name = self.dict_list_box_item.get(item_data) 
        if page_name:
            self.update_html(page_name)

    def on_anchor_clicked(self, url: str) -> None:
        page_name = url.toString()
        self.update_html(page_name)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = WindowHelper()
    window.show()
    sys.exit(app.exec_())