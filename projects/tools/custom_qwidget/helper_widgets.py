import sys
import os
from collections import OrderedDict
from PyQt5 import QtCore, QtWidgets, QtGui
import re

ROOT = os.path.dirname(__file__)


class WindowHelper(QtWidgets.QWidget):
    def __init__(self, parent, path_resources: str):
        super().__init__(parent, QtCore.Qt.Window)
        self.path_html_page = os.path.join(path_resources, 'html')
        self.first_page = None
        self.dict_list_box_item = self.get_html_page()
        
        self.dict_html_template = {
            'ITEM_LIST_BOX': '\n'.join([f'<li><a href={page}>{name}</a></li>' for name, page in self.dict_list_box_item.items()]),
            'PATH_RESOURCES': path_resources
        }

        self.setWindowTitle('Помощь')
        self.init_widgets()
        self.update_html()

    def init_widgets(self) -> None:
        self.resize(900, 400)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 5, 5, 5)
        self.v_layout.setSpacing(5)

        self.list_box = QtWidgets.QListWidget(self)
        
        for (item_name, _) in self.dict_list_box_item.items():
            self.list_box.addItem(item_name)
        self.list_box.clicked.connect(self.seltct_item_list_box)

        self.text_box_html = QtWidgets.QTextBrowser(self)
        self.text_box_html.zoomIn(3)
        self.text_box_html.setReadOnly(True)
        self.text_box_html.anchorClicked.connect(self.on_anchor_clicked)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.list_box)
        splitter.addWidget(self.text_box_html)
        splitter.setStretchFactor(1, 1)
        self.v_layout.addWidget(splitter)
    
    def get_html_page(self) -> OrderedDict:
        ordere_dict = OrderedDict()
        list_page = [file for file in os.listdir(self.path_html_page) if os.path.splitext(file)[1] == '.html']
        list_page.sort(key=lambda v: os.path.basename(v).split('_')[0])
        for file in list_page:
            with open(os.path.join(self.path_html_page, file), 'r', encoding='utf-8') as html:
                document_name = re.findall('<title>(.+?)<\/title>', html.read())
                if document_name:
                    if self.first_page is None:
                        self.first_page = file
                    ordere_dict[document_name[0]] = file
        return ordere_dict

    def update_html(self, filename: str=None) -> None:
        if filename is None:
            filename = self.first_page
        with open(os.path.join(self.path_html_page, filename), 'r', encoding='utf-8') as html_file:
            html_code = html_file.read()

            for temp in re.findall(r'{{ (.+) }}', html_code):
                html_code = html_code.replace('{{ ' + temp + ' }}', self.dict_html_template.get(temp))
        
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

    window = WindowHelper(parent=None, path_resources=r'd:\Python\AlfaServis\Constructor\projects\copy_assembly\resources', )
    window.show()
    sys.exit(app.exec_())