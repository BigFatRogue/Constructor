from __future__ import annotations
import os
import ctypes
from PyQt5 import QtCore, QtWidgets, QtGui

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context.app_context import app_context
SETTING = app_context.context_setting
SIGNAL_BUS = app_context.single_bus
ENUMS = app_context.context_enums
CONSTANTS = app_context.constants

from projects.specification.ui.widgets.control_panel_application import ControlPanelAppliction
from projects.specification.ui.widgets.browser_widget import BrowserWidget
from projects.specification.ui.widgets.content_widget.content_widget import ContentWidget


class WindowSpecification(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.path_project: str = None

        self.init_widnow()
        self.init_menubar()
        self.init_widgets()
        self.init_status_bar()

        self.browser_widget.open_project(r'C:\Users\p.golubev\Desktop\python\AfaLServis\Constructor\ALS.1648.8.2.01.scdata')
    
    def init_widnow(self) -> None:
        myappid = 'mycompany.myproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QtGui.QIcon(os.path.join(SETTING.ICO_FOLDER, 'Specification.png')))

        with open(os.path.join(SETTING.RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', SETTING.ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        self.resize(1000, 400)
        self.setWindowTitle('КО спецификация')

        self.central_widget = QtWidgets.QWidget(self)
        self.central_widget.setObjectName("central_widget")

        self.grid_layout = QtWidgets.QGridLayout(self.central_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)

        self.setCentralWidget(self.central_widget)

    def init_menubar(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu('&Файл')

        open_action = QtWidgets.QAction('&Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

    def init_widgets(self) -> None:
        self.control_panel: ControlPanelAppliction = ControlPanelAppliction(self)
        SIGNAL_BUS.save.connect(self.save)
        self.grid_layout.addWidget(self.control_panel, 0, 0, 1, 1)

        self.browser_widget = BrowserWidget(self)
        self.browser_widget.setObjectName('browser')
        SIGNAL_BUS.satus_bar.connect(self.set_status)
        SIGNAL_BUS.open_project.connect(self.open_project)
        
        self.content_widget = ContentWidget(self)
        SIGNAL_BUS.delele_item.connect(self.content_widget.view_empty_page)
        SIGNAL_BUS.satus_bar.connect(self.set_status)
        
    
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.browser_widget)
        self.splitter.addWidget(self.content_widget)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStyleSheet("""
        QSplitter::handle {background-color: #d0d0d0}
        QSplitter::handle:pressed {background-color: #4060ff;}""")
        self.grid_layout.addWidget(self.splitter, 1, 0, 1, 1)

    def init_status_bar(self) -> None:
        statusBar = QtWidgets.QStatusBar(self)
        statusBar.layout().setContentsMargins(2, 2, 2, 2)
        statusBar.setStyleSheet('QStatusBar {border-top: 1px solid gray}')
        self.setStatusBar(statusBar)
        statusBar.showMessage(ENUMS.STATUS_BAR.WAIT.value)

        self.timer_status = QtCore.QTimer(self)
        self.timer_status.setSingleShot(True)
        self.timer_status.timeout.connect(self.reset_status_bar)

    def save(self) -> None:
        self.content_widget.save()
        self.browser_widget.save()
    
    def open_project(self) -> None:
        dlg = QtWidgets.QFileDialog(self)
        filename = dlg.getOpenFileName(self, 'Выбрать файл', filter=f'SPEC файл (*.{CONSTANTS.MY_FORMAT})')
        if filename and filename[0]:
            filepath, _ = filename
            filename = os.path.basename(filepath)
            self.browser_widget.open_project(filepath)
    
    def set_status(self, text: str, timeout=3000) -> None:
        self.timer_status.stop()
        self.statusBar().showMessage(text)
        self.timer_status.start(timeout)

    def reset_status_bar(self) -> None:
        self.statusBar().showMessage(ENUMS.STATUS_BAR.WAIT.value) 


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = WindowSpecification()
    
    window.show()
    sys.exit(app.exec_())