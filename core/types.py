from pathlib import Path
from typing import NamedTuple


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
