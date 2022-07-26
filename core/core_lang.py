import re
from abc import abstractstaticmethod, ABCMeta, abstractproperty
from enum import Enum
from pathlib import Path
from typing import Optional, NamedTuple

from logsmal import logger

from core.RegexStorage import REGEX


class Lange:
    """
    Шаблонная структура класса для языка программирования или языка разметки
    """

    @abstractproperty
    def name_lange(self):
        """Имя языка для код блока в Markdown"""
        ...

    class REGEX(metaclass=ABCMeta):
        """
        Регулярные выражения, для поиска элемента в конкретном языке программирования или разметки
        """

        @abstractproperty
        def class_func_var_re(self):
            """Регулярное выражение для поиска класс/функции/переменной в коде"""
            ...

        @abstractproperty
        def class_meth_attr_re(self):
            """Регулярное выражение для поиска метода/атрибута в коде"""
            ...

        @abstractstaticmethod
        def class_meth_attr(name: str, text: str) -> tuple[str, int, int]:
            """
            Логика поиск метода/атрибута в коде

            :param name:
            :param text:
            :return: (НайденныйТекст, началоТекста, КонецТекста)
            """
            return text, 0, 0

        @abstractstaticmethod
        def class_func_var_anchor(name: str, text: str) -> tuple[str, int, int]:
            """
            Поиск класс/функции/переменной в коде

            Если не определен, то вызовет метод для поиска `УникальногоЯкоря`

            :param name:
            :param text:
            :return: (НайденныйТекст, началоТекста, КонецТекста)
            """
            return Lange.anchor(name, text)

    @staticmethod
    def anchor(name: str, text: str) -> Optional[tuple[str, int, int]]:
        """
        Поиск уникального якоря
        :param name:
        :param text:
        :return: (НайденныйТекст, началоТекста, КонецТекста)
        """
        res = None
        for _m2 in re.finditer(REGEX.AnchorFromCode.format(name=name), text):
            # Находим лишние переносы строк в конце текст
            _text = _m2.group(0)
            _index_end = 0
            # Если есть лишние переносы строк в конце, то удаляем их
            if re.search('\s+$', _m2.group()[:-1]):
                for _i in range(len(_text) - 1, 0, -1):
                    if _text[_i] == '\n':
                        _index_end = _i
                        break
                _index_end = len(_text) - _index_end
            end: int = _m2.end() - _index_end
            # Формируем ответ
            res = _m2.group(), _m2.start(), end
            logger.debug(res, 'Якорь')
        return res


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


