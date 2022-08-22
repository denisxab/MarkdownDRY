import re
from base64 import b64encode
from decimal import Decimal
from enum import Enum
from hashlib import md5
from pathlib import Path
from typing import Optional, Literal

import requests
from logsmal import logger
from sympy import sympify, SympifyError

from core.core_html import HTML_CLASS, HTML_JS
from core.core_lang import Lange, ConvertSuffixToLange, AvailableLanguages
from core.types import BaseCodeRefReturn


class AggregateFunc:
    """
    Реализация агрегатных функций в таблицах. Функции которые созданы здесь(по правилам которые указаны ниже) будут автоматически добавлены в
    `Tables.allowed_func` и в регулярное выражения для их поиска `REGEX.MultiLineTablesDepLogicAggregateFunc`

    ------------

    Для создания новой агрегатной функции нужно создать метод по шаблону

    ```
    @staticmethod
    def f_ИмяАгрегатнойФункции(cls, date: list[str]):
        ...
    ```
    """

    @classmethod
    def main(cls, _m: re.Match, table_body: list[list[str]]) -> str:
        """Точка входа в реализацию логики агрегатных функций"""
        c_s: int = int(_m['c_s'])
        c_e: int = int(_m['c_e'])
        r_s: int = int(_m['r_s'])
        r_e: int = int(_m['r_e'])
        date: Optional[list[str]] = None
        # Если нужно считать столбцы
        if c_s == c_e:
            date = [x[c_s - 1].strip() for x in table_body[r_s - 1:r_e]]
        # Если нужно считать строки
        elif r_s == r_e:
            date = [x.strip() for x in table_body[r_s - 1]][c_s - 1:c_e]
        else:
            logger.warning(f'Строки или столбцы не равны: ({c_s},{c_e},{r_s},{r_e})', 'AggregateFunc.f_avg')
            return _m.group(0)
        if date:
            # После получения списка значений, вызываем указанную агрегатную функцию
            return str(AggregateFunc.__dict__[f"f_{_m['func']}"](cls, date))
        else:
            logger.warning(f'Диапазон ячеек пуст: ({c_s},{c_e},{r_s},{r_e})', 'AggregateFunc.f_avg')
            return _m.group(0)

    @staticmethod
    def _toDecimal(date: list[str]) -> list[Decimal]:
        """Конвертировать список строк в список дробных чисел"""
        return [Decimal(x) for x in date]

    @staticmethod
    def f_avg(cls, date: list[str]) -> Decimal:
        """Среднее значение"""
        date: list[Decimal] = cls._toDecimal(date)
        return sum(date) / len(date)

    @staticmethod
    def f_sum(cls, date: list[str]) -> Decimal:
        """Сумма"""
        date: list[Decimal] = cls._toDecimal(date)
        return sum(date)


class Tables:
    """
    Структура данных для формирования и хранения Markdown таблицы.
    """
    # Доступные агрегатные функции в таблице
    allowed_func = frozenset(x[2:] for x in AggregateFunc.__dict__.keys() if x.startswith('f_'))

    def __init__(self, max_column: int):
        # Заголовок
        self.title: list[str] = []
        # Тело таблицы
        self.body: list[list[str]] = [[]]
        # Сколько максимум колонок в таблице
        self.max_column = max_column
        # Внутренний счетчик текущей строки
        self._next_row = 0
        # Внутренний счетчик текущего столбца
        self._next_column = 0

    def EndBuild(self):
        """
        Преобразования в таблицы после добавления всех строк и столбцов.
        """
        # Переносим заголовки из тела таблицы, в переменную непосредственно для заголовков
        self.title = self.body.pop(0)
        # Удаляем строку с тире, которое должно быть под заголовок.
        self.body.pop(0)
        # Убираем возможность вызвать эту функцию более одного раза у экземпляра класса
        self.EndBuild = lambda *args, **kwargs: None

    def EndMultiLaneBuild(self):
        """
        Преобразования в таблицы для многострочных строк.
        """
        # Массив для результата.
        res: list[list[str]] = [[]]
        # Инициализируем первую строку новой таблицы, пустыми столбцами, количество столбцов будет равно
        # количеству в исходном теле таблицы.
        for _ in self.body[0]: res[0].append('')
        # Индекс последнего столба в результирующий таблице
        _num_col_res = 0
        for _i, _x in enumerate(self.body[:-1]):
            # Если в строке у которой первый столбце НЕ начинается на три тире и более, то тогда считаем эту строку с полезными данными
            if not re.match('\s*-{3,}\s*', self.body[_i][0]):
                # Перебираем столбцы в исходной таблице, так как это строка многострочная то столбцы будут объединиться
                # в единую строчку, до того момента пока не встретиться три тире и более
                for _in, _item in enumerate(self.body[_i]):
                    res[_num_col_res][_in] += f"{_item}\n"
            else:
                # Если в строке первый столбец начинателя на три тире и более, то значит что многострочная строка закончена
                # и должна быть сформироваться новая строка
                res.append([])
                _num_col_res += 1
                for _ in self.body[_i]:
                    res[_num_col_res].append('')
        # Убираем лишний хвост
        res.pop()
        # Делаем подмену исходной таблицы на многострочную
        self.body = res

    def DepLogic(self) -> None:
        """
        Реализуем логику агрегатных функций и простого обращения к ячейкам. Вызываем у таблицы после `EndBuild` и/или `EndMultiLaneBuild`
        """

        # Временное хранение найденного, или не найденного результата
        tmp_re: Optional[re.Match] = None
        # Временное хранение арифметического выражения
        tmp_equations: str = ''
        for _i_r, _row in enumerate(self.body):
            for _i_c, _col in enumerate(_row):
                # Ищем, где есть обращение к агрегатным функциям или ячейкам
                tmp_re = REGEX.MultiLineTablesDepLogic.search(_col)
                if tmp_re:
                    # Получаем результат для агрегатных функций
                    tmp_equations = REGEX.MultiLineTablesDepLogicAggregateFunc.sub(
                        lambda m: AggregateFunc.main(m, self.body) if m['func'] else m.group(0),
                        tmp_re['body']
                    )
                    try:
                        # Получаем арифметическое выражение
                        tmp_equations = REGEX.MultiLineTablesDepLogicSlot.sub(
                            lambda m:
                            self.body[int(m['row']) - 1][int(m['col']) - 1].strip(),
                            tmp_equations
                        )
                    except IndexError:
                        logger.error(
                            f'Недосягаемый столбец или строка {tmp_re["body"]}',
                            'Tables.DepLogic')
                    except ValueError:
                        logger.error(
                            f'Синтаксическая ошибка в ячейке, невозможно конвертировать в число {tmp_re["body"]}',
                            'Tables.DepLogic')
                    try:
                        # Считаем
                        self.body[_i_r][_i_c] = sympify(tmp_equations).__str__()
                    except SympifyError:
                        logger.error(
                            f'Синтаксическая ошибка в ячейке, не возможно произвести вычисления ячейки: {tmp_equations}',
                            'Tables.DepLogic')

    def addColumn_IfEndThenNewRow(self, column: str):
        """
        :param column: Новый столбец в таблицу
        """
        # Добавляем новый столбец в строку,
        self.body[self._next_row].append(column)
        self._next_column += 1
        # Если он будет превышать максимально разрешенное количество столбцов в таблице,
        # то добавляем этот столбце на новую строку
        if self._next_column == self.max_column:
            self._next_column = 0
            self.body.append([])
            self._next_row += 1


