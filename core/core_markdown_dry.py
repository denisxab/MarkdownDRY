import re
import re
import typing
from base64 import b64encode
from hashlib import md5
from pathlib import Path
from typing import Optional, Literal

import requests
from logsmal import logger
from prettytable import HEADER
from sympy import sympify, SympifyError

from core.RegexStorage import REGEX, Tables
from core.core_html import HTML_CLASS, HTML_JS
from core.core_lang import Lange, ConvertSuffixToLange, AvailableLanguages, BaseCodeRefReturn
from core.helpful import ptabel
from core.types import HeaderMain_data_body, HeaderType, HeaderMain_ValueVar, \
    HeaderMain_Headers_With_Found_Variables, HeaderMain, ProceduralTemplatesTypeBody


class StoreDoc:
    """
    Класс для хранения кеша, который будет использоваться во время сборки
    """
    ReferenceBlock: dict[str, str] = dict()
    DropdownBlock: dict[str, str] = dict()
    # Список строк которые нужно вставить в конце сборки
    LastInsert: list[str] = []

    class ProceduralTemplates:
        """Процедурные шаблоны"""
        # Словарь процедурных шаблонов. {ИмяПроцедуры,(ТекстПроцедуры,{ИмяПеременной,(ЗначениеПоУмолчанию,)})}
        # TODO: Реализовать значение по умолчанию, для переменных в процедурных шаблонах
        date: dict[str, ProceduralTemplatesTypeBody] = dict()

        @classmethod
        def addVars(cls, name_procedure: str, name_var: str):
            """Добавить в указанную процедуру переменные"""
            cls.date[name_procedure].vars[name_var] = ''

        @classmethod
        def addProcedure(cls, name_procedure: str, text_procedure: str):
            """Добавить процедуру и её текст"""
            res = cls.date.get(name_procedure)
            if not res:
                cls.date[name_procedure] = ProceduralTemplatesTypeBody(text_procedure=text_procedure, vars=dict())

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

        # Заголовки - ИмяЗаголовка:(УровеньЗаголовка,ТипЗаголовка,{ИмяПеременной:(Значение,IdЗаголовка)},IdЗаголовка)
        date: HeaderMain.date = dict()

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
            Добавить новый заголовок в кеш.

            :param name: Имя заголовка
            :param level: Уровень заголовка
            :param type_header: Тип заголовка
            :return: Уникальный идентификатор заголовка
            """

            def generate_id_header(date: cls.date) -> str:
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

            uuid_header: str = f"{HTML_CLASS.ScreeningId(name)}_{md5(generate_id_header(cls.date).encode()).hexdigest()}"
            cls.date[name] = HeaderMain_data_body(level=level,
                                                  type_header=type_header.value,
                                                  vars=dict(),
                                                  uuid_header=uuid_header)
            return uuid_header

        @classmethod
        def addVar(cls, header: str, name: str, value: str, type_value: Optional[str]):
            """
            Добавить переменную в кеш с заголовками

            :param type_value: Тип переменной, используется чисто как подсказка для пользователя
            :param header: Имя Заголовка
            :param name: Имя племенной
            :param value: Значение
            """
            cls.date[header].vars[name] = HeaderMain_ValueVar(value=value, type=type_value if type_value else '')

        @classmethod
        def getVar(cls, header: str, name: str, default: Optional[str] = None, context: str = None) -> tuple[str, str]:
            """
            Получить значение по имени переменной

            :param header: Имя заголовка
            :param name: Имя переменной
            :param default: Значение если ключа нет
            :param context: Для подробного вывода в лог с ошибками, передаем контекст в котором происходит поиск переменных
            :return: (ЗначениеПеременной, ТипПеременной)
            """

            # Ищем переменные в текущем заголовке
            _res = cls.date[header].vars.get(name, ('', ''))
            if _res == ('', ''):
                # Если не найдено в текущем заголовке, то ищем в вышестоящих заголовках

                # Получаем заголовки в которых объявлена такая переменная
                _tmp: list[HeaderMain_Headers_With_Found_Variables] = [
                    HeaderMain_Headers_With_Found_Variables(name_head=k, value=v)
                    for k, v in cls.date.items()
                    if v.vars.get(name)
                ]
                if _tmp:
                    # Если есть заголовки с такими переменными, то тогда начинаем искать с конца,
                    # до того момента пока следующий заголовок не станет больше предыдущего или равен ему,
                    # все подходящие под это правило элементы попадут в результат, после этого берем первый элемент
                    # из результата так как там объявлена самая новая переменная.
                    _last: int = HeaderType.MaxLvlHeader.value
                    _next: int = 0
                    _tmp2: list[HeaderMain_Headers_With_Found_Variables] = []
                    for _index in range(len(_tmp) - 1, -1, -1):
                        _next = _tmp[_index].value.level  # _tmp[_index][1][0]
                        if _next >= _last:
                            break
                        _last = _next
                        _tmp2.append(_tmp[_index])
                    _res = _tmp2[0].value.vars[name]
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
            return REGEX.ReferenceBlock.sub(lambda m: GenericMDDRY.ReferenceBlock(m, MDDRY_TO_HTML.ReferenceBlock), source_text)
        else:
            return REGEX.ReferenceBlock.sub(lambda m: GenericMDDRY.ReferenceBlock(m, MDDRY_TO_MD.ReferenceBlock), source_text)

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
        return REGEX.UseReferenceBlock.sub(lambda m: GenericMDDRY.UseReferenceBlock(m, StoreDocs_ReferenceBlock),
                                           source_text)

    @classmethod
    def ProceduralTemplates(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Процедурные шаблоны объявление
        """
        if type_out == 'html':
            return REGEX.ProceduralTemplates.sub(lambda m: GenericMDDRY.ProceduralTemplates(m, MDDRY_TO_HTML.ProceduralTemplates),
                                                 source_text)
        else:
            return REGEX.ProceduralTemplates.sub(lambda m: GenericMDDRY.ProceduralTemplates(m, MDDRY_TO_MD.ProceduralTemplates),
                                                 source_text)

    @staticmethod
    def UseProceduralTemplates(source_text: str,
                               StoreDocs_ProceduralTemplates: StoreDoc.ProceduralTemplates = None
                               ) -> Optional[str]:
        """
        Ссылочный блок использование

        :param StoreDocs_ProceduralTemplates: Хранилище с объявленными ссылочными блоками
        """
        if not StoreDocs_ProceduralTemplates:
            StoreDocs_ProceduralTemplates = StoreDoc.ProceduralTemplates
        return REGEX.UseProceduralTemplates.sub(
            lambda m: GenericMDDRY.UseProceduralTemplates(m, StoreDocs_ProceduralTemplates,
                                                          call_format=MDDRY_TO_MD.UseProceduralTemplates),
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
            return REGEX.MathSpan.sub(lambda m: MDDRY_TO_MD.MathSpan(m), source_text)

    @classmethod
    def InsertCodeFromFile(cls, source_text: str, self_path: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Экранированная вставка текста из файла, в код блок, далее он будет обработан стандартным `Markdown` этапом для код блоков
        """
        if type_out == 'html':
            return REGEX.InsertCodeFromFile.sub(lambda t: MDDRY_TO_HTML.InsertCodeFromFile(t, self_path), source_text)
        else:
            return REGEX.InsertCodeFromFile.sub(lambda t: GenericMDDRY.InsertCodeFromFile(t, self_path), source_text)

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
            res = REGEX.HeaderMain.sub(
                lambda m: GenericMDDRY.HeaderMain.call(m, MDDRY_TO_HTML.HeaderMain, MDDRY_TO_HTML.MathSpan), source_text)

            def create_table_contents_from_HTML(
                    hed: StoreDoc.HeaderMain.date,
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
                            header_esp=_val[1][3],
                            # Вставляем текст как есть
                            header_raw=_val[0])
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
            return REGEX.HeaderMain.sub(
                lambda m: GenericMDDRY.HeaderMain.call(m, MDDRY_TO_MD.HeaderMain, MDDRY_TO_MD.MathSpan), source_text)

    @classmethod
    def MultiLineTables(cls, source_text: str, type_out: Literal['html', 'md']) -> Optional[str]:
        """
        Многострочные таблицы, и обычные
        """
        # TODO: реализовать type_out: Literal['html', 'md']
        if type_out == 'html':
            return REGEX.MultiLineTables.sub(lambda m: GenericMDDRY.MultiLineTables(m, MDDRY_TO_HTML.MultiLineTables),
                                             source_text)
        else:
            return REGEX.MultiLineTables.sub(lambda m: GenericMDDRY.MultiLineTables(m, MDDRY_TO_MD.MultiLineTables),
                                             source_text)


class GenericMDDRY:
    """
    Основной функционал MarkdownDRY, который будет использоваться для конвертации в другие форматы,
    сейчас поддерживаются форматы: `html`, `md`
    """

    @staticmethod
    def BaseCodeRef(m: re.Match, self_path: str) -> Optional[BaseCodeRefReturn]:
        """
        Основная логика ссылок на код
        """
        # Имя ссылки
        name_re: str = m['name']
        # Базовое имя в теле ссылки
        main_re: str = m['main']
        # Уточняющие имя у базового имени
        child_re: str = m['child']
        if not m['path']:
            # Если не указан путь, то выходим
            return None
        # Путь к исходному файлу
        path_re: Path = Path(m['path'])
        # Проверим что это НЕ бинарный файл, путем просмотра расширения файла. Если это бинарный файл, то выходим из функции
        if AvailableLanguages.Binary.value.search(path_re.suffix):
            return None
        # Язык программирования или разметки
        lange_file: Lange = ConvertSuffixToLange.getlang(path_re.suffix)
        # Исходный текст кода
        text_in_file: str
        # Проверяем куда указывает путь, локально или в интернет
        path_or_url = re.match('(https|http|ftp|tcp|localhost):', m['path'])
        if path_or_url:
            """Это ссылку в интернет"""
            logger.debug(m['path'], 'URL')
            # Скачиваем исходный текст из интернета
            text_in_file = requests.get(m['path']).text
        else:
            """Это локальный путь"""
            logger.debug(path_re, 'LOCAL')  # Path(self_path, m['path']).resolve().__str__()
            try:
                # Читаем файл по абсолютному пути
                text_in_file = Path(self_path, path_re).resolve().read_text()
            except FileNotFoundError as e:
                logger.error(f"{path_re}:\n{e}", "LOCAL_BaseCodeRef")
                return None
            except TypeError as e:
                logger.error(f"{path_re}:\n{e}", "LOCAL_BaseCodeRef")
                return None

        # Формируем ссылку, например ей можно использовать для `HTML`
        ref = f"{f'{main_re}' if main_re else ''}{f'.{child_re}' if child_re else ''}"
        # Переменная для указания индекса начало найденного элемента
        line_start = 0
        # Переменная для указания индекса конца найденного элемента
        line_end = -1
        # Переменная для хранения обрезанного текста
        text_in_file_cup: str = text_in_file
        # Если указано, что вставлять, то вставляем этот участок код из файла
        if main_re:
            # Если указывает на класс/функцию/переменную/УникальныйЯкорь
            text_in_file_cup, line_start, line_end = lange_file.REGEX.class_func_var_anchor(main_re, text_in_file)
            if child_re:
                # Если указывает на метод класса/атрибут класса
                text_in_file_cup, tmp_line_start, tmp_line_end = lange_file.REGEX.class_meth_attr(child_re, text_in_file_cup)
                # Конец найденного текста
                line_end = line_start + tmp_line_end if tmp_line_end else 0
                # Начало найденного текст
                line_start = line_start + tmp_line_start if tmp_line_start else 0
        return BaseCodeRefReturn(name_re=name_re,
                                 text_in_file_cup=text_in_file_cup,
                                 text_in_file=text_in_file,
                                 line_start=line_start,
                                 line_end=line_end,
                                 ref=ref,
                                 lange_file=lange_file,
                                 file=path_re)

    @classmethod
    def MathSpan(cls, m: re.Match, body: str = None) -> tuple[str, str]:
        """
        Высчитываем математическое выражение с помощью SymPy, и возвращаем результат выражения

        :param m:
        :param body: Тело математического выражения, это нужно, для того чтобы передавать значения переменных, а не их имена
        """

        """
        Доработать математический размах, сделать подсказку переменной, и её типа,
        добавить возможность самому писать ответ к выражению, но все равно делать
        расчеты для проверки правильности указного ответа, если ответы разные то
        выдавать ошибку сборки!
        """

        text: str = body if body else m['body']
        # Предварительный ответ, который заранее написан в выражение
        preliminary_response: Optional[str] = m['preliminary_response']
        try:
            # Ответ посчитанный SymPy
            res = sympify(text).__str__()
            # Если есть предварительный ответ, и он не равен ответу от `SymPy`
            if preliminary_response and preliminary_response != res:
                # То записываем в лог ошибку и возвращаем выражение с ошибкой в ответе
                logger.error(
                    f"Ожидался ответ={preliminary_response}, но получен={res}.\nВ уравнение: {m.group(0)}.\nВ готовом варианте:{m['preliminary_response']}={body}",
                    "Не равные ответы в `MathSpan`")
                return f'!ERROR!', text
            else:
                return res, text
        except SympifyError:
            logger.error(f"{text}", "MathSpan")
            return '!ERROR!', text

    @staticmethod
    def ReferenceBlock(m: re.Match, call_res: typing.Callable[[re.Match], str]) -> str:
        """Ссылочные блоки"""
        # Заносим найденные ссылочные блоки в общий кеш документа
        StoreDoc.ReferenceBlock[m['ref_block_name']] = m['ref_block_text']
        return call_res(m)

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
    def InsertCodeFromFile(cls, m: re.Match, self_path: str) -> Optional[str]:
        """
        Экранированная вставка текста из файла, в код блок, далее он будет обработан стандартным `Markdown` этапом для код блоков
        """
        res: BaseCodeRefReturn = cls.BaseCodeRef(m, self_path)
        if not res:
            # Если нет ответа то вернем тот же текст
            return m.group(0)
        # TODO: Проработать экранирование спец символов
        return f"{res.name_re}\n```{res.lange_file.name_lange} [{res.name_re}]{{{res.line_start}-{res.line_end}}}\n{res.text_in_file_cup}\n```"

    @classmethod
    def MultiLineTables(cls, m: re.Match, call_res: typing.Callable[[Tables.title, Tables.body], str]) -> str:
        """
        Многостраничная таблица

        :param m:
        :param call_res: Функция форматирования результата таблицы
        """
        text = m.group(0)
        # Формируем таблицу
        tb = Tables(text)
        for _index, _head_table in enumerate(REGEX.MultiLineTablesColumn.finditer(text)):
            tb.addColumn_IfEndThenNewRow(_head_table['column'].rstrip())
        # После вставки всех строк и столбцов, производим конечное преобразование таблицы
        tb.EndBuild()
        # Реализуем логику агрегатных функций и простого обращения к ячейкам. Вызываем у таблицы после `EndBuild` и/или `EndMultiLaneBuild`
        tb.DepLogic()
        # Формируем таблицу через переданную функцию форматирования
        return call_res(tb.title, tb.body)

    class HeaderMain:
        """
        Основная логика заголовков и переменных в MarkdownDRY
        """

        @classmethod
        def call(cls, m: re.Match,
                 call_return: typing.Callable[[int, str, str, str, str], str],
                 call_format_math_span: typing.Callable[[re.Match, str], str]) -> str:
            """
            :param m:
            :param call_return: Функция для формирования результата в нужный формат
            :param call_format_math_span: Функция для формирования результат математического выражения в котором используются переменные


            1. Ищем все заголовки. Нам нужно получить имя заголовка, его уровень, и его тело. После этого проверяем тип заголовка, он
            может быть обычным, а может быть скрытым.

            2. Начинаем поиск инициализируемых переменных, если это простое значение то записываем его в кеш, также возможны случае
            когда в текуще инициализируемой переменной идет обращение к уже ранее созданным переменным, тогда нужно получить
            значение этих переменных из кеша, и записать к текущую инициализируемую переменную, после этого возможно что в
            инициализируемой переменной есть математическое выражение(MathSpan), тогда нам нужно его вычислить, после всех
            проверок записываем имя и значение переменной в `StoreDoc.HeaderMain`

            3. После этого проверяем во всем тексе заголовка обращения к переменным, если есть то тогда проверяем кеш на наличие переменных
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
            # Добавляем заголовок в кеш, получаем уникальный id для заголовка
            name_from_id = StoreDoc.HeaderMain.addHeaders(name_head, level, res_HeadersType)
            #######################################################################################################
            # Поиск инициализации переменных
            body_header = REGEX.VarsInit.sub(lambda _m: cls.vars_init(_m, name_head), body_header)
            # Обрабатываем обращения к переменным которые находятся внутри математического выражения `MathSpan`.
            body_header = REGEX.MathSpan.sub(lambda _m: cls.vars_get_from_math_span(_m, name_head, call_format_math_span),
                                             body_header)
            # Обрабатываем обращения во всем тексе.
            body_header = REGEX.VarsGet.sub(lambda _m: cls.vars_get(_m, name_head), body_header)
            #######################################################################################################

            return call_return(level, name_from_id, res_HeadersTypeHtml, name_head, body_header)

        @staticmethod
        def vars_init(m: re.Match, name_head: str) -> str:
            """
            Поиск инициализации переменных


            Наглядный пример:

            - [=Имя](Иван)
            - [=Фамилия]([=Имя] Иванов)
            - [=Отчество]([=Имя] Иванов Иванович):ТипИмяОтчество

            В итоге `[=Фамилия]` будет равен Иванов Иван
            """
            # Обрабатываем вариант когда при инициализации переменной есть обращение к уже ранее созданным переменным
            _nested_var = REGEX.VarsGet.sub(lambda _n_v:
                                            StoreDoc.HeaderMain.getVar(name_head, _n_v['name'], context=m.group(0))[0],
                                            m['value']
                                            )
            # Переменная с результатом
            res_var: str = _nested_var if _nested_var else m['value']
            # Проврем на возможность наличия в значение математического выражения `MathSpan`
            is_math_span: re.Match = REGEX.MathSpan.match(res_var)
            if is_math_span:
                # Если есть `MathSpan`, то высчитываем выражение.
                res_var = GenericMDDRY.MathSpan(is_math_span)[0]
            # Записываем переменные в кеш заголовка
            StoreDoc.HeaderMain.addVar(name_head, m['name'], res_var, m['type'])
            # Скрываем из выходного текста инициализацию переменных,
            # все данные о переменных теперь хранятся в `StoreDoc.HeaderMain`
            return f"%%{m['name']}={res_var}:{m['type']}%%"

        @staticmethod
        def vars_get_from_math_span(m: re.Match, name_head: str, call_format: typing.Callable[[re.Match, str], str]) -> str:
            """
            Вставка значений в места, где идет обращение к переменным,
            область вставки внутри математического выражению `MathSpan`.
            """

            # Если в математическом выражение нет обращения к переменным, то пропускам такое выражение,
            # его должны обработать отдельно, на этапе `MathSpan`
            if REGEX.VarsGet.search(m['body']):
                res = REGEX.VarsGet.sub(
                    lambda _m: StoreDoc.HeaderMain.getVar(
                        name_head,
                        _m['name'],
                        default=_m.group(0))[0],
                    m['body']
                )
                return call_format(m, res)
            else:
                return m.group(0)

        @staticmethod
        def vars_get(m: re.Match, name_head: str) -> str:
            """
            Вставка значений и тип(переменной) в места, где идет обращение к переменным.
            Область вставки во всем тексе.
            """
            res = StoreDoc.HeaderMain.getVar(name_head, m['name'], default=m.group(0))
            return f"{res[0]}({res[1]})"

    @classmethod
    def ProceduralTemplates(cls, m: re.Match, call_format: typing.Callable[[re.Match], str]) -> str:
        """Процедурные шаблоны, объявление"""
        # Заносим переменные в кеш
        StoreDoc.ProceduralTemplates.addProcedure(
            name_procedure=m['ref_block_name'],
            text_procedure=m['ref_block_text']
        )
        # Ищем объявление переменных
        for x in REGEX.ProceduralTemplatesInitVar.finditer(m['ref_block_text']):
            # Заносим переменные в кеш
            StoreDoc.ProceduralTemplates.addVars(
                name_procedure=m['ref_block_name'],
                name_var=x['name'],
            )
        return call_format(m)

    @classmethod
    def UseProceduralTemplates(cls, m: re.Match, StoreDocs_ProceduralTemplates: StoreDoc.ProceduralTemplates,
                               call_format: typing.Callable[[str], str]):
        """Процедурные шаблоны, использование"""
        # Имя процедуры
        name_procedure: str = m['ref_block_name']
        # Текст процедуры
        res = StoreDocs_ProceduralTemplates.date[name_procedure].text_procedure
        # Ищем обращение к переменным
        for x in REGEX.UseProceduralTemplatesUseVar.finditer(m['ref_block_text']):
            # В тексте процедурного шаблона - заменяем имя переменной(в объявление), на значение переменной(из использования).
            res = res.replace(f'[!{x["name"]}]', x['body'])
        return call_format(res)


class MDDRY_TO_HTML:
    """
    Класс для конвертации MarkdownDRY в HTML
    """

    @staticmethod
    def ReferenceBlock(m: re.Match) -> str:
        """Ссылочные блоки"""
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
    def InsertCodeFromFile(cls, m: re.Match, self_path: str) -> Optional[str]:
        """Вставка кода"""
        res: BaseCodeRefReturn = GenericMDDRY.BaseCodeRef(m, self_path)
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
        res: BaseCodeRefReturn = GenericMDDRY.BaseCodeRef(m, self_path)
        if not res:
            # Если нет ответа то вернем тот же текст
            return m.group(0)
        # Записать в кеш исходный текст из файла
        StoreDoc.LinkCode.add(res.file, HTML_CLASS.ReplaceGtLt(res.text_in_file))
        return f"""
<a href="#" class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.LinkCode.value}" file="{res.file.__str__()}" ref="{res.ref}" char_start="{res.line_start}" char_end="{res.line_end}">{res.name_re}</a>
"""[1:]

    @staticmethod
    def HeaderMain(level: int, name_from_id: str, res_HeadersTypeHtml: str, name_head: str, body_header: str) -> str:
        """Форматирование результата заголовка"""
        return f"""<h{level} id="{name_from_id}" class="{HTML_CLASS.MarkdownDRY.value} {res_HeadersTypeHtml}"><div class="{HTML_CLASS.mddry_name.value}">{name_head}</div><span class="{HTML_CLASS.paragraph.value}">¶</span><div class="{HTML_CLASS.mddry_level.value}">{level}</div></h{level}>\n{body_header}\n"""

    @staticmethod
    def MathSpan(m: re.Match, body: str):
        """
        Форматирование математического выражения

        :param m:
        :param body: Тело математического выражения, это нужно, для того чтобы передавать значения переменных, а не их имена
        """

        text: str = body if body else m['body']
        # Текстовый тип результат математического выражения
        type_math_span: str = m["type"] if m["type"] else ''
        # Информацией о математическом выражение, например из каких переменных состоит математическое выражение
        info = re.sub(':[^ \n.,]+', '', m.group(0)).replace('[=', '[').replace('`', '')
        # Ответ математического выражения выражение
        res_math_span: tuple[str, str] = GenericMDDRY.MathSpan(m, text)
        return f"""<div class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.MathSpanBody.value}">
        {f'<div class="{HTML_CLASS.MathSpanInfo.value}">{info if info else "_" * len(type_math_span)}<div class="{HTML_CLASS.MathSpanType.value}">{type_math_span}</div></div>'}
        <span class="{HTML_CLASS.MathSpan.value}"><span class="{HTML_CLASS.MathResult.value}">{res_math_span[0]}</span>={res_math_span[1]}</span>
        </div>"""

    @classmethod
    def MultiLineTables(cls, title: Tables.title, body: Tables.body) -> str:
        """Многостраничная таблица"""
        return f"""
<div class="{HTML_CLASS.MarkdownDRY.value} {HTML_CLASS.MultiLineTables.value}">
<table>
<thead>
<tr>
{''.join(f'<th>{x}</th>' for x in title)}
</tr>
</thead>
<tbody>
{''.join(f'<tr>{"".join(f"<td>{y}</td>" for y in x)}</tr>' for x in body).replace(f'{REGEX.NL}', "<br>")}
</tbody>
</table>        
</div>
"""[1:]


class MDDRY_TO_MD:
    """
    Класс для конвертации MarkdownDRY в Markdown
    """

    @staticmethod
    def HeaderMain(level: int, name_from_id: str, res_HeadersTypeHtml: str, name_head: str, body_header: str) -> str:
        """Форматирование результата заголовка"""
        return f"""{"#" * level} {'^' if res_HeadersTypeHtml == HeaderType.Hide.value else ''}{name_head}\n{body_header}"""

    @staticmethod
    def ReferenceBlock(m: re.Match) -> str:
        """Ссылочные блоки"""
        # Убрать следы ссылочного блока из обычного `Markdown`
        return ''

    @staticmethod
    def ProceduralTemplates(m: re.Match) -> str:
        """Процедурный шаблон, объявление"""
        # Убрать следы ссылочного блока из обычного `Markdown`
        return ''

    @staticmethod
    def UseProceduralTemplates(res: str) -> str:
        """Процедурный шаблон, использование"""
        # Вернем результат без изменений
        return res

    @classmethod
    def IndisputableInsertCodeFromFile(cls, m: re.Match, self_path: str) -> Optional[str]:
        """Бесспорная вставка кода"""
        return Path(self_path, m['path']).resolve().read_text()

    @staticmethod
    def MathSpan(m: re.Match, body: str = None):
        """
        Форматирование математического выражения
        """
        # Удаляем скобки если они уже были поставлены ранее
        type_res = '(' + re.sub("[()]", '', m['type']) + ')' if m['type'] else ''
        return f"""`{'='.join(GenericMDDRY.MathSpan(m, body=body))}`{type_res}"""

    @classmethod
    def MultiLineTables(cls, title: Tables.title, body: Tables.body) -> str:
        """Многостраничная таблица"""
        return '\n{0}\n'.format(
            ptabel(
                (title, *([y.replace('\n', '<br>').strip() for y in x] for x in body)), junction_char='|', hrules=HEADER
            )
        )
