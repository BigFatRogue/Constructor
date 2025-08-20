from pathlib import Path


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


def strip_path(path: str) -> str:
    """
    Убирает пробелы перед и после слэшами
    """
    return str(Path(*[s.strip() for s in Path(path).parts]))


if __name__ == '__main__':
    c = RowCounter()

    print(c())
    print(c())
    print(c.value)