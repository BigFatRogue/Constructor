import os
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.app_context import SETTING, DATACLASSES
from projects.specification.core.config_table import ColumnConfig, GENERAL_ITEM_CONFIG, INVENTOR_ITEM_CONFIG
from projects.specification.ui.widgets.table.tw_vhow import VerticallWithOverlayWidgets

class TitleViewLinkRow(QtWidgets.QFrame):
    signal_toggle_view = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)

        self.icon_hide: QtGui.QIcon = None
        self.icon_show: QtGui.QIcon = None
        self.is_visible = False

        self.setObjectName('TitleViewLinkRow')
        self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.setFixedHeight(20)

        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.h_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(5)
        
        self.btn_set_view = QtWidgets.QPushButton(self)
        self.btn_set_view.setObjectName('btn_set_view_link_content')
        self.btn_set_view.setFixedSize(20, 20)
        self.btn_set_view.setIconSize(QtCore.QSize(12, 12))
        self.btn_set_view.clicked.connect(self._toggle_btn)
        self._set_icon_show()
        self.h_layout.addWidget(self.btn_set_view)

        self.label_ico_link = QtWidgets.QLabel(self)
        self.label_ico_link.setFixedSize(20, 20)
        pixmap = QtGui.QPixmap(os.path.join(SETTING.ICO_FOLDER, 'link.png'))
        self.label_ico_link.setPixmap(pixmap.scaled(12, 12))
        self.h_layout.addWidget(self.label_ico_link)

        self.label = QtWidgets.QLabel(self)
        self.label.setText('Связь строки:')
        self.h_layout.addWidget(self.label)

    def populate(self, number_row: int) -> None:
        self.label.setText(f'Связь строки: <b>{number_row}</b>')

    def _toggle_btn(self) -> None:
        if self.is_visible:
            self._set_icon_show()
        else:
            self._set_icon_hide()
        self.signal_toggle_view.emit(self.is_visible)
        self.is_visible = not self.is_visible
        
    def _set_icon_hide(self) -> None:
        if self.icon_hide is None:
            self.icon_hide = QtGui.QIcon()
            self.icon_hide.addFile(os.path.join(SETTING.ICO_FOLDER, 'arrow_down_hide.png'))
        self.btn_set_view.setIcon(self.icon_hide)

    def _set_icon_show(self) -> None:
        if self.icon_show is None:
            self.icon_show = QtGui.QIcon()
            self.icon_show.addFile(os.path.join(SETTING.ICO_FOLDER, 'arrow_down_show.png'))
        self.btn_set_view.setIcon(self.icon_show)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        self._toggle_btn()
        return super().mousePressEvent(event)


class ModelTableLink(QtCore.QAbstractTableModel):
    def __init__(self, parent):
        super().__init__(parent)
        self._columns_config: list[ColumnConfig] = GENERAL_ITEM_CONFIG.columns + INVENTOR_ITEM_CONFIG.columns
        self._view_columns = [col for col in self._columns_config if col.is_view]
        self._index_column_view = self._set_index_column_view()
        self._data: list[list[DATACLASSES.DATA_CELL]] = []

    def _set_index_column_view(self) -> dict[int, int]:
        """
        Из указанного в QTableView адреса колонки преобразует в адрес колонки в _data 
        
        :return: Сслыка видимой колонки на колонку в _data
        :rtype: dict[int, int]
        """
        dct = {}
        view_x = 0
        for x, col in enumerate(self._columns_config):
            if col.is_view:
                dct[view_x] = x
                view_x += 1
        return dct

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data)
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._view_columns)
    
    def data(self, index: QtCore.QModelIndex, role=QtCore.Qt.ItemDataRole):
        if not index.isValid() and not self._data:
            return
        
        row = index.row()
        column = self._index_column_view[index.column()]

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self._data[row][column].value
    
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._view_columns[section].column_name
            elif orientation == QtCore.Qt.Orientation.Vertical:
                return str(section + 1)

    def populate(self, data: list[list[DATACLASSES.DATA_CELL]]) -> None:
        self._data = data
        self.layoutChanged.emit()
        print([(col.column_name, cell.value) for cell, col in zip(data[0], self._columns_config)])


class ContentViewLinkRow(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(5, 0, 0, 0)
        self.v_layout.setSpacing(0)

        self.table_view = QtWidgets.QTableView(self)
        self.v_layout.addWidget(self.table_view)
        self.table_model = ModelTableLink(self)
        self.table_view.setModel(self.table_model)

        self.btn_add_link = QtWidgets.QPushButton(self)
        self.btn_add_link.setText('Добавить связь')
        self.v_layout.addWidget(self.btn_add_link)

    def _stretch_columns_evenly(self):
        header = self.table_view.horizontalHeader()

        total_width = self.table_view.viewport().width()
        used_width = sum(header.sectionSize(i) for i in range(header.count()))
        extra = max(0, total_width - used_width)

        if header.count() == 0:
            return

        add = extra // header.count()

        for i in range(header.count()):
            header.resizeSection(i, header.sectionSize(i) + add)

    def populate(self, data: list[list[DATACLASSES.DATA_CELL]]) -> None:
        self.table_model.populate(data)
        
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.resizeColumnsToContents()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        self._stretch_columns_evenly()
        

class ViewLinkRow(QtWidgets.QWidget):
    signal_is_show = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)

        self.is_animating = False
        self.max_content_height = 150
        self.content_visible = False

        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)
        self.v_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.title = TitleViewLinkRow(self)
        self.title.signal_toggle_view.connect(self.toggle_content)
        self.title.signal_toggle_view.connect(self.signal_is_show)
        self.v_layout.addWidget(self.title)

        self.content = ContentViewLinkRow(self)
        self.content.hide()
        # self.content.setMaximumHeight(0)
        # self.content.setMinimumHeight(0)
        self.v_layout.addWidget(self.content)
        
        # self.animation = QtCore.QPropertyAnimation(self.content, b"maximumHeight")
        # self.animation.setDuration(300)
        # self.animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        # self.animation.finished.connect(self.on_animation_finished)
        
    def toggle_content(self, value) -> None:
        if value:
            self.content.hide()
        else:
            self.content.show()
    
    def populate(self, number_row: int, data: list[list[DATACLASSES.DATA_CELL]]=None) -> None:
        self.title.populate(number_row)
        if data is not None:
            self.content.populate(data)


    # def toggle_content(self, value) -> None:
    #     if self.is_animating:
    #         return
            
    #     self.is_animating = True
        
    #     if not value:
    #         self.content.show()
    #         self.animation.setStartValue(0)
    #         self.animation.setEndValue(self.max_content_height)
    #         self.content_visible = True
    #     else:
    #         self.animation.setStartValue(self.max_content_height)
    #         self.animation.setEndValue(0)
    #         self.content_visible = False
            
    #     self.animation.start()
        
    # def on_animation_finished(self):
    #     self.is_animating = False
    #     if not self.content_visible:
    #         self.content.hide()
    #     self.signal_resize.emit()
            
    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     if self.content_visible and not self.is_animating:
    #         self.content.setMaximumHeight(self.max_content_height)