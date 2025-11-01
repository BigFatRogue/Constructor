class RowCounter:
    def __init__(self, start=0):
        self.__value = 0
    
    def next(self) -> int:
        self.__value += 1
        return self.value
    
    def __call__(self) -> int:
        return self.next()
    
    @property
    def value(self) -> int:
        return self.__value