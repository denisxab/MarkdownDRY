import typing
from enum import Enum
from pathlib import Path
from typing import NamedTuple


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
    # Текст целиком
    text_in_file: str
    # Обрезанный текст
    text_in_file_cup: str
    # Старт найденного элемента
    line_start: int
    # Конец найденного элемента
    line_end: int
    # На какой элемент ссылка
    ref: str
    # Путь к файлу или ссылка
    file: Path


class HeaderMain_data_vars(typing.NamedTuple):
    items: str
    type: str


class HeaderMain_data_body(typing.NamedTuple):
    level: int
    type_header: HeaderType
    vars: dict[str, HeaderMain_data_vars]
    uuid_header: str


class HeaderMain:
    """
    Структура для заголовков
    """

    # data_body = tuple[int, HeaderType, dict[str, tuple[str, str]], str]
    data_type = dict[str, HeaderMain_data_body]
    # Заголовки - ИмяЗаголовка:(УровеньЗаголовка,ТипЗаголовка,{ИмяПеременной:(Значение,IdЗаголовка)},IdЗаголовка)
    date: data_type = dict()
