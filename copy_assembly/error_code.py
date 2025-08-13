from enum import Enum, auto


class ErrorCode(Enum):
    SUCCESS = (0, 'Успешное выполнение', None)
    OPEN_INVENTOR_PROJECT = (1, 'Ошибка открытия проекта', 'Закройте все активные документы или перезапустите приложение')
    OPEN_INVENTOR_APPLICATION = (2, 'Ошибка открытия приложения Inventor', None)
    CONNECT_INVENTOR_APPLICATION = (3, 'Ошибка подключения к экземпляру Inventor', None)
    EMPTY_FIELD = (4, 'Данное поле не может быть пустым', None)
    READ_ASSEMBLY = (5, 'Ошибка чтения сборки', None)

    def __init__(self, code, message, description):
        self.code = code
        self.message = message
        self.description = description
    
    def __str__(self):
        return f'{self.code}::{self.message}\n{self.description}'




if __name__ == '__main__':
    print(ErrorCode.OPEN_INVENTOR_APPLICATION)