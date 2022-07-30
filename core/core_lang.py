import re
from abc import abstractstaticmethod, ABCMeta, abstractproperty
from enum import Enum
from typing import Optional

from logsmal import logger

from core import core_markdown_dry


class Lange(metaclass=ABCMeta):
    """
    Шаблонная структура класса для языка программирования или языка разметки
    """

    class REGEX(metaclass=ABCMeta):
        """
        Регулярные выражения
        """

        @abstractproperty
        def class_func_var_re(self):
            ...

        @abstractproperty
        def class_meth_attr_re(self):
            ...

        @abstractstaticmethod
        def class_meth_attr(name: str, text: str) -> tuple[str, int, int]:
            """
            Поиск метода/атрибута в коде

            :param name:
            :param text:
            :return: (НайденныйТекст, началоТекста, КонецТекста)
            """
            ...

        @abstractstaticmethod
        def class_func_var_anchor(name: str, text: str) -> tuple[str, int, int]:
            """
            Поиск класс/функции/переменной в коде

            :param name:
            :param text:
            :return: (НайденныйТекст, началоТекста, КонецТекста)
            """
            ...


class Python(Lange):
    """
    Python
    """

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
                    re_math = f"(?P<meth>((?P<count>[\t ]+)def[ \t]+{name}[\t ]*)\((.+):\n(?:(?:\t| {{{len(_m['count_meth']) * 2},}}).*\n+)+)"
                    tmp = re.search(re_math, text[_m.start():])
                    res = tmp.group(0), _m.start(), _m.start() + tmp.end()
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
                res = [x for x in (_m['class'], _m['func'], _m['var']) if x is not None][0], _m.start(), _m.end()
                if _m['class']:
                    logger.debug(res, 'Класс')
                elif _m['func']:
                    logger.debug(res, 'Функция')
                elif _m['var']:
                    logger.debug(res, 'Переменная')

            if not res:
                # Если класс/функцию/переменю с указанным именем не удалось найти, то тогда ищем якорь с таким именем, если он найдется,
                # то берем код из якоря
                for _m2 in re.finditer(core_markdown_dry.REGEX.AnchorFromCode.format(name=name), text):
                    res = _m2.group(), _m2.start(), _m2.end()
                    logger.debug(res, 'Якорь')

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
    | 2. Добавить в класс `AvailableLanguages`                       |
    | 3. Добавить в класс `ConvertSuffixToLange`                     |
    ------------------------------------------------------------------
    """
    Python = Python


class ConvertSuffixToLange:
    """
    Класс для перевода расширения файла в стандартное имя языка программирования или языка разметки
    """

    __store = {
        '.py': AvailableLanguages.Python
    }

    @classmethod
    def getlange(cls, suffix: str) -> Lange:
        return cls.__store[suffix].value
