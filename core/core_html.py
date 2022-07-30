from enum import Enum

# Стандартный заголовок
html_head: str = """
<head>
    <meta charset="UTF-8">
    <link href="./bootstrap-5.1.3-dist/main.css" rel="stylesheet">
    <script src="./bootstrap-5.1.3-dist/main.js"></script>
    <link rel="stylesheet" href="./main.min.css">
    <link rel="stylesheet" href="./plugin.css">
</head>
"""[1:]


class HTML_CLASS(Enum):
    """
    Класс для HTML хранения классов
    """
    MarkdownDRY = 'MarkdownDRY'
    InReferenceBlock = 'InReferenceBlock'
    DropdownBlock = "DropdownBlock"
    DropdownBlockTitle = "DropdownBlockTitle"
    DropdownBlockText = "DropdownBlockText"
    HighlightBlock = "HighlightBlock"
    HighlightBlock1 = "HighlightBlock1"
    HighlightBlock2 = "HighlightBlock2"
    HighlightBlock3 = "HighlightBlock3"
    HighlightTitle = "HighlightTitle"
    HighlightBody = "HighlightBody"
    PhotoGallery = "PhotoGallery"
    PhotoGalleryBody = "PhotoGalleryBody"
    MultiPageCode = 'MultiPageCode'
    MathSpan = "MathSpan"
    HiddenHeaders = "HiddenHeaders"
    StandardHeaders = "StandardHeaders"
    InsertCodeFromFile = 'InsertCodeFromFile'
    LinkCode = "LinkCode"
    LinkCodeSourceCode = "LinkCodeSourceCode"
    LinkCodeWindow = "LinkCodeWindow"
    LinkCodeWindowButtonHide = "LinkCodeWindowButtonHide"
    LinkCodeWindowBody = "LinkCodeWindowBody"
    LinkCodeWindowDet = "LinkCodeWindowDet"
    LinkSourceCode = "LinkSourceCode"
    MultiLineTables = "MultiLineTables"
    Ol = "Ol"
    Ul = "Ul"
    Hr = 'Hr'
    menu = "menu"
    detail_menu = "detail_menu"
    shot_menu = "shot_menu"
    bt_show_menu = "bt_show_menu"


html_js: str = f"""
function AddEventLinkCode() {{
    // Добавление обработка нажатий на ссылки
    const elm = document.querySelectorAll(".{HTML_CLASS.MarkdownDRY.value}.{HTML_CLASS.LinkCode.value}");
    elm.forEach((e) => {{
        e.addEventListener("click", () => {{
            DisplayLinkCode(e);
        }});
    }});
}}

function DisplayLinkCode(_elem) {{
    /* Показать всплывающие окно с исходным кодом */
    // Получаем элемент в котором будет исходный текст из файла
    _el = document.querySelector('#{HTML_CLASS.LinkCodeWindowBody.value}')
    source_text = {HTML_CLASS.LinkSourceCode.value}[_elem.getAttribute('file')]
    if (source_text) {{
        // --- Вставка кода в всплывающие окно --- //
        _el.innerHTML = toCode(source_text, 'code');
        // --- Выделение кода --- //
        char_start = _elem.getAttribute('char_start');
        char_end = _elem.getAttribute('char_end');
        if (char_start > 0 && char_end > 0) {{
            // Выделяем текст согласно диапазону из ссылки. Если конечно такой диапазон есть.
            // Его может не быть если ссылка указывает на несуществующий элемент кода.
            highlight_text = toCode(toCode(_el.textContent.slice(char_start, char_end), 'span'), 'code');
            // Собираем результат, и записываем его в тело всплывающего окна
            _el.innerHTML = `${{toCode(_el.textContent.slice(0, char_start), 'code')}}` +
                `\\n${{highlight_text}}\\n` +
                `${{toCode(_el.textContent.slice(char_end, _el.innerHTML.length), 'code')}}`
        }}
        // --- --- //
    }}
    // Делаем видимым окно
    {HTML_CLASS.LinkCodeWindow.value}.style.display = 'block';
    // Перебираем все строки и ищем начало выделение кода
    for (let _e of _el.childNodes) {{
        if (_e.childNodes.length > 0 && _e.childNodes[0].tagName === "SPAN") {{
            // Плавная прокрутка к первому выделенному блоку
            _e.scrollIntoView({{ behavior: 'smooth'}});
            break;
        }}
    }}
}}

function toCode(inText, tag) {{
    text = [];
    inText.split('\\n').forEach(
        (_e) => {{
            text.push(`<${{tag}}>${{_e}}</${{tag}}>`);
        }}
    )
    return text.join('\\n');
}}

AddEventLinkCode();

function OnHide(_event) {{
    /* Скрыть выплывающие окно при нажатии вне его */
    console.log(_event.target);
    if (_event.target.id === '{HTML_CLASS.LinkCodeWindow.value}') {{
        {HTML_CLASS.LinkCodeWindow.value}.style.display = 'none'

    }}
}}
"""
