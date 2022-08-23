import pathlib
import re
from typing import Optional

from logsmal import logger

from core.core_html import HTML_CLASS
from core.core_lang import AvailableLanguages
from core.core_markdown_dry import REGEX, MDDRY_TO_HTML


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
        """Горизонтальная линия"""
        return '<hr>'

    @staticmethod
    def CodeLine(m: re.Match) -> str:
        """Строка с кодом"""
        return f'<span class="{HTML_CLASS.CodeLine.value}">{m["body"]}</span>'

    @staticmethod
    def CodeBlock(m: re.Match) -> str:
        """Блок с кодом"""
        body_code: list[str] = []
        for index, lange, line_code, info in MDDRY_TO_HTML.PageCode(m.group(0), REGEX.CodeBlock):
            body_code.append(f"""
<div class="{HTML_CLASS.CodeBlock.value}">
{f'<div class="{HTML_CLASS.head.value}">{info}</div>' if info else ''}
<div>
<pre class="{HTML_CLASS.code.value} {lange}">
{HTML_CLASS.toCode(line_code)}
</pre>
</div>
</div>    
        """[1:])
        return ''.join(body_code)

    @staticmethod
    def ImgMd(m: re.Match) -> str:
        """
        Изображение
        """
        # Описание фото
        name: str = m['name']
        # Путь к исходному файлу
        path_re: pathlib.Path = pathlib.Path(m['path'])
        # Проверим что это ЕСТЬ бинарный файл, путем просмотра расширения файла. Если это НЕ бинарный файл, то выходим из функции
        if not AvailableLanguages.Binary.value.search(path_re.suffix):
            return m.group(0)
        return f'<div class="{HTML_CLASS.ImgMd.value}"><img src="{path_re.__str__()}" alt="{HTML_CLASS.ScreeningId(name)}"><div class="{HTML_CLASS.ImgMdName.value}">{name}</div></div>'

    @staticmethod
    def Br(m: re.Match) -> str:
        return '\n<br>' * len(m.group(0))


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
        logger.debug('Ul')
        return REGEX.BaseBlockUl_or_Ol.sub(MD_TO_HTML.Ul, source_text)

    @classmethod
    def Ol(cls, source_text: str) -> Optional[str]:
        """
        Нумерованный Список
        """
        logger.debug('Ol')
        return REGEX.BaseBlockUl_or_Ol.sub(MD_TO_HTML.Ol, source_text)

    @classmethod
    def Hr(cls, source_text: str) -> Optional[str]:
        """
        Горизонтальная линия
        """
        logger.debug('Hr')
        return REGEX.Hr.sub(MD_TO_HTML.Hr, source_text)

    @classmethod
    def CodeLine(cls, source_text: str) -> Optional[str]:
        """
        Строка с кодом
        """
        logger.debug('Code')
        return REGEX.CodeLine.sub(MD_TO_HTML.CodeLine, source_text)

    @classmethod
    def CodeBlock(cls, source_text: str) -> Optional[str]:
        """
        Блок с кодом
        """
        logger.debug('CodeBlock')
        return REGEX.CodeBlock.sub(MD_TO_HTML.CodeBlock, source_text)

    @classmethod
    def ImgMd(cls, source_text: str) -> Optional[str]:
        """
        Изображение
        """
        logger.debug('ImgMd')
        return REGEX.ImgMd.sub(MD_TO_HTML.ImgMd, source_text)

    @classmethod
    def Br(cls, source_text: str) -> Optional[str]:
        """
        Вставить тег <br> если есть два переноса
        """
        logger.debug('Br')
        return REGEX.Br.sub(MD_TO_HTML.Br, source_text)
