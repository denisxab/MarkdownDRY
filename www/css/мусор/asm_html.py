"""
Сборщик HTML
"""

import re
from base64 import b64encode
from pathlib import Path
from typing import Optional

import requests


class НезависимыйHTMLФайл:
    """
    Класс для сборки независимого HTML файла
    """

    @classmethod
    def ВставкаCSS_JS_В_HTML_Файл(cls, source_text: str, path: Path) -> tuple[str, Optional[Path]]:
        """
        Вставить CSS и JS который указан в HTML файле.

        :param source_text: Html текст
        :param path: Путь к файлу исходному html файлу, для построения относительных импортов

        :Пример:

        ```py
        <head>
            <link rel="stylesheet" href="../style.min.css">
            <script src="./logic.js" defer></script>
        </head>
        ```
        """
        NL = "\n"

        def _self(m: re.Match):
            nonlocal path
            if m['path_css']:
                m_path: Path = (path / Path(m['path_css'])).resolve()
                suffix: str = m_path.suffix
                if suffix == '.css':
                    return f"""<style>\n{m_path.read_text().replace(NL, '')}\n</style>"""
            elif m['path_js']:
                m_path: Path = (path / Path(m['path_js'])).resolve()
                suffix: str = m_path.suffix
                if suffix == '.js':
                    return f"""<script>\n{re.sub(f"//.+", "", m_path.read_text())}\n</script>"""

            raise ValueError(f"Ни чего не найдено:{m.group(0)}")

        СкрытьКомментарии: re.Pattern = re.compile("""<!--(?:.\s*(?!-->))+.-->""")
        source_text = СкрытьКомментарии.sub('', source_text)
        НайтиCssИлиJS: re.Pattern = re.compile(
            """(<link(?:.(?!href))* +href=\"(?P<path_css>[^\"]+)\"[^>]*>)|(<script +src=\"(?P<path_js>[^\"]+)\"[^>]*></script>)""")
        return НайтиCssИлиJS.sub(_self, source_text), path

    @classmethod
    def СохранитьФотоВ_HTML(cls, source_text: str, path: Path) -> tuple[str, Optional[Path]]:
        """
        Сохранить в HTML файл изображения

        :param source_text: Html текст
        :param path: Путь к файлу исходному html файлу, для построения относительных импортов
        """
        cachy_img: dict[str, str] = {}
        CACHY_IMG_JS: str = "CACHY_IMG_JS"

        def _self(m: re.Match):
            nonlocal path, cachy_img

            if m['path_img']:
                m_path: Path = (path / Path(m['path_img'])).resolve()
                suffix: str = m_path.suffix
                if m_path.exists():
                    # Кодируем фото в base64
                    m_base64: str = b64encode(m_path.read_bytes()).decode('ascii')
                    # Проверяем на формат изображения на то что он допустимый
                    m_type_img: Optional[str] = {
                        "png": "png",
                        "jpeg": "jpeg",
                        "jpg": "jpg",
                        "gif": "gif",
                        "bmp": "bmp",
                        "tiff": "tiff",
                        "icon": "x-icon",
                        "svg": "svg+xml",
                        "webp": "webp",
                        "xxx": "xxx"
                    }.get(suffix[1:], None)
                    if m_type_img:
                        # Сохраняем результат в кеш, который потом вставиться в JS переменную, из которой в потом заполниться тег <img>
                        if not cachy_img.get(m['path_img'], None):
                            cachy_img[(m['path_img'])] = f"data:image/{m_type_img};base64,{m_base64}"
                        return f'''<img class="{CACHY_IMG_JS}" path="{m['path_img']}" src="">'''
                    else:
                        raise KeyError("Не допустимый формат изображения")
                raise FileNotFoundError(f"Файл не найден: {m_path}")
            raise ValueError(f"Ни чего не найдено:{m.group(0)}")

        СсылкаНаФото: re.Pattern = re.compile("<img +src=\"(?P<path_img>[^\"]+)\"[^>]+>")
        _res = (
            f"""
        {СсылкаНаФото.sub(_self, source_text)}
        <script>
            // При запуске странице выводим в тег `img` атрибут `src` изображения из кеша JavaScript, эта 
            // махинация нужна чтобы не хранить дубли фото в html
            const CACHY_IMG_JS={cachy_img}
            document.querySelectorAll('.{CACHY_IMG_JS}').forEach((elm) => {{
                res = elm.attributes['path'].textContent
                elm.attributes['src'].textContent = CACHY_IMG_JS[res]
            }});
        </script>
        """, path
        )
        return _res

    @classmethod
    def Собрать(cls, in_path: str, out_path: str):
        """
        Собрать Независимый HTML Файл

        :param in_path: Путь к исходному HTML файлу
        :param out_path: Путь куда сохранить результат
        """
        p_out_path = Path(out_path).resolve()
        p_in_path = None
        if re.search('https?|localhost', in_path):
            # Скачать из интернета
            # TODO: Это не реализовано
            _res = requests.get(in_path)
            p_text = _res.text
        else:
            # Взять локально
            p_in_path = Path(in_path).resolve()
            p_text = p_in_path.read_text()
            p_in_path = p_in_path.parent

        _res = cls.СохранитьФотоВ_HTML(*cls.ВставкаCSS_JS_В_HTML_Файл(p_text, p_in_path))
        p_out_path.write_text(_res[0])
        return True


if __name__ == '__main__':
    НезависимыйHTMLФайл.Собрать(
        "/media/denis/dd19b13d-bd85-46bb-8db9-5b8f6cf7a825/MyProject/PycharmProjects/MarkdownDRY/core/test/dataset/pub/ParsingToHtml.html",
        "./ParsingToHtml_res.html"
    )
    НезависимыйHTMLФайл.Собрать(
        "/media/denis/dd19b13d-bd85-46bb-8db9-5b8f6cf7a825/MyProject/PycharmProjects/MarkdownDRY/www/css/мусор/test.html",
        "./test_res.html"
    )
