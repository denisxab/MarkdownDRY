from enum import Enum

# Стандартный заголовок
html_head: str = """
<head>
    <meta charset="UTF-8">
    <link href="../../../../../www/css/bootstrap-5.1.3-dist/main.css" rel="stylesheet">
    <script src="../../../../../www/css/bootstrap-5.1.3-dist/main.js"></script>
    <link rel="stylesheet" href="../../../../../www/css/main.min.css">
    <link rel="stylesheet" href="../../../../../www/css/plugin.css">
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
    LinkCodeWindowFooter = "LinkCodeWindowFooter"
    LinkCodeWindowDet = "LinkCodeWindowDet"
    LinkCodeWindowPath = "LinkCodeWindowPath"
    LinkSourceCode = "LinkSourceCode"
    LinkCodeName = "LinkCodeName"
    MultiLineTables = "MultiLineTables"
    Ol = "Ol"
    Ul = "Ul"
    Hr = 'Hr'
    code="code"
    menu = "menu"
    detail_menu = "detail_menu"
    shot_menu = "shot_menu"
    bt_show_menu = "bt_show_menu"
    bt_hidden_menu = "bt_hidden_menu"

    @staticmethod
    def toCode(text: str) -> str:
        """Конвертировать текст в вид для нумерованного кода"""
        return ''.join(f'<code>{x}</code>\n' for x in text.split('\n'))


class HTML_JS:
    """
    JS код для MarkdownDRY
    """

    class Hotkey:
        """
        Комбинации клавиш для различных фич. Вставлять нужно собранные `result`

        - `ALT+T` - Скрыть/Показать оглавление

        """

        HeaderMain = f"""
if (e.altKey && e.which == 84) {{
    if ({HTML_CLASS.menu.value}_is_hidden() === false) {{
        {HTML_CLASS.menu.value}_show();
    }} else {{
        {HTML_CLASS.menu.value}_hidden();
    }}
    return false;
}}
"""[1:]
        result = f"""
<script>
// https://snipp.ru/handbk/js-kbd-codes
document.onkeyup = function () {{
    var e = e || window.event;
    {HeaderMain}
}}
</script>
"""[1:]

    HeaderMain = f"""
function {HTML_CLASS.menu.value}_hidden(){{
    // Скрыть оглавление
    {HTML_CLASS.detail_menu.value}.hidden=false;
    {HTML_CLASS.bt_show_menu.value}.hidden=true;
    {HTML_CLASS.bt_hidden_menu.value}.hidden=false;
    {HTML_CLASS.menu.value}.style.height='50%';
}}
function {HTML_CLASS.menu.value}_show(){{
    // Показать оглавление
   {HTML_CLASS.detail_menu.value}.hidden=true;
   {HTML_CLASS.bt_show_menu.value}.hidden=false;
   {HTML_CLASS.bt_hidden_menu.value}.hidden=true;
   {HTML_CLASS.menu.value}.style.height='50px';
}}
function {HTML_CLASS.menu.value}_is_hidden(){{
    // Узнать скрыто ли оглавление
    return {HTML_CLASS.detail_menu.value}.hidden
}}
// Изначально скрываем кнопку показа оглавления
{HTML_CLASS.bt_show_menu.value}.hidden = true;
(function (){{
    // Переход к заголовку по нажатию элемент оглавления.        
    document.querySelectorAll("#detail_menu li").forEach((e) => {{
        e.onclick = ()=>{{
          window.location.href  = e.children[0].href
        }}
      }}
    );
}})()
"""[1:]
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
    
    // Установить путь к файлу или ссылку в выплывающие окно
    LinkCodeWindowPath.textContent=_elem.getAttribute('file')

    // Получаем элемент в котором будет исходный текст из файла
    let _el = document.querySelector('#{HTML_CLASS.LinkCodeWindowBody.value}')
    const source_text = {HTML_CLASS.LinkSourceCode.value}[_elem.getAttribute('file')]
    if (source_text) {{
        // --- Вставка кода в всплывающие окно --- //
        _el.innerHTML = toTag(source_text, 'code', 0, 0, 0, true);
        // --- Выделение кода --- //
        const char_start = _elem.getAttribute('char_start');
        const char_end = _elem.getAttribute('char_end');
        if (char_start > 0 && char_end > 0) {{
            // Выделяем текст согласно диапазону из ссылки. Если конечно такой диапазон есть.
            // Его может не быть если ссылка указывает на несуществующий элемент кода.              
            const highlight_text = toTag(toTag(_el.textContent.slice(char_start, char_end), 'span', 0, 0, 0, true), 'code', true);
            // Собираем результат, и записываем его в тело всплывающего окна
            _el.innerHTML = `${{toTag(_el.textContent.slice(0, char_start), 'code', null, null, true, true)}}` +
                `${{highlight_text}}` +
                `${{toTag(_el.textContent.slice(char_end, _el.innerHTML.length), 'code', null, true, null, true)}}`
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
function toTag(text, tag, is_skip_first_last, skip_first, skip_last, escaping) {{
    /*Поместить текст в теги

    is_skip_first_last=true - Если нужно пропустить первый и последний тег.
    escaping=true -  Экранирование треугольных скобок, если этого не сделать то метод `innerHTML` скроет текст в скобках.
    */

    let list = [];
    if (escaping) {{
        text = text.replace(/</g,'&lt').replace(/>/g,'&gt');
    }}
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
"""[1:]