class Python(Lange):
    """
    Python
    """

    name_lange = 'py'

    class REGEX(Lange.REGEX):
        class_func_var_re = "(?P<class>(class[\t ]+{name}[\t ]*)(?:\((.+)\))?:\n(?:\t+| {{1,4}}.*\n+)+)|" \
                            "(?P<func>(def[\t ]+{name}[\t ]*)\((.+):\n(?:(?:\t+| {{1,4}}).*\n+)+)|" \
                            "(?:\A|\n)\s*(?P<var>{name}[\t ]*=.+)"

        class_meth_attr_re = '(?P<meth>(?P<count_meth>[\t ]+)def[ \t]+{name}[\t ]*\(.+:)|' \
                             '(?P<attr>(?P<count_attr>[\t ]+){name}.+)'

        @classmethod
        def class_meth_attr(cls, name: str, text: str) -> tuple[str, int, int]:
            # Ищем методы в тексте, также получаем отступы у этих методов, берем последний отступ и последний метод,
            # Если нет отступов для метода то проверяем наличие атрибута с таким именем
            # Если нет ни метода ни атрибута то возвращаем пустую ст уроку и нули
            res: tuple[str, int, int] = ('', 0, 0)
            for _m in re.finditer(cls.class_meth_attr_re.format(name=name), text):
                if _m['count_meth']:
                    # Регулярное выражение для поиска метода класса
                    re_math = f"(?P<meth>((?P<count>[\t ]+)def[ \t]+{name}[\t ]*)\((.+):\n(?:(?:\t| {{{len(_m['count_meth']) * 2},}}).*\n+)+)"
                    # Ищем метод класса с начала найденного класса
                    tmp = re.search(re_math, text[_m.start():])
                    # Получаем лишние переносы строк в конце текста
                    end_next_line: Optional[re.Match] = re.search('\n+$', tmp.group(0))
                    # Вычитаем лишние переносы строк в конце текста
                    end: int = tmp.end() - (end_next_line.group(0).__len__() if end_next_line else 0)
                    # Формируем результат
                    res = tmp.group(0), _m.start(), _m.start() + end
                elif _m['attr']:
                    res = _m['attr'], _m.start(), _m.end()
            if res == ('', 0, 0):
                logger.debug(name, 'Пусто')
            return res

        @classmethod
        def class_func_var_anchor(cls, name: str, text: str) -> tuple[str, int, int]:
            # Ищем класс/функцию/переменю с указанным именем
            # Если есть одноименные функции или переменные или классы, то берём последний найденных элемент.
            res: Optional[tuple[str, int, int]] = None
            for _m in re.finditer(cls.class_func_var_re.format(name=name), text):
                # Вычитаем лишние переносы строк в начале текста
                start_next_line: Optional[re.Match] = re.search('^\n+', _m.group(0))
                start: int = _m.start() + (start_next_line.group(0).__len__() if start_next_line else 0)
                # Вычитаем лишние переносы строк в конце текста
                end_next_line: Optional[re.Match] = re.search('\n+$', _m.group(0))
                end: int = _m.end() - (end_next_line.group(0).__len__() if end_next_line else 0)
                # Формируем результат
                res = [x for x in (_m['class'], _m['func'], _m['var']) if x is not None][0], start, end
                if _m['class']:
                    logger.debug(res, 'Класс')
                elif _m['func']:
                    logger.debug(res, 'Функция')
                elif _m['var']:
                    logger.debug(res, 'Переменная')
            if not res:
                # Если класс/функцию/переменю с указанным именем не удалось найти, то тогда ищем якорь с таким именем, если он найдется,
                # то берем код из якоря
                res = Lange.anchor(name, text)
            if not res:
                # Если ничего не найдено
                logger.debug(name, 'Пусто')
                res = ('', 0, 0)
            return res


class AvailableLanguages(Enum):
    """
    Класс для хранения поддерживаемых языков программирования или языков разметки

    ------------------------------------------------------------------
    | Как добавить новый язык                                        |
    |                                                                |
    | 1. Создать наследника класса `Lange` - Реализовать его методы  |
    | 2. Добавить наследника в класс `AvailableLanguages`            |
    | 3. Добавить наследника в класс `ConvertSuffixToLange.__store`  |
    ------------------------------------------------------------------
    """
    # Неопределенный тип файла
    NoneType = Lange
    # Бинарный тип файла, эти типы файлов будут исключены из обработки `InsertCodeFromFile`, `LinkCode`
    Binary: re.Pattern = re.compile(
        ".+(?={0})".format(
            "".join(f"{x}|" for x in (
                "jpg", "png", "gif", "bmp", "tiff", "psd", "mp4", "mkv", "avi", "mov", "mpg", "vob", "mp3", "aac", "wav", "flac",
                "ogg", "mka", "wma", "pdf", "doc", "xls", "ppt", "docx", "odt", "zip", "rar", "7z", "tar", "iso", "mdb", "accde",
                "frm", "sqlite", "exe", "dll", "so", "jpeg", 'svg'
                # Можете добавлять сюда дополнительные расширения файлов
            ))[:-1]
        )
    )

    # Определённые языки программирования
    Python = Python


class ConvertSuffixToLange:
    """
    Класс для перевода расширения файла в стандартное имя языка программирования или языка разметки
    """

    _store = {
        '.py': AvailableLanguages.Python
    }

    @classmethod
    def getlang(cls, suffix: str) -> Lange:
        """
        Получить объект на основе расширения файла, если расширение файла не поддерживается или оно не указано то тогда
        будет поддержка только `УникальногоЯкоря`
        """
        res = cls._store.get(suffix, AvailableLanguages.NoneType.value)
        if res == AvailableLanguages.NoneType.value:
            # Если это не поддерживаемый тип, то указываем имя языка таким же как и расширение файла, только без символов точки
            res.name_lange = suffix.replace('.', '')
        return res