class REGEX:
    """
    Класс для хранения регулярных выражений
    """
    # ---   MarkdownDRY   --- #
    # Инициализация ссылочного блока
    ReferenceBlock: re.Pattern = re.compile(
        '\[#(?P<ref_block_name>[\d\w_-]+)]\(\n{2}(?P<ref_block_text>[^\n][^)]+)\n{2}\)'
    )
    # Использование ссылочного блока
    UseReferenceBlock: re.Pattern = re.compile(
        '\[#(?P<use_ref_block>[^]]+)](?P<sm>[ \n]+)'
    )
    # -------------------------

    # -  Скрываемый блок - #
    DropdownBlock: re.Pattern = re.compile(
        "(?P<sp>\? )(?<=\? )(?P<name>.+)\n+(?P<body>(?:.+\n)+)(?=\n+\?\n+)(?P<sp_end>\n+\?)"
    )
    # -------------------------

    # --- Выделение --- #
    HighlightBlock: str = '({sp} )(?<={sp} )(?P<name>.+)\n+(?P<body>(?:.+\n)+)(?=\n+{sp}\n)(\n+{sp}\n)'
    HighlightBlock1: re.Pattern = re.compile(
        HighlightBlock.format(sp='!' * 1)
    )
    HighlightBlock2: re.Pattern = re.compile(
        HighlightBlock.format(sp='!' * 2)
    )
    HighlightBlock3: re.Pattern = re.compile(
        HighlightBlock.format(sp='!' * 3)
    )
    # -------------------------

    # --- Фото галерея --- #
    PhotoGalleryBody: re.Pattern = re.compile(
        '\d+\.\s+!\[(?P<name_img>.*)]\((?P<path>.+)\)'
    )
    PhotoGallery: re.Pattern = re.compile('-\s+(?P<name>.+)\s+(?P<body>(?:\d+\.\s+!\[.*]\(.+\)\s+)+)')
    # ------------------------

    # - Многостраничные кодблоки  - #
    MultiPageCodeBody: re.Pattern = re.compile(
        '(?P<padding>[\n\t ]*)`{3}(?P<lg>[ \w_-]+) *(?:\[(?P<info>[^\n\]]+)])?(?:{(?P<mark>[\d,-]+)})?\n(?P<code>(?:.\s*(?!`{3}))+)\s*`{3}'
    )
    MultiPageCode: re.Pattern = re.compile(
        '-\s+(?P<name>.+)\s+(?P<body>(?:`{3}.+\n(?:.\s*(?!`{3}))+\s*`{3}\s+)+)'
    )
    # ------------------------

    # - Математически блок - #
    # Для поиска математических блоков
    MathSpan: re.Pattern = re.compile(
        '`(?P<preliminary_response>\d*[,.]?\d*)=(?P<body>[^\n`]+)`:?(?P<type>[^ \n.,]+)?'
        # '`(?P<preliminary_response>\d*)=(?P<body>[^\n`]+)`'
    )
    # ------------------------

    # ------------------------
    _BaseCodeRef: str = "\[(?P<name>.*)\]\((?P<path>[^#\n]+)#?(?P<main>[^)\n.]+)?\.?(?P<child>[^.\n)]+)?\)"
    # Поиск мест где нужно вставить код из файла
    InsertCodeFromFile: re.Pattern = re.compile(f"!{_BaseCodeRef}")
    # Бесспорная вставка кода
    IndisputableInsertCodeFromFile: re.Pattern = re.compile(f"!!{_BaseCodeRef}")
    # Поиск мест где нужно сослаться на код
    LinkCode: re.Pattern = re.compile(f"\+{_BaseCodeRef}")
    # Поиск уникального якоря в коде
    AnchorFromCode: str = '(?<={name}>\n)\n*(?:.\s*(?!<{name}))+'
    # ------------------------

    # - Заголовки и переменные - #
    #: Поиск заголовков и его тела.
    HeaderMain: re.Pattern = re.compile(
        '(?P<lvl>#+) (?P<hidden>\^?)(?P<name>.+)(?P<body>(?:.*\s*(?!#+))+\n?)'
    )
    #: Поиск типа заголовка, обычный или скрытый
    # HeaderType: re.Pattern = re.compile('\s*(?P<hidden>\^)?.+')

    #: Поиск инициализированных переменных
    VarsInit: re.Pattern = re.compile(
        '- \[=(?P<name>[^]]+)]\((?P<value>[^\n]+)\):?(?P<type>[^\n]+)?'
        # '- \[=(?P<name>[^]]+)]\((?P<value>.+(?!\n))\)'
    )
    #: Поиск мест, где идет обращение к переменной
    VarsGet: re.Pattern = re.compile('\[=(?P<name>[^]]+)]')
    # ------------------------

    # - Многострочные таблицы - #
    # Найти таблицу
    MultiLineTables: re.Pattern = re.compile(
        "(?:(?:\|[^|\n]+)+\|\n){2,}"
        # "\|(?:.\s*(?!\|\n\n))+\s*\|"
    )
    # Найти строку
    MultiLineTablesRow: re.Pattern = re.compile("(?P<row>\|.+\|)")
    # Найти столбец
    MultiLineTablesColumn: re.Pattern = re.compile("(?<=\|)(?P<column>[^|\n]+)(?=\|)")
    # Поиск многострочного столбца
    MultiLineTablesMultiLineColumn: re.Pattern = re.compile("(?:- +\|\n)(?P<row>\|(?:.\s*(?!\| -))+)")
    # Регулярное выражения для проверки таблица многострочная или обычная
    MultiLineTablesIsMultyOrStandard: re.Pattern = re.compile("(?<=\|)\s+-+\s+(?=\|)")
    # Регулярное выражение для поиска агрегатных функций или обращение к ячейкам
    MultiLineTablesDepLogic: re.Pattern = re.compile("`~(?P<body>[^`]+)`")
    # Поиск обращения ячейкам таблицы, и замена их на значение этой ячейки
    MultiLineTablesDepLogicSlot: re.Pattern = re.compile("(?P<col>\d+),(?P<row>\d+)")
    # Доступные агрегатные функции в таблице
    MultiLineTablesDepLogicAggregateFunc: re.Pattern = re.compile(
        "(?P<func>{func})\((?P<c_s>\d+),(?P<c_e>\d+),(?P<r_s>\d+),(?P<r_e>\d+)\)".format(
            func='|'.join(Tables.allowed_func)
        )
    )
    # ------------------------

    # ---   Markdown    --- #
    # Паттерн для нахождения многострочных списков
    _MultiLineUl_or_Ol = '(?:\n+ {2,}.+)*'
    # Найти все нумерованные и ненумерованные блоки
    BaseBlockUl_or_Ol = re.compile(f'(?:\A|\n)(?:(?:[-+*]|\d+\.)\s+[^\n]+{_MultiLineUl_or_Ol}\n+)+')
    # Не нумерованный список
    Ul: re.Pattern = re.compile(f'[-+*]\s+(?P<ul>[^\n]+{_MultiLineUl_or_Ol})')
    # Нумерованный список
    Ol: re.Pattern = re.compile(f'\d+\.\s+(?P<ol>[^\n]+{_MultiLineUl_or_Ol})')
    # Горизонтальная линия
    Hr: re.Pattern = re.compile('-{3,}')
    # Комментарий %%
    CommentMD: re.Pattern = re.compile('%%(?P<body>\n?(?:.\s*(?!%%))*[^%])%%')
    # Строка с кодом
    CodeLine: re.Pattern = re.compile('`(?P<body>[^`\n]+)`')
    # Блок с кодом
    CodeBlock: re.Pattern = re.compile(
        # Пример взят из `MultiPageCodeBody`
        '`{3}(?P<lg>[ \w_-]+) *(?:\[(?P<info>[^\n\]]+)])?(?:{(?P<mark>[\d,-]+)})?\n(?P<code>(?:.\s*(?!`{3}))+)\s*`{3}')
    # Изображение (не должно быть два восклицательных знаков в начале, так как два восклицательных знака
    # это `IndisputableInsertCodeFromFile`)
    ImgMd: re.Pattern = re.compile("(?<=[^!])!\[(?P<name>[^]]*)]\((?P<path>[^)]*)\)")
    # ----------------------
    Slash: str = "\\"
    Qm1: str = "'"
    NL: str = '\n'


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


