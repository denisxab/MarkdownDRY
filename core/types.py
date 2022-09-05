from enum import Enum
from typing import NamedTuple

from logsmal import logger

from core.helpful import ptabel


class HeaderType(Enum):
    """
    Доступные типы заголовков
    """
    # Стандартный заголовок
    Standard = 0
    # Не отображать заголовок в оглавление
    Hide = 1
    # Сколько максимально возможно заголовков
    MaxLvlHeader = 6


class ErrorBuildMDDRY(Exception):
    """
    Ошибка сборки MarkdownDRY
    """

    def __init__(self, text, reasons: tuple[str, ...], solutions: tuple[str, ...], ):
        """

        :param text: Текст ошибки
        :param reasons: Список возможных причин возникновения исключения
        :param solutions: Список возможных решения для исправления исключения
        """
        self.text = text
        self.solutions = solutions
        self.reasons = reasons

    def __str__(self):
        res = "ErrorBuildMDDRY: {text}\n{reasons}\n{solutions}".format(
            text=self.text,
            reasons=ptabel((('№', 'Возможные причины',), *[(i, x) for i, x in enumerate(self.reasons)],)),
            solutions=ptabel((('№', 'Возможные решения',), *[(i, x) for i, x in enumerate(self.solutions)],)),
        )
        logger.error(res)
        return res


class HeaderMain_ValueVar(NamedTuple):
    """
    Хранение значения переменной
    """
    # Значение переменной
    value: str
    # Текстовый тип переменной
    type: str


class HeaderMain_data_body(NamedTuple):
    """
    Что храниться в заголовке
    """
    # Уровень заголовка
    level: int
    # Тип заголовка, обычный или скрытый
    type_header: HeaderType
    # Переменны которые инициализированы в текущем заголовке
    vars: dict[str, HeaderMain_ValueVar]
    # Уникальный идентификатор заголовка, который строиться на основе имен вышестоящих заголовка, это нужно для того чтобы можно было указывать
    # одинаковые имена заголовков, в разных главах.
    uuid_header: str


class HeaderMain_Headers_With_Found_Variables(NamedTuple):
    """
    Заголовки с найденными переменными
    """
    # Структура заголовка
    name_head: str
    # Значение найденной переменной
    value: HeaderMain_data_body


class HeaderMain:
    """
    Структура для заголовков
    """
    # Заголовки - ИмяЗаголовка:(УровеньЗаголовка,ТипЗаголовка,{ИмяПеременной:(Значение,IdЗаголовка)},IdЗаголовка)
    date: dict[str, HeaderMain_data_body] = dict()


class ProceduralTemplatesTypeBody(NamedTuple):
    """
    Структура для хранения процедурных шаблонов
    """
    # Весь текст в процедуру(вместе с объявлением переменных)
    text_procedure: str
    # Объявленные переменные в процедуре
    vars: dict[str, str]

    def __str__(self):
        return str(self.__dict__)
