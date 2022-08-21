# TODO: Реализовать конвертацию файла на ``MarkdownDRY` в `HTML`

from abc import abstractmethod
from hashlib import md5
from typing import Literal

from core.core_html import html_head, HTML_JS, HtmlTag, HTML_CLASS
from core.core_markdown import CoreMarkdown
from core.core_markdown_dry import CoreMarkdownDRY, REGEX, StoreDoc


class ParsingBase:
    """
    Базовый класс для парсинга MarkdownDRY
    """
    #: Хранение комментариев
    cache_comment: dict[str, str] = dict()

    def __init__(self, text_mddry: str):
        self.text_mddry: str = text_mddry

    def goMDDRYPars(self, text: str, path: str, type_out: Literal['html', 'md']) -> str:
        """Парсинг MDDRY"""
        res = CoreMarkdownDRY.IndisputableInsertCodeFromFile(text, path)
        res = self.ExcludeComment(res, type_out)
        res = CoreMarkdownDRY.HeaderMain(res, type_out)
        # ------
        res = CoreMarkdownDRY.ReferenceBlock(res, type_out)
        res = CoreMarkdownDRY.MathSpan(res, type_out)
        res = CoreMarkdownDRY.DropdownBlock(res, type_out)
        res = CoreMarkdownDRY.HighlightBlock(res, type_out)
        res = CoreMarkdownDRY.PhotoGallery(res, type_out)
        res = CoreMarkdownDRY.InsertCodeFromFile(res, path, type_out)
        res = CoreMarkdownDRY.LinkCode(res, path, type_out)
        res = CoreMarkdownDRY.MultiPageCode(res, type_out)
        res = CoreMarkdownDRY.MultiLineTables(res, type_out)
        return res

    @staticmethod
    def goMDPars(text: str) -> str:
        """Парсинг MD"""
        res = CoreMarkdown.Hr(text)
        res = CoreMarkdown.Ol(res)
        res = CoreMarkdown.Ul(res)
        # TODO: Добавить тесты для CodeLine
        res = CoreMarkdown.CodeLine(res)
        # TODO: Добавить тесты для CodeBlock
        res = CoreMarkdown.CodeBlock(res)
        # TODO: Добавить тесты для ImageMd
        res = CoreMarkdown.ImgMd(res)
        # TODO: Реализовать вспомогательный текст (символ `> ` в начале строки)
        return res

    @staticmethod
    def _ReturnLastInsert() -> str:
        """
        Вернуть значение которые были отложены для вставки, сейчас это JS код.
        Это нужно для того чтобы не было экранирования JS кода при парсинге
        """
        return ''.join(StoreDoc.LastInsert)

    def _ReturnValuesWereHiddenFromPreTag(self, text_html: str) -> str:
        """
        Вернуть значения, которые были скрыты из тега <pre>
        """
        for k, v in self.cache_comment.items():
            text_html = text_html.replace(k, v)
        return text_html

    def ExcludeComment(self, text: str, type_out: Literal['html', 'md']) -> str:
        """
        Исключение комментариев из кода

        1. ScreeningLt_Gt_Symbol_CodeLine
        2. ExcludePre
        3. ScreeningLt_Gt_Symbol_ALlText
        4. DeleteComment
        """

        def _ScreeningLt_Gt_Symbol_CodeLine(text_html: str) -> str:
            """
            Экранировать символьны меньше и больше, которые находятся в обратных кавычках(`)
            """
            return REGEX.CodeLine.sub(lambda m: HTML_CLASS.ReplaceGtLt(m.group(0)), text_html)

        def _ExcludePre(text_html: str) -> str:
            """
            Заменяем текст в теге `<pre>` на хеш сумму данных, а сами данные записывает в `self.cache_comment`,
            в конце компиляции по этому хешу будут вставлены значения.

            Это нужно чтобы текст в теге `<pre>` не обрабатывался компилятором
            """

            def repl_tag(repl: str, date: str, name_tag: str):
                """Замена данных на хеш, и запись в `self.cache_comment`"""
                # Экранирование больше меньше в тексте тега <pre>
                len_name_tag: int = len(name_tag)
                date = f"<{name_tag}>{HTML_CLASS.ReplaceGtLt(date[len_name_tag + 2:-(len_name_tag + 3)])}</{name_tag}>"
                # Получаем хеш сумму того что получилось
                _hash = md5(date.encode()).hexdigest()
                # Записываем в кеш
                self.cache_comment[_hash] = date
                return repl.format(date=_hash)

            return HtmlTag.SubTag(HtmlTag.ParseTag(text_html, 'pre'), '{date}', text_html, repl_tag)

        def _DeleteComment(text_html: str) -> str:
            """
            Скрыть комментарии `%%Текст%%` из текста
            """
            return REGEX.CommentMD.sub(lambda m: f"""<div hidden="">{m['body']}</div>""", text_html)

        def _ScreeningLt_Gt_Symbol_ALlText(text_html: str) -> str:
            """
            Экранировать символьны меньше больше во всем тексте
            """
            return HTML_CLASS.ReplaceGtLt(text_html)

        return _DeleteComment(_ScreeningLt_Gt_Symbol_ALlText(_ExcludePre(_ScreeningLt_Gt_Symbol_CodeLine(text))))

    # ---------------------------------------------#

    @abstractmethod
    def goPars(self, path: str) -> str:
        """
        Этапы конвертации
        """
        ...

    @abstractmethod
    def goEndBuild(self, text: str) -> str:
        """
        Конечный этап сборки
        """
        ...
    # ---------------------------------------------#


