"""
Сборщик HTML
"""

# 1. Вставка JS и CSS из файлов, в HTML

import re
from pathlib import Path


def ВставкаCSS_JS_В_HTML_Файл(source_text: str) -> str:
    # Вставить значение из файлов по указанным путям в HTML
    """
    Пример:

    $$(./ПутьФайлу.css)$$
    $$(./ПутьФайлу.js)$$
    """
    res: str = source_text
    for m in re.finditer("\$\$\(((?:.(?!\)\$\$))+.)\)\$\$", source_text):
        tmp: str = ""
        m_res: str = m.group(1)
        m_path: Path = Path(m_res)
        suffix: str = m_path.suffix
        if suffix == '.css':
            tmp = f"""<style>{m_path.read_text()}</style>"""
        elif suffix == '.js':
            # JS в конец HTML файл, для того чтобы HTML успел прогрузиться паевым
            tmp = f"""<script>{m_path.read_text()}</script>"""
        res = res.replace(m.group(0), tmp)
    return res


if __name__ == '__main__':
    in_path = "./test.html"
    out_path = "./test_2.html"
    text = Path(in_path).resolve().read_text()
    res = ВставкаCSS_JS_В_HTML_Файл(text)
    write_file = Path(out_path).resolve().write_text(res)
