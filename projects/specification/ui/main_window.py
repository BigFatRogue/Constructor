import ctypes

from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.settings import *
from projects.specification.config.constants import *
from projects.specification.config.enums import EnumStatusBar

from projects.specification.ui.widgets.browser import WidgetBrowser, ProjectItem
from projects.specification.ui.widgets.content import WidgetContent


class WindowSpecification(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.path_project: str = None

        self.init_widnow()
        self.init_menubar()
        self.init_widgets()
        self.init_status_bar()

        self.widget_browser.load_project(r'D:\Python\AlfaServis\Constructor\_pp_data.scdata')
    
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
        self.widget_browser = WidgetBrowser(self)
        self.widget_browser.signal_status.connect(self.set_status)
        self.widget_browser.setObjectName('browser')
        self.widget_browser.signal_select_item.connect(self.select_item)
        self.widget_browser.signal_open_project.connect(self.open_project)
        
        self.widget_content = WidgetContent(self)
        self.widget_content.signal_status.connect(self.set_status)
        self.widget_content.page_property_projcet.signal_save_project.connect(self.save_project)
        self.widget_browser.signal_del_item.connect(self.widget_content.view_empty_page)
    
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.widget_browser)
        splitter.addWidget(self.widget_content)
        splitter.setStretchFactor(1, 1)
        self.grid_layout.addWidget(splitter, 0, 0, 1, 1)

    def init_status_bar(self) -> None:
        statusBar = QtWidgets.QStatusBar(self)
        statusBar.layout().setContentsMargins(2, 2, 2, 2)
        statusBar.setStyleSheet('QStatusBar {border-top: 1px solid gray}')
        self.setStatusBar(statusBar)
        statusBar.showMessage(EnumStatusBar.WAIT.value)

        self.timer_status = QtCore.QTimer(self)
        self.timer_status.setSingleShot(True)
        self.timer_status.timeout.connect(self.reset_status_bar)

    def select_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        self.widget_content.set_item(item)
        
    def save_project(self, item: ProjectItem) -> None:
        table_data = item.table_data
        if not item.is_init:
            table_data.create_sql()
            table_data.insert_sql()
            item.is_init = True
            item.table_data.commit_sql()
            self.widget_browser.create_main_item_project(item)
        else:
            table_data.update_sql()
            table_data.commit_sql()
        item.is_save = True
        
    def open_project(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getOpenFileName(self, 'Выбрать файл', filter=f'SPEC файл (*.{MY_FROMAT})')
        if filename and filename[0]:
            filepath, _ = filename
            filename = os.path.basename(filepath)
            self.widget_browser.load_project(filepath)
    
    def set_status(self, text: str, timeout=3000) -> None:
        self.timer_status.stop()
        self.statusBar().showMessage(text)
        self.timer_status.start(timeout)

    def reset_status_bar(self) -> None:
        self.statusBar().showMessage(EnumStatusBar.WAIT.value) 

    def closeEvent(self, event):
        # for db in self.databases.values():
        #     db.close()

        return super().closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = WindowSpecification()
    
    window.show()
    sys.exit(app.exec_())