class CLS_mddry_emerge_windows {
    // Логика для Всплывающей подсказки
    static show_or_hide() {
        if (mddry_emerge_windows.style.visibility == "hidden") {
            // Показать
            mddry_emerge_windows.style.visibility = "visible";
        } else {
            // Скрыть
            mddry_emerge_windows.style.visibility = "hidden";
        }
    }
}
class CLS_mddry_hint {
    // Логика для Блок с подсказкой
    static show_or_hide() {
        if (mddry_hint.style.visibility == "hidden") {
            // Показать
            mddry_hint.style.visibility = "visible";
        } else {
            // Скрыть
            mddry_hint.style.visibility = "hidden";
        }
    }
}

class CLS_mddry_menu {
    // Скрыть оглавление
    static hidden() {
        detail_menu.style.display = "none";
        bt_show_menu.style.display = "block";
    }
    // Показать оглавление
    static show() {
        detail_menu.style.display = "block";
        bt_show_menu.style.display = "none";
    }
    // Добавить обработчик для  перехода к заголовку по нажатию элемент оглавления.
    static add_handler_on_click_from_header() {
        document.querySelectorAll("#detail_menu li").forEach((e) => {
            e.onclick = () => {
                window.location.href = e.children[0].href;
            };
        });
    }
    // Узнать скрыто ли оглавление
    static is_hidden() {
        if (detail_menu.style.display == "none") {
            return false;
        } else {
            return true;
        }
    }
    // Горячая клавиша для Скрытия/Показа заголовка ALT+T
    static hot_key(e) {
        if (e.altKey && e.which == 84) {
            if (CLS_mddry_menu.is_hidden() === false) {
                CLS_mddry_menu.show();
            } else {
                CLS_mddry_menu.hidden();
            }
            return false;
        }
    }
    static init() {
        this.add_handler_on_click_from_header();
    }
}

class DevLogic {
    // Логика для отладки программы
    static show_or_hide_dev() {
        // Показать скрыть команды для отладки
        if (debug_body.style.display == "none") {
            debug_body.style.display = "block";
        } else {
            debug_body.style.display = "none";
        }
    }
    static mddry_hint_show_or_hide() {
        CLS_mddry_hint.show_or_hide();
    }
    static mddry_emerge_windows_show_or_hide() {
        CLS_mddry_emerge_windows.show_or_hide();
    }
    static mddry_hint_inset_text() {
        // Вставить подсказку введенный текст
        mddry_hint_body.innerText = dev_text_hide_mddry_hint.value;
    }
}
class InitAppp {
    // Обработка горячих клавиш
    static hot_key() {
        // https://snipp.ru/handbk/js-kbd-codes
        document.onkeyup = function () {
            var e = e || window.event;
            CLS_mddry_menu.hot_key(e);
        };
    }
    // Инициализация программы
    static init() {
        this.hot_key();
        CLS_mddry_menu.init();
    }
}
InitAppp.init();
