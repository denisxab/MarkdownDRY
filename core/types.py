from typing import NamedTuple


class BaseCodeRefReturn(NamedTuple):
    """Структура данных для хранения ответа функции"""
    name_re: str
    text_in_file: str
    line_start: int
    line_end: int
    # На какой элемент ссылка
    ref: str
    file: str
