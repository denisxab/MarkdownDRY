// ---------------------------------------- MAIN --------------------------------- //

// Логика для `Подсказки`
class CLS_mddry_emerge_windows {
    static show_or_hidden() {
        if (getComputedStyle(mddry_emerge_windows).visibility == "hidden") {
            // Показать
            mddry_emerge_windows.style.setProperty("visibility", "visible");
        } else {
            // Скрыть
            mddry_emerge_windows.style.setProperty("visibility", "hidden");
        }
    }
    static hot_key(e) {
        // Скрыть всплывающие окно ALT+R
        if (e.altKey && e.which == 82) {
            this.show_or_hidden();
            return false;
        }
    }
}

// Логика для `Всплывающие окно`
class CLS_mddry_hint {
    static show_or_hidden() {
        if (getComputedStyle(mddry_hint).visibility == "hidden") {
            // Показать
            mddry_hint.style.setProperty("visibility", "visible");
        } else {
            // Скрыть
            mddry_hint.style.setProperty("visibility", "hidden");
        }
    }

    static hot_key(e) {
        // Скрыть всплывающие подсказки ALT+E
        if (e.altKey && e.which == 69) {
            this.show_or_hidden();
            return false;
        }
    }
}

// Логика для  `Оглавление`
class CLS_mddry_menu {
    // Добавить обработчик для  перехода к заголовку по нажатию элемент оглавления.
    static add_handler_on_click_from_header() {
        document.querySelectorAll("#detail_menu li").forEach((e) => {
            e.onclick = () => {
                window.location.href = e.children[0].href;
            };
        });
    }
    // Узнать скрыто ли оглавление
    static show_or_hidden() {
        if (getComputedStyle(detail_menu).display == "none") {
            // Показать оглавление
            detail_menu.style.setProperty("display", "block");
            bt_show_menu.style.setProperty("display", "none");
            mddry_menu.style.setProperty("height", "50%");
        } else {
            // Скрыть оглавление
            detail_menu.style.setProperty("display", "none");
            bt_show_menu.style.setProperty("display", "block");
            mddry_menu.style.setProperty("height", "30px");
        }
    }
    // Горячая клавиша для Скрытия/Показа заголовка ALT+T
    static hot_key(e) {
        if (e.altKey && e.which == 84) {
            this.show_or_hidden();
            return false;
        }
    }
    static init() {
        this.add_handler_on_click_from_header();
    }
}
// ---------------------------------------- END_MAIN --------------------------------- //
// ---------------------------------------- DEV -------------------------------------- //
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
        CLS_mddry_hint.show_or_hidden();
    }
    static mddry_emerge_windows_show_or_hide() {
        CLS_mddry_emerge_windows.show_or_hidden();
    }
    static mddry_hint_inset_text() {
        // Вставить подсказку введенный текст
        mddry_hint_body.innerText = dev_text_hide_mddry_hint.value;
    }
}
// ---------------------------------------- END_DEV ---------------------------------- //
// -------------------------- Инициализация проекта ---------------------------------- //
class InitApp {
    // Обработка горячих клавиш
    static hot_key() {
        // https://snipp.ru/handbk/js-kbd-codes
        document.onkeyup = function () {
            var e = e || window.event;
            CLS_mddry_menu.hot_key(e);
            CLS_mddry_emerge_windows.hot_key(e);
            CLS_mddry_hint.hot_key(e);
        };
    }
    // Инициализация логики компонентов программы
    static init() {
        this.hot_key();
        CLS_mddry_menu.init();
    }
}
InitApp.init();
// ------------------------------------000---------------------------------------------- //
