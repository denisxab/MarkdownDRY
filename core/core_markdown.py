import re
from typing import Optional

from logsmal import logger

from core.core_html import HTML_CLASS
from core.core_markdown_dry import REGEX


class MD_TO_HTML:
    """
    Конвертация Markdown в HTML
    """

    @staticmethod
    def Ul(m: re.Match) -> str:
        """Ссылочные блоки"""
        trigger = False

        def _self(_m: re.Match):
            nonlocal trigger
            trigger = True
            return f'<li>{_m["ul"]}</li>'

        res = REGEX.Ul.sub(_self, m.group(0))
        if trigger:
            return f'<ul class="{HTML_CLASS.MarkdownDRY} {HTML_CLASS.Ul}">{res}</ul>'
        else:
            return m.group(0)

    @staticmethod
    def Ol(m: re.Match) -> str:
        """Ссылочные блоки"""
        trigger = False

        def _self(_m: re.Match):
            nonlocal trigger
            trigger = True
            return f'<li>{_m["ol"]}</li>'

        res = REGEX.Ol.sub(_self, m.group(0))
        if trigger:
            return f'<ol class="{HTML_CLASS.MarkdownDRY} {HTML_CLASS.Ol}">{res}</ol>'
        else:
            return m.group(0)

    @staticmethod
    def Hr(m: re.Match) -> str:
        return '<hr>'


class CoreMarkdown:
    """
    Стандартные возможности:

    - Заголовки - реализовано в CoreMarkdownDRY.HeaderMain
    - Таблицы - реализовано в CoreMarkdownDRY.MultiLineTables
    - Не нумерованный Список - CoreMarkdown.Ul
    - Нумерованный Список - CoreMarkdown.Ol
    """

    @classmethod
    def Ul(cls, source_text: str) -> Optional[str]:
        """
        Не нумерованный Список
        """
        logger.debug(source_text, 'Ul')
        return REGEX.BaseBlockUl_or_Ol.sub(MD_TO_HTML.Ul, source_text)

    @classmethod
    def Ol(cls, source_text: str) -> Optional[str]:
        """
        Нумерованный Список
        """
        logger.debug(source_text, 'Ol')
        return REGEX.BaseBlockUl_or_Ol.sub(MD_TO_HTML.Ol, source_text)

    @classmethod
    def Hr(cls, source_text: str) -> Optional[str]:
        """
        Горизонтальная линия
        """
        logger.debug(source_text, 'Hr')
        return REGEX.Hr.sub(MD_TO_HTML.Hr, source_text)
