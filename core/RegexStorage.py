import re
from decimal import Decimal
from typing import Optional

from logsmal import logger
from sympy import SympifyError, sympify


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
    # Вставить тег <br> если есть два переноса
    Br: re.Pattern = re.compile("\n")
    # ----------------------
    Slash: str = "\\"
    Qm1: str = "'"
    NL: str = '\n'
