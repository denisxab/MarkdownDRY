import re
from abc import abstractstaticmethod, ABCMeta, abstractproperty
from enum import Enum


class Lange(metaclass=ABCMeta):
    """
    Шаблонная структура класса для языка программирования или языка разметки
    """
    ...

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
        def class_func_var(name: str, text: str) -> tuple[str, int, int]:
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
                            "(?P<var>{name}[\t ]*=.+)"

        # РегуляркаДляПоискаАтрибутов>
        class_meth_attr_re = '(?P<meth>(?P<count_meth>[\t ]+)def[ \t]+{name}[\t ]*\(.+:)|' \
                             '(?P<attr>(?P<count_attr>[\t ]+){name}.+)'

        # <РегуляркаДляПоискаАтрибутов

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
            return res

        @classmethod
        def class_func_var(cls, name: str, text: str) -> tuple[str, int, int]:
            # Ищем класс функцию переменю с указанным именем
            # Если есть одноименные функции или переменные или классы то берём последний найденных элемент
            res: tuple[str, int, int] = ('', 0, 0)
            for _m in re.finditer(cls.class_func_var_re.format(name=name), text):
                res = [x for x in (_m['class'], _m['func'], _m['var']) if x is not None][0], _m.start(), _m.end()
            return res


class AvailableLanguages(Enum):
    """
    Класс для хранения поддерживаемых языков программирования или языков разметки

    # Документация>
    ------------------------------------------------------------------
    | Как добавить новый язык                                        |
    |                                                                |
    | 1. Создать наследника класса `Lange` - Реализовать его методы  |
    | 2. Добавить в класс `AvailableLanguages`                       |
    | 3. Добавить в класс `ConvertSuffixToLange`                     |
    ------------------------------------------------------------------
    #<Документация
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