class StoreDoc:
    """
    Класс для хранения кеша, который будет использоваться во время сборки
    """
    ReferenceBlock: dict[str, str] = dict()
    DropdownBlock: dict[str, str] = dict()
    # Список строк которые нужно вставить в конце сборки
    LastInsert: list[str] = []

    @classmethod
    def clear(cls):
        """Отчистить кеш. Используется при тестировании проекта"""
        cls.ReferenceBlock.clear()
        cls.DropdownBlock.clear()
        cls.HeaderMain.clear()
        cls.LinkCode.clear()
        cls.LastInsert.clear()

    class LinkCode:
        """
        Кеш для исходного текста файлов, на которые формируются ссылки
        """
        # ИмяФайла:Текст
        date: dict[str, str] = dict()

        @classmethod
        def add(cls, path_file: Path, text: str):
            if not cls.date.get(path_file.__str__(), None):
                cls.date[path_file.__str__()] = text

        @classmethod
        def clear(cls):
            cls.date.clear()

    class HeaderMain:
        """
        Структура для заголовков
        """
        data_body = tuple[int, HeaderType, dict[str, tuple[str, str]], str]
        data_type = dict[str, data_body]
        # Заголовки - ИмяЗаголовка:(УровеньЗаголовка,ТипЗаголовка,{ИмяПеременной:(Значение,IdЗаголовка)},IdЗаголовка)
        date: data_type = dict()

        @classmethod
        def clear(cls):
            """Отчистка"""
            cls.date.clear()

        @classmethod
        def addHeaders(cls,
                       name: str,
                       level: Literal[1, 2, 3, 4, 5, 6],
                       type_header: HeaderType,
                       ) -> str:
            """
            Добавить новый заголовок в кеш

            :param name: Имя заголовка
            :param level: Уровень заголовка
            :param type_header: Тип заголовка
            :return: Уникальный идентификатор заголовка
            """

            def generate_id_header(date: cls.data_type) -> str:
                """
                Создаем уникальный идентификатор заголовка на основе вложенности выше стоящих заголовках
                """
                _last: int = level
                _next: int = 0
                tmp: list[str] = [name]
                for k, v in reversed(date.items()):
                    _next = v[0]
                    if _next > _last:
                        continue
                    elif _last > _next:
                        tmp.append(k)
                    _last = _next
                return ''.join(tmp)

            id_header: str = f"{HTML_CLASS.ScreeningId(name)}_{md5(generate_id_header(cls.date).encode()).hexdigest()}"
            cls.date[name] = (level, type_header.value, dict(), id_header)
            return id_header

        @classmethod
        def addVar(cls, header: str, name: str, value: str, type_value: Optional[str]):
            """
            Добавить переменную в кеш с заголовками

            :param type_value: Тип переменной, используется чисто как подсказка для пользователя
            :param header: Имя Заголовка
            :param name: Имя племенной
            :param value: Значение
            """
            cls.date[header][2][name] = (value, type_value if type_value else '')

        @classmethod
        def getVar(cls, header: str, name: str, default: Optional[str] = None, context: str = None) -> tuple[str, str]:
            """
            Получить значение по имени переменной

            :param header: Имя заголовка
            :param name: Имя переменной
            :param default: Значение если ключа нет
            :param context: Для подробного вывода ошибок, передаем контекст в котором происходит поиск переменных
            :return: (ЗначениеПеременной, ТипПеременной)
            """

            # Ищем переменные в текущем заголовке
            _res = cls.date[header][2].get(name, ('', ''))
            if not _res:
                # Если не найдено в текущем заголовке, то ищем в вышестоящих заголовках

                # Получаем заголовки в которых объявлена такая переменная
                _tmp: list[tuple[str, cls.data_body]] = [
                    (k, v)
                    for k, v in cls.date.items()
                    if v[2].get(name)
                ]
                if _tmp:
                    # Если есть заголовки с такими переменными, то тогда начинаем искать с конца,
                    # до того момента пока следующий заголовок не станет больше предыдущего или равен ему,
                    # все подходящие под это правило элементы попадут в результат, после этого берем первый элемент
                    # из результата так как там объявлена самая новая переменная.
                    _last: int = HeaderType.MaxLvlHeader.value
                    _next: int = 0
                    _tmp2 = []
                    for _index in range(len(_tmp) - 1, -1, -1):
                        _next = _tmp[_index][1][0]
                        if _next >= _last:
                            break
                        _last = _next
                        _tmp2.append(_tmp[_index])
                    _res = _tmp2[0][1][2][name]
                else:
                    logger.error(f"{header=}->{name=}->{context=}", "Переменная не инициализирована")
                    return default, ''
            return _res


