# TODO: Реализовать конвертацию файла на ``MarkdownDRY` в `HTML`
import re
from hashlib import md5

from bs4 import BeautifulSoup

from core.core_html import html_head, HTML_JS
from core.core_markdown import CoreMarkdown
from core.core_markdown_dry import CoreMarkdownDRY, REGEX


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
            9.  LinkCode - Ссыки на код
            10. MultiPageCode - Многостраничные коды
            11. MultiLineTables - Таблицы

        - `MD`:

            1. Hr - Горизонтальная линия
            2. Ol, Ul - Нумерованный и не нумерованных список

        :return: Собранный HTML
        """
        return f"{html_head}{self.goMDPars(self.goMDDRYPars(self.text_mddry, path))}{HTML_JS.Hotkey.result}"

    def goMDDRYPars(self, text: str, path: str) -> str:
        """Парсинг MDDRY"""
        res = CoreMarkdownDRY.IndisputableInsertCodeFromFile(text, path)
        res = self.ExcludeComment(res)
        res = CoreMarkdownDRY.HeaderMain(res)
        res = CoreMarkdownDRY.ReferenceBlock(res)
        res = CoreMarkdownDRY.MathSpan(res)
        res = CoreMarkdownDRY.DropdownBlock(res)
        res = CoreMarkdownDRY.HighlightBlock(res)
        res = CoreMarkdownDRY.PhotoGallery(res)
        res = CoreMarkdownDRY.InsertCodeFromFile(res, path)
        res = CoreMarkdownDRY.LinkCode(res)
        res = CoreMarkdownDRY.MultiPageCode(res)
        res = CoreMarkdownDRY.MultiLineTables(res)
        return res

    def goMDPars(self, text: str) -> str:
        """Парсинг MD"""
        res = CoreMarkdown.Hr(text)
        res = CoreMarkdown.Ol(res)
        res = CoreMarkdown.Ul(res)
        return res

    def ExcludeComment(self, text: str) -> str:
        """Исключение комментариев из кода"""

        def _self(m: re.Match) -> str:
            _hash = md5(m['body'].encode()).hexdigest()
            self.cache_comment[_hash] = m['body']
            return _hash

        def ExcludePre(text: str) -> str:
            """
            TODO: Оставить текст в теге <pre> без изменений
            """
            return f"<pre>{REGEX.TagPre.sub(_self, text)}</pre>"

        def DeleteComment(text: str) -> str:
            """
            TODO Удалить комментарии `%%Текст%%` из текста
            """
            return text

        soup = BeautifulSoup(text, 'lxml')

        res = ExcludePre(text)
        res = DeleteComment(res)
        return res
