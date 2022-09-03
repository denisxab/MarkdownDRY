import typing
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from core.core_lang import Lange


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


class BaseCodeRefReturn(NamedTuple):
    """Структура данных для хранения ответа функции"""
    # Описание ссылки
    name_re: str
    # Текст целиком из файла
    text_in_file: str
    # Обрезанный текст, на который указывает ссылка
    text_in_file_cup: str
    # Начальный индекс найденного элемента
    line_start: int
    # Конечный индекс найденного элемента
    line_end: int
    # На какой элемент ссылка
    ref: str
    # Имя языка программирования или разметки
    lange_file: Lange
    # Путь к файлу или ссылка
    file: Path


class HeaderMain_ValueVar(typing.NamedTuple):
    """
    Хранение значения переменной
    """
    # Значение переменной
    value: str
    # Текстовый тип переменной
    type: str


class HeaderMain_data_body(typing.NamedTuple):
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


class HeaderMain_Headers_With_Found_Variables(typing.NamedTuple):
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
