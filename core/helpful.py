import os.path
import re

from logsmal import logger
from prettytable import PrettyTable, ALL


def ptabel(data: tuple[tuple[str, ...], ...], align="l", junction_char='+', hrules=ALL) -> str:
    """
    :param data: [ [Столбец_1_Строка_1,Столбец_1_Строка_N], [Столбец_2_Строка_1,[Столбец_2_Строка_N]] ]
    :param align: Выравнивание
    :param junction_char: Строка из одного символа, используемая для рисования соединений линий. По умолчанию +.
    :param hrules:  Управляет печатью горизонтальных линеек после строк. Допустимые значения: FRAME, HEADER, ALL, NONE- обратите
    внимание, что это переменные, определенные внутри prettytable модуль, поэтому убедитесь, что вы импортируете их или используете
     prettytable.FRAME
    :return:
    """
    x = PrettyTable(data[0])
    x.add_rows(data[1:])
    x.align = align
    x.junction_char = junction_char
    x.hrules = hrules
    return x.__str__()


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


def StrFormat(text: str):
    """
    Красиво отформатировать многострочный текст
    """
    # 1. Убрать перенос строк в начале и в конце текста
    # 2. Убрать табуляции в начале сроки
    return re.sub('\n([\t ]+)', '\n', text.strip())
