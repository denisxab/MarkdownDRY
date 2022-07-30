import os.path

from logsmal import logger


class File:
    """
    Класс для работы с файлами
    """

    @staticmethod
    def read(path: str):
        if not os.path.exists(path):
            etext = f"Файл не существует: {path}"
            logger.error(etext, 'read')
            raise FileExistsError(etext)
        if not os.path.isfile(path):
            etext = f"Путь указывает не на файл: {path}"
            logger.error(etext, 'read')
            raise FileExistsError(etext)
        with open(path, 'r', encoding='utf-8') as _f:
            return _f.read()

    @staticmethod
    def wrire(path: str, text: str):
        with open(path, 'w', encoding='utf-8') as _f:
            return _f.write(text)
