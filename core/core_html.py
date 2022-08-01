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
    LinkCodeWindowButtonTitle = "LinkCodeWindowButtonTitle"
    LinkCodeWindowButtonHide = "LinkCodeWindowButtonHide"
    LinkCodeWindowBody = "LinkCodeWindowBody"
    LinkCodeWindowDet = "LinkCodeWindowDet"
    LinkSourceCode = "LinkSourceCode"
    LinkCodeName = "LinkCodeName"
    MultiLineTables = "MultiLineTables"
    Ol = "Ol"
    Ul = "Ul"
    Hr = 'Hr'
    menu = "menu"
    detail_menu = "detail_menu"
    shot_menu = "shot_menu"
    bt_show_menu = "bt_show_menu"


class HTML_JS:
    """
    JS код для MarkdownDRY
    """
    LinkCode = f"""
function AddEventLinkCode() {{
    /* Добавление обработка нажатий на ссылки */
    
    let elm = document.querySelectorAll(".{HTML_CLASS.MarkdownDRY.value}.{HTML_CLASS.LinkCode.value}");
    elm.forEach((e) => {{
        e.addEventListener("click", () => {{
            DisplayLinkCode(e);
        }});
    }});
}}
AddEventLinkCode();
function DisplayLinkCode(_elem) {{
    /* Показать всплывающие окно с исходным кодом */
    
    // Устанавливаем в заголовок всплывающего окна, название ссылки которая вызвала это окно
    LinkCodeName.textContent=_elem.textContent

    // Получаем элемент в котором будет исходный текст из файла
    let _el = document.querySelector('#{HTML_CLASS.LinkCodeWindowBody.value}')
    const source_text = {HTML_CLASS.LinkSourceCode.value}[_elem.getAttribute('file')]
    if (source_text) {{
        // --- Вставка кода в всплывающие окно --- //
        _el.innerHTML = toTag(source_text, 'code');
        // --- Выделение кода --- //
        const char_start = _elem.getAttribute('char_start');
        const char_end = _elem.getAttribute('char_end');
        if (char_start > 0 && char_end > 0) {{
            // Выделяем текст согласно диапазону из ссылки. Если конечно такой диапазон есть.
            // Его может не быть если ссылка указывает на несуществующий элемент кода.              
            const highlight_text = toTag(toTag(_el.textContent.slice(char_start, char_end), 'span'), 'code', true);
            // Собираем результат, и записываем его в тело всплывающего окна
            _el.innerHTML = `${{toTag(_el.textContent.slice(0, char_start), 'code', null, null, true)}}` +
                `${{highlight_text}}` +
                `${{toTag(_el.textContent.slice(char_end, _el.innerHTML.length), 'code', null, true, null)}}`
        }}
        // ------------------------------------------------------------- //        
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
function toTag(text, tag) {{
    /*Поместить текст в теги*/
    
    let list = [];
    text.split('\\n').forEach(
        (_e) => {{
            list.push(`<${{tag}}>${{_e}}</${{tag}}>`);
        }}
    )
    return list.join('\\n');
}}

function toTag(text, tag, is_skip_first_last) {{
    /*Поместить текст в теги
    
    is_skip_first_last=true - Если нужно пропустить первый и последний тег
    */
    
    let list = [];
    if (!is_skip_first_last) {{
        text.split('\\n').forEach(
            (_e) => {{
                list.push(`<${{tag}}>${{_e}}</${{tag}}>`);
            }}
        )
    }} else {{
        // Если нужно пропустить первый и последний тег
        const tmp = text.split('\\n')
        list.push(tmp[0])
        tmp.slice(1, -1).forEach(
            (_e) => {{
                list.push(`<${{tag}}>${{_e}}</${{tag}}>`);
            }}
        )
        list.push(tmp[tmp.length-1])
    }}
    return list.join('\\n');
}}
function toTag(text, tag, is_skip_first_last, skip_first, skip_last) {{
    /*Поместить текст в теги

    is_skip_first_last=true - Если нужно пропустить первый и последний тег
    */

    let list = [];
    const tmp = text.split('\\n');

    if (!is_skip_first_last) {{
        if (skip_last) {{
            tmp.slice(0, -1).forEach(
                (_e) => {{
                    list.push(`<${{tag}}>${{_e}}</${{tag}}>`);
                }}
            )
            list.push(`<${{tag}}>${{tmp[tmp.length - 1]}}`)
        }} else if (skip_first) {{
            list.push(`</${{tag}}>${{tmp[0]}}`)
            tmp.slice(1, -1).forEach(
                (_e) => {{
                    list.push(`<${{tag}}>${{_e}}</${{tag}}>`);
                }}
            )
        }} else {{
            tmp.forEach(
                (_e) => {{
                    list.push(`<${{tag}}>${{_e}}</${{tag}}>`);
                }}
            )
        }}
    }} else {{
        // Если нужно пропустить первый и последний тег
        list.push(tmp[0])
        tmp.slice(1).forEach(
            (_e) => {{
                list.push(`<${{tag}}>${{_e}}</${{tag}}>`);
            }}
        )
        // list.push(tmp[tmp.length - 1])
    }}
    return list.join('\\n');
}}
function OnHide(_event) {{
    /* Скрыть выплывающие окно при нажатии вне его */
    
    console.log('OnHide');
    if (_event.target.id === '{HTML_CLASS.LinkCodeWindow.value}') {{
        {HTML_CLASS.LinkCodeWindow.value}.style.display = 'none'
    }}
}}
"""
