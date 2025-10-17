from PyQt5 import QtCore, QtWidgets, QtGui


class WidgetHelperInterective(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.resize(parent.size())

        self.list_widgets: list[QtWidgets.QWidget] = []
        self.dict_rect_widgets: dict[QtWidgets.QWidget, tuple[int]] = {}
        self.highlight_rect = QtCore.QRectF()
        self.disabled_widgets = []
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.initWidgets()

    def initWidgets(self) -> None:
        ...
    
    def add_widget(self, widget: QtWidgets.QWidget) -> None:
        widget.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.list_widgets.append(widget)

    def highlight_widgets(self) -> None:
        x0 = y0 = x1 = y1 = 0
        for widget in self.list_widgets:
            # widget.raise_()
            x0_widget, y0_widget = widget.mapTo(self.parent(), QtCore.QPoint(0, 0)).x(), widget.mapTo(self.parent(), QtCore.QPoint(0, 0)).y()
            width, heigth = widget.size().width(), widget.size().height()
            x1_widget, y1_widget = x0_widget + width, y0_widget + heigth
            
            self.dict_rect_widgets[widget] = (x0_widget, y0_widget, width, heigth)
            
            if x0 == y0 == x1 == y1 == 0:
                x0, y0, x1, y1 =  x0_widget, y0_widget, x1_widget, y1_widget
            else:
                if x0_widget < x0:
                    x0 = x0_widget
                if y0_widget < y0:
                    y0 = y0_widget
                if x1_widget > x1:
                    x1 = x1_widget
                if y1_widget > y1:
                    y1 = y1_widget

        point = QtCore.QPoint()
        point.setX(x0 - 5)
        point.setY(y0 - 5)
        
        size_f = QtCore.QSizeF()
        size_f.setWidth(abs(x1 - x0) + 10)
        size_f.setHeight(abs(y1 - y0) + 10)
        
        self.highlight_rect = QtCore.QRectF(point, size_f)
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        path = QtGui.QPainterPath()
        path.addRect(QtCore.QRectF(self.rect()))
        # self.highlight_widgets()
        path.addRoundedRect(self.highlight_rect, 5, 5)
       
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(0, 0, 0, 180)))
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 50, 50), 2))
        
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        painter.end()

    def show_message(self) -> None:
        ...
    
    def next_step(self) -> None:
        self.list_widgets.clear()

    def prev_step(self) -> None:
        self.list_widgets.clear()
    
    def end(self) -> None:
        self.list_widgets.clear()
    
    def resizeEvent(self, event):
        self.highlight_widgets()
        return super().resizeEvent(event)