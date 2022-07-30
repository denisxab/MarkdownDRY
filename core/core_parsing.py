# TODO: Реализовать конвертацию файла на ``MarkdownDRY` в `HTML`
from core.core_markdown import CoreMarkdown
from core.core_markdown_dry import CoreMarkdownDRY


class Parsing:
    """
    Класс для парсинга файлов в формате `mddry` и конвертации их в html
    """

    def __init__(self, text_mddry: str):
        self.text_mddry: str = text_mddry

    def goPars(self) -> str:
        """

        Этапы конвертации
        1. HeaderMain - найти заголовки, инициализировать переменные, вставить значения в места обращения к переменным.
        2. ReferenceBlock, UseReferenceBlock - Инициализация и сборка ссылочных блоков.

        :return: Собранный HTML
        """

        return self.goMDPars(self.goMDDRYPars(self.text_mddry))

    def goMDDRYPars(self, text: str) -> str:
        res = CoreMarkdownDRY.HeaderMain(text)
        res = CoreMarkdownDRY.ReferenceBlock(res)
        res = CoreMarkdownDRY.UseReferenceBlock(res)
        res = CoreMarkdownDRY.DropdownBlock(res)
        res = CoreMarkdownDRY.HighlightBlock(res)
        res = CoreMarkdownDRY.PhotoGallery(res)
        res = CoreMarkdownDRY.MathSpan(res)
        return res

    def goMDPars(self, text: str) -> str:
        res = CoreMarkdown.Hr(text)
        res = CoreMarkdown.Ol(res)
        res = CoreMarkdown.Ul(res)
        return res

    def ExcludePre(self) -> str:
        """
        TODO: Оставить текст в теге <pre> без изменений
        """
        ...

    def DeleteComment(self) -> str:
        """
        TODO Удалить комментарии `%%Текст%%` из текста
        """
        ...