class CoreMarkdownDRY:
    """
    MarkdownDRY:

    - Объявление Ссылочный блок - CoreMarkdownDRY.ReferenceBlock
    - Использование Ссылочный блок - CoreMarkdownDRY.UseReferenceBlock
    - Раскрываемые блок - CoreMarkdownDRY.DropdownBlock
    - Выделение блоков - CoreMarkdownDRY.HighlightBlock
    - Фото Галерея - CoreMarkdownDRY.PhotoGallery
    - Многостраничные кодблоки - CoreMarkdownDRY.MultiPageCode
    - Математика - CoreMarkdownDRY.MathSpan
    - Скрытые заголовки - Реализовано в  CoreMarkdownDRY.HeaderMain
    - Вставить кода из файла - CoreMarkdownDRY.InsertCodeFromFile
    - Ссылки на структурные элементы кода - CoreMarkdownDRY.LinkCode
    - Переменные - CoreMarkdownDRY.Vars
        - Найти переменные, записать в кеш реализованно CoreMarkdownDRY.HeaderMain
        - Вставить текст из кеша реализованно CoreMarkdownDRY.HeaderMain
    -  Многострочные таблицы - CoreMarkdownDRY.MultiLineTables
    """

    @classmethod
    def ReferenceBlock(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Ссылочный блок объявление
        """
        if type_out == 'html':
            return REGEX.ReferenceBlock.sub(MDDRY_TO_HTML.ReferenceBlock, source_text)
        else:
            return REGEX.ReferenceBlock.sub(MDDRY_TO_MD.ReferenceBlock, source_text)

    @staticmethod
    def UseReferenceBlock(source_text: str,
                          StoreDocs_ReferenceBlock: StoreDoc.ReferenceBlock = None
                          ) -> Optional[str]:
        """
        Ссылочный блок использование

        :param StoreDocs_ReferenceBlock: Хранилище с объявленными ссылочными блоками
        """
        if not StoreDocs_ReferenceBlock:
            StoreDocs_ReferenceBlock = StoreDoc.ReferenceBlock
        return REGEX.UseReferenceBlock.sub(lambda m: MDDRY_TO_MD.UseReferenceBlock(m, StoreDocs_ReferenceBlock),
                                           source_text)

    @classmethod
    def DropdownBlock(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Раскрываемые блок
        """
        if type_out == 'html':
            return REGEX.DropdownBlock.sub(MDDRY_TO_HTML.DropdownBlock, source_text)
        else:
            return source_text

    @classmethod
    def HighlightBlock(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Выделенный блок
        """
        if type_out == 'html':
            # Поочередно ищем и обрабатываем каждый тип выделения
            for _i, _pattern in enumerate([REGEX.HighlightBlock1, REGEX.HighlightBlock2, REGEX.HighlightBlock3]):
                source_text = _pattern.sub(lambda s: MDDRY_TO_HTML.HighlightBlock(s, _i + 1), source_text)
            return source_text
        else:
            return source_text

    @classmethod
    def PhotoGallery(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Фото Галерея
        """
        if type_out == 'html':
            return REGEX.PhotoGallery.sub(MDDRY_TO_HTML.PhotoGallery, source_text)
        else:
            return source_text

    @classmethod
    def MultiPageCode(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Многостраничные кодблоки
        """
        if type_out == 'html':
            return REGEX.MultiPageCode.sub(MDDRY_TO_HTML.MultiPageCode, source_text)
        else:
            return source_text

    @classmethod
    def MathSpan(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Математический размах
        """
        if type_out == 'html':
            return REGEX.MathSpan.sub(MDDRY_TO_HTML.MathSpan, source_text)
        else:
            return REGEX.MathSpan.sub(lambda m: '='.join(MDDRY_TO_MD.MathSpan(m)), source_text)

    @classmethod
    def InsertCodeFromFile(cls, source_text: str, self_path: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Вставка кода, не трогает `md` файл, а создается в HTML
        """
        if type_out == 'html':
            return REGEX.InsertCodeFromFile.sub(lambda t: MDDRY_TO_HTML.InsertCodeFromFile(t, self_path), source_text)
        else:
            return REGEX.InsertCodeFromFile.sub(lambda t: MDDRY_TO_MD.InsertCodeFromFile(t, self_path), source_text)

    @classmethod
    def IndisputableInsertCodeFromFile(cls, source_text: str, self_path: str) -> Optional[str]:
        """
        Бесспорная вставка кода, выполняется в начале сборки, изменяет `md` файл, а после этого может
        быть конвертирован по остальным правилам `MDDRY`
        """
        return REGEX.IndisputableInsertCodeFromFile.sub(lambda t: MDDRY_TO_MD.IndisputableInsertCodeFromFile(t, self_path),
                                                        source_text)

    @classmethod
    def LinkCode(cls, source_text: str, self_path: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Ссылка на элементы кода
        """
        if type_out == 'html':
            res = REGEX.LinkCode.sub(lambda t: MDDRY_TO_HTML.LinkCode(t, self_path), source_text)
            # Формируем HTML, Исходный код файла + ссылки
            StoreDoc.LastInsert.append(f"""
    <script>
    /* -------------------------- Логика для {HTML_CLASS.LinkCode.value} -------------------------- */
    // Переменная для хранения исходного кода из файлов. Храниться в кодировки UTF-8, для экранирования спец символов
    {HTML_CLASS.LinkSourceCode.value}={{
        {','.join(f'"{k}":decodeURIComponent(escape(atob({REGEX.Qm1}{repr(b64encode(v.encode("utf8")))[2:-1]}{REGEX.Qm1})))' for k, v in StoreDoc.LinkCode.date.items())}
    }};
    {HTML_JS.LinkCode}
    /* --------------------------------------------------------------------------------------------- */
    </script>
            """[1:])
            return f"""
    <!-- Всплывающие окно с исходным кодом из файла ------------------------------------------ -->
    <div id="{HTML_CLASS.LinkCodeWindow.value}" onclick="OnHide(event)">
        <div id="{HTML_CLASS.LinkCodeWindowDet.value}">
            <div id="{HTML_CLASS.LinkCodeWindowButtonTitle.value}">
                <div id="{HTML_CLASS.LinkCodeName.value}"></div>
                <input type="button" id="{HTML_CLASS.LinkCodeWindowButtonHide.value}" value="Скрыть" onclick="{HTML_CLASS.LinkCodeWindow.value}.style.display='none'">
            </div>
            <pre class="{HTML_CLASS.code.value}" id="{HTML_CLASS.LinkCodeWindowBody.value}">
            </pre>
        </div>
        <div id="{HTML_CLASS.LinkCodeWindowFooter.value}">
            <div id="{HTML_CLASS.LinkCodeWindowPath.value}"></div>
        </div>
    </div>
    <!-- ---------------------------------------------------------------------------------------- -->
    {res}
    """[1:]
        else:
            return source_text

    @classmethod
    def HeaderMain(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Поиск заголовка и его тела
        """
        if type_out == 'html':
            res = REGEX.HeaderMain.sub(lambda m: MDDRY_TO_HTML.HeaderMain(m, type_out=type_out), source_text)

            def create_table_contents_from_HTML(
                    hed: StoreDoc.HeaderMain.data_type,
                    template_li: str = "<li>{header}</li>"
            ) -> str:
                """
                Сделать оглавление в формате HTML

                :param template_li: Шаблон для элемента оглавления
                :param hed: ИмяЗаголовка:(УровеньЗаголовка, ЛюбоеЧисло, ЛюбойСловарь)

                :ПРИМЕР:

                IN:
                {
                    'Стек технологий': (1, 0, {}),
                    'БД': (2, 0, {}),
                    'SQL': (3, 0, {}),
                    'NoSQL': (3, 0, {}),
                    'Frontend': (2, 0, {}),
                    'Брокеры сообщений': (2, 0, {}),
                    'Диплой': (2, 0, {}),
                    'Ссылки на документацию': (1, 0, {}),
                    'Ошибки': (1, 0, {}),
                    'Ошибки связанные с API': (2, 1, {}),
                    'Ошибки связанные с БД': (2, 1, {}),
                    'Ошибки в UI': (2, 1, {}),
                    'Ошибки связанные с VPN': (2, 1, {}),
                    'Ошибки связанные с Легаси кодом': (2, 1, {}),
                    'Готовые решения задач': (1, 0, {})
                }
                --------------------------------------------------
                OUT:
                <ol>
                    <li>Стек технологий</li>
                    <ol>
                        <li>БД</li>
                        <ol>
                            <li>SQL</li>
                            <li>NoSQL</li>
                        </ol>
                        <li>Frontend</li>
                        <li>Брокеры сообщений</li>
                        <li>Диплой</li>
                    </ol>
                    <li>Ссылки на документацию</li>
                    <li>Ошибки</li>
                    <ol>
                        <li>Ошибки связанные с API</li>
                        <li>Ошибки связанные с БД</li>
                        <li>Ошибки в UI</li>
                        <li>Ошибки связанные с VPN</li>
                        <li>Ошибки связанные с Легаси кодом</li>
                    </ol>
                    <li>Готовые решения задач</li>
                </ol>
                --------------------------------------------------

                """
                _tmp = [(k, v) for k, v in hed.items()]
                _last: int = 0
                _res: list[str] = []
                for _val in _tmp:
                    _next: int = _val[1][0]
                    if _next > _last:
                        _res.append("<ol>")
                    elif _next < _last:
                        _res.append("</ol>")
                    # Не скрытый заголовок попадает в оглавление
                    if _val[1][1] != HeaderType.Hide.value:
                        _res.append(template_li.format(
                            # Экранированный уникальный id заголовка
                            header_esp=_val[1][3]
                            # Вставляем текст как есть
                            , header_raw=_val[0])
                        )
                    _last = _next
                _res.append("</ol>")
                return ''.join(_res)

            StoreDoc.LastInsert.append(f"""
            <script>
            {HTML_JS.HeaderMain}
            </script>
            """[1:])
            # Формируем навигационное оглавление по заголовкам
            return "{menu}{res}".format(menu=f"""
            <div id="{HTML_CLASS.menu.value}">
                <!-- Скрыть оглавление -->
                <input type="button" id="bt_show_menu" value="<<"
                       onclick="{HTML_CLASS.menu.value}_hidden()">
                <!-- Развернуть оглавление -->
                <input type="button" id="bt_hidden_menu" value=">>"
                       onclick="{HTML_CLASS.menu.value}_show()"/>
                <!-- Темы оглавления -->
                <div id="{HTML_CLASS.detail_menu.value}">
                    <ol>
                        {create_table_contents_from_HTML(StoreDoc.HeaderMain.date, '<li><a href="#{header_esp}">{header_raw}</a></li>')}
                    </ol>
                </div>
            </div>
            """[1:], res=res)
        else:
            return REGEX.HeaderMain.sub(lambda m: MDDRY_TO_HTML.HeaderMain(m, type_out=type_out), source_text)

    @classmethod
    def MultiLineTables(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Многострочные таблицы, и обычные
        """
        # TODO: реализовать type_out: Literal['html', 'md']
        if type_out == 'html':
            return REGEX.MultiLineTables.sub(MDDRY_TO_HTML.MultiLineTables, source_text)
        else:
            return source_text

    class DeepLogic:
        """Углубленная логика MarkdownDRY"""

        @staticmethod
        def BaseCodeRef(m: re.Match, self_path: str) -> Optional[BaseCodeRefReturn]:
            """
            Подготовить параметры для ссылки на код
            """
            name_re: str = m['name']
            main_re: str = m['main']
            child_re: str = m['child']
            if not m['path']:
                return None
            # Путь к исходному файлу
            path_re: Path = Path(m['path'])
            # Проверим что это НЕ бинарный файл, путем просмотра расширения файла. Если это бинарный файл, то выходим из функции
            if AvailableLanguages.Binary.value.search(path_re.suffix):
                return None
            # Язык программирования или разметки
            lange_file: Lange
            # Исходный текст кода
            text_in_file: str
            # Проверяем куда указывает путь, локально или в интернет
            path_or_url = re.match('(https|http|ftp|tcp|localhost):', m['path'])
            if path_or_url:
                """Это ссылку в интернет"""
                logger.debug(m['path'], 'URL')
                lange_file = ConvertSuffixToLange.getlang(path_re.suffix)
                # Скачиваем исходный текст из интернета
                text_in_file = requests.get(m['path']).text
            else:
                """Это локальный путь"""
                logger.debug(path_re, 'LOCAL')  # Path(self_path, m['path']).resolve().__str__()
                lange_file = ConvertSuffixToLange.getlang(path_re.suffix)
                # Читаем файл по абсолютному пути
                try:
                    text_in_file = Path(self_path, path_re).resolve().read_text()
                except FileNotFoundError as e:
                    logger.error(f"{path_re}:\n{e}", "LOCAL_BaseCodeRef")  # path_re
                    return None
                except TypeError as e:
                    logger.error(f"{path_re}:\n{e}", "LOCAL_BaseCodeRef")  # path_re
                    return None

            # Формируем ссылку для `HTML`
            ref = f"{f'{main_re}' if main_re else ''}{f'.{child_re}' if child_re else ''}"
            # Переменная для указания начало найденного элемента
            line_start = 0
            # Переменная для указания конца найденного элемента
            line_end = -1
            # Обрезанный текст
            text_in_file_cup: str = text_in_file
            # Если указано, что вставлять, то вставляем этот участок код из файла
            if main_re:
                # Если указывает на класс/функцию/переменную
                text_in_file_cup, line_start, line_end = lange_file.REGEX.class_func_var_anchor(main_re, text_in_file)
                if child_re:
                    # Если указывает на метод класса/атрибут класса
                    text_in_file_cup, tmp_line_start, tmp_line_end = lange_file.REGEX.class_meth_attr(child_re, text_in_file_cup)
                    # Конец текста
                    line_end = line_start + tmp_line_end if tmp_line_end else 0
                    # Начало текст
                    line_start = line_start + tmp_line_start if tmp_line_start else 0
            return BaseCodeRefReturn(name_re=name_re,
                                     text_in_file_cup=text_in_file_cup,
                                     text_in_file=text_in_file,
                                     line_start=line_start,
                                     line_end=line_end,
                                     ref=ref,
                                     file=path_re)


class MDDRY_TO_HTML:
    """
    Класс для конвертации MarkdownDRY в HTML
    """

    @staticmethod
    def ReferenceBlock(m: re.Match) -> str:
        """Ссылочные блоки"""
        # Заносим найденные ссылочные блоки в общий кеш документа
        StoreDoc.ReferenceBlock[m['ref_block_name']] = m['ref_block_text']
        # Формируем html
        return f"""
<div class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.InReferenceBlock.value}">
<div hidden>{m['ref_block_name']}</div>
<div>
    {m['ref_block_text']}
</div>
</div>
"""[1:]

    @staticmethod
    def DropdownBlock(m: re.Match) -> str:
        """Раскрываемые блоки"""
        # Заносим найденные ссылочные блоки в общий кеш документа
        StoreDoc.DropdownBlock[m['name']] = m['body']
        # Формируем html
        return f"""
<div class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.DropdownBlock.value}">
<div class="{HTML_CLASS.DropdownBlockTitle.value}">{m['name']}</div>
<div class="{HTML_CLASS.DropdownBlockText.value}">
    {m['body']}
</div>
</div>      
"""[1:]

    @staticmethod
    def HighlightBlock(m: re.Match, level: int) -> str:
        """Выделение блоков"""
        SelectHighlightBlock: Optional[HTML_CLASS] = None
        # В зависимости от количества знаков
        match level:
            case 1:
                SelectHighlightBlock = HTML_CLASS.HighlightBlock1
            case 2:
                SelectHighlightBlock = HTML_CLASS.HighlightBlock2
            case 3:
                SelectHighlightBlock = HTML_CLASS.HighlightBlock3
        res = f"""
<div class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.HighlightBlock.value} {SelectHighlightBlock.value}">
<div class="{HTML_CLASS.HighlightTitle.value}">{m['name']}</div>
<div class="{HTML_CLASS.HighlightBody.value}">
{m['body']}
</div>
</div>
"""[1:]
        return res

    @classmethod
    def PhotoGallery(cls, m: re.Match) -> str:
        """Фото галерея"""
        body_img = [f"""
<div class="carousel-item{' active' if i == 0 else ''}">
<img src="{x["path"]}" alt="{x["name_img"]}" class="d-block">
<h3>{x["name_img"]}</h3>
</div>    
"""[1:] for i, x in enumerate(REGEX.PhotoGalleryBody.finditer(m['body']))]
        return cls._slide_block(m['name'], body_img, class_2=HTML_CLASS.PhotoGallery)

    @classmethod
    def PageCode(cls, body: str, regex: re.Pattern) -> [int, str, str, str]:
        """
        Блок кодом, доступно:

        1. Указание описание для языка разметки
        2. Так же происходит выделение строк в коде.

        :param body: Тело с кодом
        :param regex: Каким регулярным выражение искать
        """
        for _index, _x in enumerate(regex.finditer(body)):
            # Строки которые нужно выделить
            mark: Optional[str] = _x['mark']
            mark: str = mark.strip() if mark else ''
            # Язык текста
            lange: str = _x['lg'].strip()
            # Текст
            code: str = _x['code'].strip()
            # Если нужно выделить строчки
            if mark:
                line_code = code.split('\n')
                max_len = len(max(line_code, key=len))
                # Позиционно маркировать стоки в коде
                for _line in mark.split(','):
                    if _line.isnumeric():
                        _line = int(_line) - 1
                        # Выделим строку
                        line_code[_line] = f'<span>{line_code[_line].ljust(max_len)}</span>'
                    else:
                        # Переводим диапазон {3-6} в конкретные числа [3,4,5,6]
                        _start, _end = list(map(int, _line.split('-')))
                        for _line_range in range(_start - 1, _end):
                            # Выделим строку
                            line_code[_line_range] = f'<span>{line_code[_line_range].ljust(max_len)}</span>'
                # Объедение сточек в цельный текст
                line_code = '\n'.join(line_code)
            # Если не нужно выделять строки
            else:
                line_code = code
            yield _index, lange, line_code, _x["info"]

    @classmethod
    def MultiPageCode(cls, m: re.Match) -> str:
        """Многостраничные кодблоки"""
        body_code: list[str] = []
        for index, lange, line_code, info in cls.PageCode(m.group(0), REGEX.MultiPageCodeBody):
            body_code.append(f"""
<div class="carousel-item{' active' if index == 0 else ''}">
{f'<h3>{info}</h3>' if info else ''}
<div>
<pre class="{HTML_CLASS.code.value} {lange}">
{HTML_CLASS.toCode(line_code)}
</pre>
</div>
</div>    
"""[1:])
        return cls._slide_block(m['name'], body_code, class_2=HTML_CLASS.MultiPageCode)

    @staticmethod
    def _slide_block(title: str, body: list[str], class_2: HTML_CLASS) -> str:
        """
        Формирование прокручиваемого виджета

        :param title: Заголовок виджета
        :param body: Тело которе будет прокручиваться в виджете
        :param class_2: Класс тела
        """
        count_items = len(body)
        body = ''.join(body)
        id_hash = f"i{md5(body.encode()).hexdigest()}"
        bt_down_slide = ''.join(
            f"""<button type="button" data-bs-target="#{id_hash}" data-bs-slide-to="{_index}"{' class="active"' if _index == 0 else ''}></button>"""
            for _index in range(count_items)
        )
        return f"""
<div class="{HTML_CLASS.MarkdownDRY.value} Slider {class_2.value}">
    <h2>{title}</h2>
    <!--
    data-touch="true" -- Должна ли карусель поддерживать смахивание влево/вправо на устройствах с сенсорным экраном.
    data-bs-interval="false" -- отключить авто переключение фото
    data-pause="false" -- убрать авто переключение фото
    data-touch="true" -- переключение фото с помощью клавиш
    -->
    <div id="{id_hash}"
        class="carousel slide"
        data-ride="carousel"
        data-pause="false"
        data-touch="true"
        data-bs-interval="false"
        data-keyboard="true" >

        <!-- Список элементов для прокрутки -->
        <div class="carousel-inner">
            {body}
        </div>
        <!-- Навигация по элементам -->
        <div class="slider_nav">
            <!-- Кнопки переключение с лево и право -->
            <button class="carousel-control-prev" type="button" data-bs-target="#{id_hash}" data-bs-slide="prev">
                <span class="carousel-control-prev-icon"></span>
            </button>
            <!-- Кнопки снизу -->
            <div class="carousel-indicators">{bt_down_slide}</div>
            <button class="carousel-control-next" type="button" data-bs-target="#{id_hash}" data-bs-slide="next">
                <span class="carousel-control-next-icon"></span>
            </button>
        </div>
    </div>
</div>
"""[1:]

    @classmethod
    def MathSpan(cls, m: re.Match, body: str = None, info: str = '') -> str:
        """
        Высчитываем математическое выражение с помощью SymPy, и возвращаем результат выражения в виде `HTML`

        :param m:
        :param body: Тело математического выражения, это нужно, для того чтобы передавать значения из переменных, а не сами переменные
        :param info: Информацией о математическом выражение, например из каких переменных состоит математическое выражение
        """
        text: str = body if body else m['body']
        type_math_span: str = m["type"] if m["type"] else ''
        # Ответ, Выражение
        res: tuple[str, str] = MDDRY_TO_MD.MathSpan(m, body)
        return f"""
<div class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.MathSpanBody.value}">
    {f'<div class="{HTML_CLASS.MathSpanInfo.value}">{info if info else "_" * len(type_math_span)}<div class="{HTML_CLASS.MathSpanType.value}">{type_math_span}</div></div>'}
    <span class="{HTML_CLASS.MathSpan.value}"><span class="{HTML_CLASS.MathResult.value}">{res[0]}</span>={res[1]}</span>
</div>"""[1:]

    @classmethod
    def InsertCodeFromFile(cls, m: re.Match, self_path: str) -> Optional[str]:
        """Вставка кода"""
        res: BaseCodeRefReturn = CoreMarkdownDRY.DeepLogic.BaseCodeRef(m, self_path)
        if not res:
            # Если нет ответа то вернем тот же текст
            return m.group(0)
        return f"""
<div class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.InsertCodeFromFile.value}">
<div>{res.name_re}</div>
<pre class="{HTML_CLASS.code.value}">{HTML_CLASS.toCode(HTML_CLASS.ReplaceGtLt(res.text_in_file_cup))}</pre>
</div>"""[1:]

    @classmethod
    def LinkCode(cls, m: re.Match, self_path: str) -> Optional[str]:
        """Ссылка на код"""
        res: BaseCodeRefReturn = CoreMarkdownDRY.DeepLogic.BaseCodeRef(m, self_path)
        if not res:
            # Если нет ответа то вернем тот же текст
            return m.group(0)
        # Записать в кеш исходный текст из файла
        StoreDoc.LinkCode.add(res.file, HTML_CLASS.ReplaceGtLt(res.text_in_file))
        return f"""
<a href="#" class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.LinkCode.value}" file="{res.file.__str__()}" ref="{res.ref}" char_start="{res.line_start}" char_end="{res.line_end}">{res.name_re}</a>
"""[1:]

    @classmethod
    def HeaderMain(cls, m: re.Match, type_out: Literal['html', 'md']) -> str:
        """
        Ищем все заголовки. Нам нужно получить имя заголовка, его уровень, и его тело. После этого проверяем тип заголовка, он
        может быть обычным, а может быть скрытым. Потом находим инициализацию переменных. После этого заносим данные в кеш
        `StoreDoc.HeaderMain`.

        После этого проверяем есть ли обращения к переменным в заголовке, если есть то тогда проверяем кеш на наличие переменных
        к которым идет обращение. Логика поиска переменных похоже на область видимости в других языках - поиск начинается от текущего заголовка
        и идет вверх по заголовкам, поиск остановиться в тот момент когда следующий заголовок будет не уменьшатся, а увеличиваться.

        Например, если заголовки идут как - [3,2,1,2] то в результате будет [3,2,1]

        После этого происходит замена обращение к переменной на значение переменной.
        """

        # Получаем имя заголовка
        name_head = m['name']
        # Получим тело заголовка
        body_header: str = m['body']
        # Получаем тип заголовка
        res_HeadersType: Optional[HeaderType] = None
        if m['hidden']:
            res_HeadersType = HeaderType.Hide
            res_HeadersTypeHtml = HTML_CLASS.HiddenHeaders.value
        else:
            res_HeadersType = HeaderType.Standard
            res_HeadersTypeHtml = HTML_CLASS.StandardHeaders.value
        # Получаем уровень заголовка
        level: Literal[1, 2, 3, 4, 5, 6] = len(m['lvl'])
        # Добавляем заголовок в кеш, получаем id для заголовка
        name_from_id = StoreDoc.HeaderMain.addHeaders(name_head, level, res_HeadersType)

        #: Поиск инициализации переменных
        def _vars_init(_m: re.Match) -> str:
            """
            Наглядный пример:

            - [=Имя](Иван)
            - [=Фамилия]([=Имя] Иванов)
            - [=Отчество]([=Имя] Иванов Иванович):ТипИмяОтчество

            В итоге `[=Фамилия]` будет равен Иванов Иван
            """
            # Обработать вложенных переменных, То есть когда мы обращаемся к другой переменной во время инициализации текущей,
            # ищем вложенные переменной и подставляем их значение в текущую переменную.
            _nested_var = REGEX.VarsGet.sub(lambda _n_v:
                                            StoreDoc.HeaderMain.getVar(name_head, _n_v['name'], context=_m.group(0))[0],
                                            _m['value']
                                            )
            # Переменная с результатом
            res_var: str = _nested_var if _nested_var else _m['value']
            # Проврем на возможность наличия в значение математического выражения `MathSpan`
            is_math_span: re.Match = REGEX.MathSpan.match(res_var)
            if is_math_span:
                # Если есть `MathSpan`, то высчитываем выражение.
                res_var = MDDRY_TO_MD.MathSpan(is_math_span)[0]
            # Записываем переменные в кеш заголовка
            StoreDoc.HeaderMain.addVar(name_head, _m['name'], res_var, _m['type'])
            # Скрываем из выходного текста инициализацию переменных,
            # все данные о переменных теперь хранятся в `StoreDoc.HeaderMain`
            return f"%%{_m['name']}={res_var}:{_m['type']}%%"

        def _vars_get_from_math_span(_m: re.Match) -> str:
            """
            Вставка значений в места, где идет обращение к переменным,
            область вставки внутри математического выражению `MathSpan`.
            """
            # Если в математическом выражение нет обращения к переменным, то пропускам такое выражение,
            # его должны обработать отдельно на этапе `MathSpan`
            is_math_span = False

            def _self(_m2: re.Match) -> str:
                nonlocal is_math_span
                is_math_span = True
                return StoreDoc.HeaderMain.getVar(name_head, _m2['name'], default=_m2.group(0))[0]

            res = REGEX.VarsGet.sub(_self, _m['body'])
            if is_math_span:
                if type_out == 'html':
                    return MDDRY_TO_HTML.MathSpan(_m,
                                                  body=res,
                                                  info=re.sub(':[^ \n.,]+', '', _m.group(0)).replace('[=', '[').replace('`', '')
                                                  )
                else:
                    return '='.join(MDDRY_TO_MD.MathSpan(_m, body=res))
            else:
                return _m.group(0)

        def _vars_get(_m: re.Match) -> str:
            """
            Вставка значений и тип(переменной) в места, где идет обращение к переменным.
            Область вставки во всем тексе.
            """
            return '.'.join(StoreDoc.HeaderMain.getVar(name_head, _m['name'], default=_m.group(0)))

        body_header = REGEX.VarsInit.sub(_vars_init, body_header)
        # Обрабатываем обращения к переменным которые находятся внутри математического выражения `MathSpan`.
        body_header = REGEX.MathSpan.sub(_vars_get_from_math_span, body_header)
        # Обрабатываем обращения во всем тексе.
        body_header = REGEX.VarsGet.sub(_vars_get, body_header)
        if type_out == 'html':
            return f"""<h{level} id="{name_from_id}" class="{HTML_CLASS.MarkdownDRY.value} {res_HeadersTypeHtml}"><div class="{HTML_CLASS.mddry_name.value}">{name_head}</div><span class="{HTML_CLASS.paragraph.value}">¶</span><div class="{HTML_CLASS.mddry_level.value}">{level}</div></h{level}>\n{body_header}\n"""
        else:
            return f"""{m['lvl']} {m['hidden']}{name_head}\n{body_header}"""

    @classmethod
    def MultiLineTables(cls, m: re.Match) -> str:
        """Многостраничная таблица"""
        text = m.group(0)
        # Узнаем сколько столбцов в таблице
        count_column = REGEX.MultiLineTablesRow.match(text).group(0).count('|') - 1
        # Формируем таблицу
        tb = Tables(max_column=count_column)
        for _index, _head_table in enumerate(REGEX.MultiLineTablesColumn.finditer(text)):
            tb.addColumn_IfEndThenNewRow(_head_table['column'].rstrip())
        # После вставки всех строк и столбцов, производим конечное преобразование таблицы
        tb.EndBuild()
        # Если это многостраничная таблица, то проводим дополнительные преобразования
        if len(REGEX.MultiLineTablesIsMultyOrStandard.findall(text)) > count_column:
            tb.EndMultiLaneBuild()
        logger.debug(tb.title, flag='MultiLineTables Title')
        logger.debug(tb.body, flag='MultiLineTables Body')
        # Реализуем логику агрегатных функций и простого обращения к ячейкам. Вызываем у таблицы после `EndBuild` и/или `EndMultiLaneBuild`
        tb.DepLogic()
        # Формируем таблицу на языке html
        return f"""
<div class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.MultiLineTables.value}">
<table>
<thead>
<tr>
{''.join(f'<th>{x}</th>' for x in tb.title)}
</tr>
</thead>
<tbody>
{''.join(f'<tr>{"".join(f"<td>{y}</td>" for y in x)}</tr>' for x in tb.body).replace(f'{REGEX.NL}', "<br>")}
</tbody>
</table>        
</div>
"""[1:]


class MDDRY_TO_MD:
    """
    Класс для конвертации MarkdownDRY в Markdown
    """

    @staticmethod
    def ReferenceBlock(m: re.Match) -> str:
        """Ссылочные блоки"""
        # Заносим найденные ссылочные блоки в общий кеш документа
        StoreDoc.ReferenceBlock[m['ref_block_name']] = m['ref_block_text']
        # Формируем html
        return m.group(0)

    @staticmethod
    def UseReferenceBlock(m: re.Match, StoreDocs_ReferenceBlock: StoreDoc.ReferenceBlock) -> str:
        """
        Использование ссылочного блока
        """
        # Берем тест блока из хранилища
        res = StoreDocs_ReferenceBlock.get(m['use_ref_block'])
        if res:
            return f"{res}{m['sm']}"
        else:
            # Если такого блока нет в хранилище, то возвращаем тот же текст
            return m.group(0)

    @classmethod
    def IndisputableInsertCodeFromFile(cls, m: re.Match, self_path: str) -> Optional[str]:
        """Бесспорная вставка кода"""
        return Path(self_path, m['path']).resolve().read_text()

    @classmethod
    def MathSpan(cls, m: re.Match, body: str = None) -> tuple[str, str]:
        """
        Высчитываем математическое выражение с помощью SymPy, и возвращаем результат выражения

        :param m:
        :param body: Тело математического выражения, это нужно, для того чтобы передавать значения из переменных, а не сами переменные
        """
        """
       Доработать математический размах, сделать подсказку переменной, и её типа,
       добавить возможность самому писать ответ к выражению, но все равно делать
       расчеты для проверки правильности указного ответа, если ответы разные то
       выдавать ошибку сборки!
       """

        text: str = body if body else m['body']
        preliminary_response: Optional[str] = m['preliminary_response']
        try:
            res = sympify(text).__str__()
            # Если есть предварительный ответ, и он не равен ответу от `SymPy`
            if preliminary_response and preliminary_response != res:
                # То записываем в лог ошибку и возвращаем выражение без изменений
                logger.error(f"В уравнение {m.group(0)} ожидался ответ={preliminary_response}, но получен={res}",
                             "Не равные ответы в `MathSpan`")
                return f'!ERROR!', text
            else:
                return res, text
        except SympifyError:
            logger.error(f"{text}", "MathSpan")
            return '!ERROR!', text

    @classmethod
    def InsertCodeFromFile(cls, m: re.Match, self_path: str) -> Optional[str]:
        """Вставка кода"""
        res: BaseCodeRefReturn = CoreMarkdownDRY.DeepLogic.BaseCodeRef(m, self_path)
        if not res:
            # Если нет ответа то вернем тот же текст
            return m.group(0)
        return f"{res.name_re}\n\n{res.text_in_file_cup}"
