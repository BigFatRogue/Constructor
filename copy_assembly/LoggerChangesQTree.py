from PyQt5 import QtGui
from enum import Enum ,auto


class TypeItemQTree(Enum):
    text = auto()
    rules = auto()


class ItemChangeLoggerQTree:
    def __init__(self, item: QtGui.QStandardItem, old_value: str, new_value: str, type_item: TypeItemQTree):
        self.item = item
        self.old_value = old_value
        self.new_value = new_value
        self.type = type_item
    
    def __str__(self):
        return f'({self.item}, {self.old_value}, {self.new_value}, {self.type})'

    def __repr__(self):
        return self.__str__()


class LoggerChangesQTree:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance   

    def __init__(self):
        self.list_undo: list[list[ItemChangeLoggerQTree]] = []
        self.list_redo: list[list[ItemChangeLoggerQTree]] = []
        self.is_start_transaction = False
        self.has_add_change = True

    def start_transaction(self) -> None:
        self.is_start_transaction = True

    def end_transaction(self) -> None:
        self.is_start_transaction = False

    def add_change(self, item: QtGui.QStandardItem, old_value: str, new_value: str, type_item: TypeItemQTree=TypeItemQTree.text):
        if self.has_add_change:
            if not self.is_start_transaction or not self.list_undo:
                self.list_undo.append([])
            if self.list_redo:
                self.list_redo.clear()
            self.list_undo[-1].append(ItemChangeLoggerQTree(item, old_value, new_value, type_item))
    
    def undo(self) -> None:
        self.has_add_change = False
        if self.list_undo:
            last_item = self.list_undo.pop()
            self.list_redo.append(last_item)
            for item in last_item:
                item: ItemChangeLoggerQTree
                if item.type == TypeItemQTree.text:
                    item.item.setText(item.old_value)
                if item.type == TypeItemQTree.rules:
                    item.item.rules = item.old_value
        self.has_add_change = True
            
    def redo(self) -> None:
        self.has_add_change = False
        if self.list_redo:
            last_item = self.list_redo.pop()
            self.list_undo.append(last_item)
            for item in last_item:
                item: ItemChangeLoggerQTree
                if item.type == TypeItemQTree.text:
                    item.item.setText(item.new_value)
                if item.type == TypeItemQTree.rules:
                    item.item.rules = item.new_value
        self.has_add_change = True

        
if __name__ == '__main__':
    logger = LoggerChangesQTree()

    list_item = [(f'item_{i}', f'old_text_{i}', f'old_text_{i}', TypeItemQTree.text) for i in range(3)]
    
    logger.start_transaction()
    for item in list_item:
        logger.add_change(*item)
    logger.end_transaction()

    for item in list_item:
        logger.add_change(*item)
    
    logger.undo()
    logger.undo()
    logger.redo()

    
    # logger.current_index = 1
    # logger.start_transaction()
    # for item in list_item:
    #     logger.add_change(*item)
    # logger.end_transaction()

    for i, it in enumerate(logger.list_undo):
        print(i, it)