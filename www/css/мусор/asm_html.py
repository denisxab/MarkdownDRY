"""
Сборщик HTML
"""

# 1. Вставка JS и CSS из файлов, в HTML
import base64
import re
from pathlib import Path
from typing import Optional


def ВставкаCSS_JS_В_HTML_Файл(source_text: str) -> str:
    """
    Вставить CSS и JS который указан в HTML файле.

    Пример:

    ```py
    <head>
        <link rel="stylesheet" href="../style.min.css">
        <script src="./logic.js" defer></script>
    </head>
    ```
    """

    def _self(m: re.Match):

        if m['path_css']:
            m_path: Path = Path(m['path_css'])
            suffix: str = m_path.suffix
            if suffix == '.css':
                return f"""<style>\n{m_path.read_text()}\n</style>"""
        elif m['path_js']:
            m_path: Path = Path(m['path_js'])
            suffix: str = m_path.suffix
            if suffix == '.js':
                return f"""<script>\n{m_path.read_text()}\n</script>"""

        raise ValueError("Ни чего не найдено")

    СкрытьКомментарии: re.Pattern = re.compile("""<!--(?:.\s*(?!-->))+.-->""")
    source_text = СкрытьКомментарии.sub('', source_text)
    НайтиCssИлиJS: re.Pattern = re.compile(
        """(<link +rel=\"stylesheet\" +href=\"(?P<path_css>[^\"]+)\">)|(<script +src=\"(?P<path_js>[^\"]+)\"[^>]+></script>)""")
    return НайтиCssИлиJS.sub(_self, source_text)


def СохранитьФотоВ_Теле_HTML(source_text: str) -> str:
    def _self(m: re.Match):
        if m['path_img']:
            m_path: Path = Path(m['path_img'])
            suffix: str = m_path.suffix
            # Кодируем фото в base64
            m_base64: str = base64.b64encode(m_path.read_bytes()).decode('ascii')
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
                return f'<img src="data:image/{m_type_img};base64,{m_base64}">'
            else:
                raise KeyError("Не допустимый формат изображения")
        raise ValueError("Ни чего не найдено")

    СсылкаНаФото: re.Pattern = re.compile("<img +src=\"(?P<path_img>[^\"]+)\"[^>]+>")
    return СсылкаНаФото.sub(_self, source_text)


if __name__ == '__main__':
    in_path = "./test.html"
    out_path = "./test_2.html"
    text = Path(in_path).resolve().read_text()
    res = СохранитьФотоВ_Теле_HTML(ВставкаCSS_JS_В_HTML_Файл(text))
    write_file = Path(out_path).resolve().write_text(res)
