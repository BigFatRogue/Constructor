from PyQt5 import QtWidgets

   
class WarningQEditLine:
    def __init__(self, lineedit: QtWidgets.QLineEdit):
        self.lineedit = lineedit
        self.original_style_sheet = self.lineedit.styleSheet()
        self.original_mousePressEvent = self.lineedit.mousePressEvent
        
        self.lineedit.setStyleSheet(f'#{self.lineedit.objectName()} {{border: 1px solid red}}')
        self.lineedit.mousePressEvent = self.mouse_press_event        

    def mouse_press_event(self, event) -> None:
        self.lineedit.setStyleSheet(self.original_style_sheet)
        self.lineedit.mousePressEvent = self.original_mousePressEvent
