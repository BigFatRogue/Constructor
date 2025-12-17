import os
from PyQt5 import QtCore, QtGui, QtWidgets

if __name__ == '__main__':
    import sys
    # Для запуска через IDE
    from pathlib import Path
    test_path = str(Path(__file__).parent.parent.parent.parent.parent.parent)
    sys.path.append(test_path)

from projects.specification.config.app_context.app_context import SETTING

from projects.specification.ui.widgets.table_widget.tw_data_table import DataTable
from projects.specification.ui.widgets.table_widget.new_table import Table

from projects.specification.core.data_tables import SpecificationDataItem, InventorSpecificationDataItem


class TableWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.v_layout = QtWidgets.QVBoxLayout(self)

        self.table = Table(self)
        self.v_layout.addWidget(self.table)
        
        self.current_data_table_model = None
    
    def set_item(self, item) -> None:
        self.current_data_table_model = item.data_table_model
        self.table.set_model(self.current_data_table_model)

    def tmp_set_item(self, table_data: SpecificationDataItem) -> None:
        table_data.data[1][2].color = (255, 255, 0)
        self.current_data_table_model = DataTable(self, table_data)
        self.table.set_model(self.current_data_table_model)
        self.table.set_edited(True)
        

class __Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        with open(os.path.join(SETTING.RESOURCES_PATH, r'spec_style.qss')) as style:
            text_style = style.read()
            text_style = text_style.replace('{{ICO_FOLDER}}', SETTING.ICO_FOLDER.replace('\\', '/')) 
            self.setStyleSheet(text_style)

        self.resize(750, 750)

        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.v_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.widgte_table = TableWidget(self)
        self.v_layout.addWidget(self.widgte_table)
        
        filepath = r'C:\Users\p.golubev\Desktop\python\AfaLServis\Constructor\projects\specification\DEBUG\ALS.1642.5.3.01Из инвентора.xlsx'
        data = get_specifitaction_inventor_from_xlsx(filepath)
        data_item = InventorSpecificationDataItem('')
        data_item.set_data(data)
        self.widgte_table.tmp_set_item(data_item)

        # control_panel = self.widgte_table.set_control_panel()
        # control_panel.add_block(FontStyleBlock)
        # control_panel.add_block(AlignCellBlock)
        # self.v_layout.addWidget(self.widgte_table)
        
        # table_data = InventorSpecificationDataItem(DataBase('a'))
        # filepath = r'D:\Python\AlfaServis\Constructor\projects\specification\DEBUG\ALS.1642.5.3.05.01.00.000 - Инвентор.xlsx'
        # table_data.set_data(get_specifitaction_inventor_from_xlsx(filepath))
        # self.widgte_table.populate(table_data)
                


if __name__ == '__main__':
    import sys
    from projects.specification.core.data_loader import get_specifitaction_inventor_from_xlsx
    app = QtWidgets.QApplication(sys.argv)
    window = __Window()
    
    window.show()
    sys.exit(app.exec_())