class ParsingToHtml(ParsingBase):
    """
    Класс для парсинга файлов в формате `mddry` и конвертации их в html
    """

    def goPars(self, path: str) -> str:
        """

        Этапы конвертации в HTML

        - `MDDRY`:

            1.  IndisputableInsertCodeFromFile - Бесспорная вставка
            2.  HeaderMain - найти заголовки, инициализировать переменные, вставить значения в места обращения к переменным.
            3.  ReferenceBlock, UseReferenceBlock - Инициализация и сборка ссылочных блоков.
            4.  MathSpan - Математический размах
            5.  DropdownBlock - Раскрываемые блоки
            6.  HighlightBlock - Выделение
            7.  PhotoGallery - Фотогалерея
            8.  InsertCodeFromFile - Сначала вставляем в текст данные из других файлов.
            9.  LinkCode - Ссылки на код
            10. MultiPageCode - Многостраничные коды
            11. MultiLineTables - Таблицы

        - `MD`:

            1. Hr - Горизонтальная линия
            2. Ol, Ul - Нумерованный и не нумерованных список
            3. CodeLine - Строка с кодом


        :return: Собранный HTML
        """
        # TODO: Сделать два этапа сборки. MDDRY в MD, и MDDRY в HTML. Например, для того чтобы можно было использовать только
        #  переменные и бесспорные вставки и Математический размах и агрегатные функции в таблицах в MD файлах.
        return self.goEndBuild(self.goMDPars(self.goMDDRYPars(self.text_mddry, path, 'html')))

    def goEndBuild(self, text: str) -> str:
        """
        Конечный этап сборки

        1. ReturnValuesWereHiddenFromPreTag
        2. ReturnLastInsert
        """
        return f'{html_head}{self._ReturnValuesWereHiddenFromPreTag(f"{text}{self._ReturnLastInsert()}")}{HTML_JS.Hotkey.result}'


class ParsingToMarkdown(ParsingBase):
    """
    Класс для парсинга файлов в формате `mddry` и конвертации их в стандартный Markdown
    """

    def goPars(self, path: str) -> str:
        """
        Этапы конвертации
        """
        return self.goEndBuild(self.goMDPars(self.goMDDRYPars(self.text_mddry, path, 'md')))

    def goEndBuild(self, text: str) -> str:
        """
        Конечный этап сборки
        """
        return self._ReturnValuesWereHiddenFromPreTag(text)
