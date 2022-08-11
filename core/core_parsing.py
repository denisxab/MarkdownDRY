# TODO: Реализовать конвертацию файла на ``MarkdownDRY` в `HTML`
import re
from hashlib import md5

from core.core_html import html_head, HTML_JS, HtmlTag, HTML_CLASS
from core.core_markdown import CoreMarkdown
from core.core_markdown_dry import CoreMarkdownDRY, REGEX, StoreDoc


class Parsing:
    """
    Класс для парсинга файлов в формате `mddry` и конвертации их в html
    """
    cache_comment: dict[str, str] = dict()

    def __init__(self, text_mddry: str):
        self.text_mddry: str = text_mddry

    def goPars(self, path: str) -> str:
        """

        Этапы конвертации

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
        return f"{html_head}{self.goEndBuild(self.goMDPars(self.goMDDRYPars(self.text_mddry, path)))}{HTML_JS.Hotkey.result}"

    def goMDDRYPars(self, text: str, path: str) -> str:
        """Парсинг MDDRY"""
        res = CoreMarkdownDRY.IndisputableInsertCodeFromFile(text, path)
        res = self.ExcludeComment(res)
        # TODO: хочу номер заголовка в правом углу
        res = CoreMarkdownDRY.HeaderMain(res)
        res = CoreMarkdownDRY.ReferenceBlock(res)
        res = CoreMarkdownDRY.MathSpan(res)
        res = CoreMarkdownDRY.DropdownBlock(res)
        res = CoreMarkdownDRY.HighlightBlock(res)
        res = CoreMarkdownDRY.PhotoGallery(res)
        res = CoreMarkdownDRY.InsertCodeFromFile(res, path)
        res = CoreMarkdownDRY.LinkCode(res)
        res = CoreMarkdownDRY.MultiPageCode(res)
        # TODO: чето лагает при создание таблиц
        # res = CoreMarkdownDRY.MultiLineTables(res)
        return res

    def goMDPars(self, text: str) -> str:
        """Парсинг MD"""
        res = CoreMarkdown.Hr(text)
        res = CoreMarkdown.Ol(res)
        res = CoreMarkdown.Ul(res)
        res = CoreMarkdown.CodeLine(res)
        return res

    def goEndBuild(self, text: str) -> str:
        """
        Конечный этап сборки

        1. ReturnValuesWereHiddenFromPreTag
        2. ReturnLastInsert
        """

        def ReturnValuesWereHiddenFromPreTag(text_html: str) -> str:
            """
            Вернуть значения, которые были скрыты из тега <pre>
            """
            for k, v in self.cache_comment.items():
                text_html = text_html.replace(k, v)
            return text_html

        def ReturnLastInsert(text_html: str) -> str:
            """
            Вставить значение которые были отложены, сейчас это JS код
            """
            return f"{text_html}{''.join(StoreDoc.LastInsert)}"

        return ReturnLastInsert(ReturnValuesWereHiddenFromPreTag(text))

    def ExcludeComment(self, text: str) -> str:
        """
        Исключение комментариев из кода

        1. ScreeningLt_Gt_Symbol_CodeLine
        2. ExcludePre
        3. DeleteComment
        4. ScreeningLt_Gt_Symbol_ALlText
        """

        def ScreeningLt_Gt_Symbol_CodeLine(text_html: str) -> str:
            """
            Экранировать символьны меньше больше в обратных кавычках `
            :param text_html:
            """
            return re.sub('`.+`', lambda m: HTML_CLASS.ReplaceGtLt(m.group(0)), text_html)

        def ExcludePre(text_html: str) -> str:
            """
            Заменяем текст в теге `<pre>` на хеш сумму данных, а сами данные записывает в `self.cache_comment`,
            в конце компиляции по этому хешу будут вставлены значения.
            """

            def _repl_tag(repl: str, date: str, name_tag: str):
                """Замена данных на хеш, и запись в `self.cache_comment`"""
                # Экранирование больше меньше в тексте тега <pre>
                len_name_tag: int = len(name_tag)
                date = f"<{name_tag}>{HTML_CLASS.ReplaceGtLt(date[len_name_tag + 2:-(len_name_tag + 3)])}</{name_tag}>"
                # Получаем хеш сумму того что получилось
                _hash = md5(date.encode()).hexdigest()
                # Записываем в кеш
                self.cache_comment[_hash] = date
                return repl.format(date=_hash)

            return HtmlTag.SubTag(HtmlTag.ParseTag(text_html, 'pre'), '{date}', text_html, _repl_tag)

        def DeleteComment(text_html: str) -> str:
            """
            Скрыть комментарии `%%Текст%%` из текста
            """
            return REGEX.CommentMD.sub(lambda m: f"""<div hidden="">{m['body']}</div>'""", text_html)

        def ScreeningLt_Gt_Symbol_ALlText(text_html: str) -> str:
            """
            Экранировать символьны меньше больше во всем тексте
            :param text_html:
            :return:
            """
            return HTML_CLASS.ReplaceGtLt(text_html)

        return ScreeningLt_Gt_Symbol_ALlText(DeleteComment(ExcludePre(ScreeningLt_Gt_Symbol_CodeLine(text))))
