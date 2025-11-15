import os
from PyQt5 import QtCore, QtWidgets, QtGui

from projects.specification.config.settings import *
from projects.specification.config.enums import TypeTreeItem
from projects.specification.config.constants import *

from projects.tools.functions.decorater_qt_object import decorater_set_hand_cursor_button
from projects.tools.custom_qwidget.messege_box_question import MessegeBoxQuestion


class RightIconDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        super().paint(painter, option, index)
        
        status = index.model().itemData(index).get(QROLE_STATUS_TREE_ITEM)

        if status is not None and not status:
            rect = option.rect
            r = 6
            painter.setBrush(QtGui.QBrush(QtGui.QColor(60, 60, 230)))
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
            painter.drawEllipse(rect.right() - 15, rect.top() + (rect.height() - r) // 2, r, r)
        

@decorater_set_hand_cursor_button([QtWidgets.QPushButton])
class WidgetBrowser(QtWidgets.QWidget):
    signal_select_item = QtCore.pyqtSignal(QtWidgets.QTreeWidgetItem)
    signal_del_item = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.init_widgets()

    def init_widgets(self) -> None:
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)

        self.setLayout(self.grid_layout)
        
        # --------------------------------- Frame Panel ---------------------------------------------- 
        self.frame_panel = QtWidgets.QFrame(self)
        self.h_layout_frame_panel = QtWidgets.QHBoxLayout(self.frame_panel)
        self.h_layout_frame_panel.setContentsMargins(2, 2, 2, 2)
        self.h_layout_frame_panel.setSpacing(2)
        self.frame_panel.setLayout(self.h_layout_frame_panel)
        self.grid_layout.addWidget(self.frame_panel, 0, 0, 1, 1)

        self.btn_add_project = QtWidgets.QPushButton(self.frame_panel)
        self.btn_add_project.setToolTip('Добавить новый проект')
        self.btn_add_project.setObjectName('btn_add_project')
        self.btn_add_project.setFixedSize(20, 20)
        self.btn_add_project.setStyleSheet('#btn_add_project {border: none;} #btn_add_project:hover {background-color: rgb(209, 235, 255); border: 1px solid #0078d4;}')
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'green_plus.png'))
        self.btn_add_project.setIcon(icon)
        self.btn_add_project.clicked.connect(self.create_project)
        self.h_layout_frame_panel.addWidget(self.btn_add_project)

        self.btn_del_project = QtWidgets.QPushButton(self.frame_panel)
        self.btn_del_project.setToolTip('Удалить проект из списка')
        self.btn_del_project.setObjectName('btn_del_project')
        self.btn_del_project.setStyleSheet('#btn_del_project {border: none;} #btn_del_project:hover {background-color: rgb(209, 235, 255); border: 1px solid #0078d4;}')
        self.btn_del_project.setFixedSize(20, 20)
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'red_minus.png'))
        self.btn_del_project.setIcon(icon)
        self.btn_del_project.clicked.connect(self.del_project)
        self.h_layout_frame_panel.addWidget(self.btn_del_project)

        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setPlaceholderText('Поиск')
        self.h_layout_frame_panel.addWidget(self.line_edit)

        # --------------------------------- Tree ---------------------------------------------- 
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setItemDelegate(RightIconDelegate(self))
        self.tree.setHeaderLabel('Проекты')
        self.tree.itemChanged.connect(self.change_tree_item)
        self.tree.itemPressed.connect(self.select_tree_item)
        self.grid_layout.addWidget(self.tree, 1, 0, 1, 1)
        self.create_project()

    def create_project(self) -> None:
        project_item = QtWidgets.QTreeWidgetItem()
        project_item.setText(0, 'Новый проект')
        project_item.setData(0, QROLE_TYPE_TREE_ITEM, TypeTreeItem.PROJET)
        project_item.setData(0, QROLE_PROJCET_NAME, project_item.text(0))
        project_item.setData(0, QROLE_STATUS_TREE_ITEM, True)
        project_item.setData(0, QROLE_DATA_TREE_ITEM, {})
        project_item.setFlags(project_item.flags() | QtCore.Qt.ItemIsEditable)
        self.tree.addTopLevelItem(project_item)
        project_item.setExpanded(True)
        
        spec_inv_item = QtWidgets.QTreeWidgetItem()
        spec_inv_item.setText(0, 'Спецификация из Inventor')
        spec_inv_item.setData(0, QROLE_TYPE_TREE_ITEM, TypeTreeItem.SPEC_FOLDER_INV)
        spec_inv_item.setData(0, QROLE_PROJCET_NAME, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'inventor.png'))
        spec_inv_item.setIcon(0, icon)
        project_item.addChild(spec_inv_item)

        spec_buy_item = QtWidgets.QTreeWidgetItem()
        spec_buy_item.setText(0, 'Закупочная спецификация')
        spec_buy_item.setData(0, QROLE_TYPE_TREE_ITEM, TypeTreeItem.SPEC_FOLDER_BUY)
        spec_buy_item.setData(0, QROLE_PROJCET_NAME, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'dollars.png'))
        spec_buy_item.setIcon(0, icon)
        project_item.addChild(spec_buy_item)

        spec_prod_item = QtWidgets.QTreeWidgetItem()
        spec_prod_item.setText(0, 'Сборочная спецификация')
        spec_prod_item.setData(0, QROLE_TYPE_TREE_ITEM, TypeTreeItem.SPEC_FOLDER_PROD)
        spec_prod_item.setData(0, QROLE_PROJCET_NAME, project_item.text(0))
        icon = QtGui.QIcon()
        icon.addFile(os.path.join(ICO_FOLDER, 'iam_image.png'))
        spec_prod_item.setIcon(0, icon)
        project_item.addChild(spec_prod_item)

        self.tree.setCurrentItem(project_item)

    def del_project(self) -> None:
        item = self.tree.currentItem()

        if item.data(0, QROLE_TYPE_TREE_ITEM) == TypeTreeItem.PROJET:
            msg = MessegeBoxQuestion(self,
                                 question=f'Удалить проект {item.text(0)}?',
                                 title='Удаление проекта')
            if msg.exec_():
                root = self.tree.invisibleRootItem()
                for item in self.tree.selectedItems():
                    (item.parent() or root).removeChild(item)
                self.signal_del_item.emit()

    def change_tree_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        if item.data(0, QROLE_TYPE_TREE_ITEM) == TypeTreeItem.PROJET:
            item.setData(0, QROLE_PROJCET_NAME, item.text(0))
            self.update_project_name(item, item.text(0))
                
    def update_project_name(self, parent: QtWidgets.QTreeWidgetItem, project_name) -> None:
        count = parent.childCount()
        if count > 0: 
            for i in range(count):
                child = parent.child(i)
                child.setData(0, QROLE_PROJCET_NAME, project_name)
                self.update_project_name(child, project_name)
        
    def select_tree_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        self.signal_select_item.emit(item)
    