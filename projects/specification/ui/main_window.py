import sys
import ctypes

from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.settings import *
from projects.specification.core.database import DataBase

from projects.specification.ui.widgets.browser import WidgetBrowser
from projects.specification.ui.widgets.content import WidgetContent


class WindowSpecification(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.databases: dict[str, DataBase] = {}
        self.path_project: str = None

        self.init_widnow()
        self.init_menubar()
        self.init_widgets()

    def init_widnow(self) -> None:
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ICO_FOLDER, 'Specification.png')))

        with open(os.path.join(RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        self.resize(1000, 400)
        self.setWindowTitle('КО спецификация')

        self.central_widget = QtWidgets.QWidget(self)
        self.central_widget.setObjectName("central_widget")

        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.grid_layout.setContentsMargins(2, 2, 2, 2)
        self.grid_layout.setSpacing(2)

        self.setCentralWidget(self.central_widget)

    def init_menubar(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu('&Файл')

        open_action = QtWidgets.QAction('&Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

    def init_widgets(self) -> None:
        self.browser = WidgetBrowser(self)
        self.browser.setObjectName('browser')
        self.browser.signal_select_item.connect(self.select_item)
        
        self.widget_content = WidgetContent(self)
        # self.widget_content.signal_click_btn.connect(self.load_content)
        self.browser.signal_del_item.connect(self.widget_content.view_empty_page)
    
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.browser)
        splitter.addWidget(self.widget_content)
        splitter.setStretchFactor(1, 1)
        self.grid_layout.addWidget(splitter, 0, 0, 1, 1)

    def select_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        self.widget_content.set_item(item)
        
    def create_project(self) -> None:
        ...

    def open_project(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getOpenFileName(self, 'Выбрать файл', filter='SPEC файл (*.spec)')
        if filename[0]:
            self.path_project = filename[0]
            self.browser.populate_from_db()

    def closeEvent(self, event):
        for db in self.databases.values():
            db.close()

        return super().closeEvent(event)


