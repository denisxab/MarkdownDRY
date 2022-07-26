// ---------------------------------------- MAIN --------------------------------- //

// Логика для `Подсказки`
class CLS_mddry_emerge_windows {
	static show_or_hidden() {
		if (getComputedStyle(mddry_emerge_windows).visibility == "hidden") {
			// Показать
			mddry_emerge_windows.style.setProperty("visibility", "visible");
			mddry_emerge_windows.style.setProperty("opacity", "1");
		} else {
			// Скрыть
			mddry_emerge_windows.style.setProperty("opacity", "0");
			// Скрыть отображение заголовков, после скрытия меню
			setTimeout(function () {
				mddry_emerge_windows.style.setProperty("visibility", "hidden");
			}, 300);
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
		if (mddry_hint.getAttribute("show") == "0") {
			// Показать
			mddry_hint.style.setProperty("visibility", "visible");
			mddry_hint.style.setProperty("height", "100%");
			mddry_hint.setAttribute("show", "1");
		} else {
			// Скрыть
			mddry_hint.style.setProperty("visibility", "hidden");
			mddry_hint.style.setProperty("height", "0%");
			mddry_hint.setAttribute("show", "0");
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
		if (getComputedStyle(bt_hidden_menu).display == "none") {
			// Показать оглавление
			detail_menu.style.setProperty("display", "block");
			bt_show_menu.style.setProperty("display", "none");
			bt_hidden_menu.style.setProperty("display", "block");
			mddry_menu.style.setProperty("height", "35%");
			mddry_menu.style.setProperty("width", "100%");
		} else {
			// Скрыть оглавление
			bt_show_menu.style.setProperty("display", "block");
			bt_hidden_menu.style.setProperty("display", "none");
			mddry_menu.style.setProperty("height", "20px");
			mddry_menu.style.setProperty("width", "120px");
			// Скрыть отображение заголовков, после скрытия меню
			setTimeout(function () {
				detail_menu.style.setProperty("display", "none");
			}, 300);
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

// Логика для работы галериеи

class Gallery {
	// Получить текущий элемент, и скрыть его
	static _select_items(elm) {
		// Получем галерею со всеми элементами
		let e_parent = elm.parentNode;
		// Сколько всего элюентов в галерией
		let max_len = e_parent.querySelectorAll("img").length - 1;
		// Находим индекс выбранного элемента
		let select_index = 0;
		for (let e0 of e_parent.querySelectorAll("img")) {
			if (e0.getAttribute("select") === "1") {
				// Скрываем текущий элемент
				e0.setAttribute("select", "0");
				break;
			}
			select_index += 1;
		}
		return [select_index, max_len, e_parent];
	}
	// Переключить на предыдущий элемент
	static last_page(elm) {
		let [select_index, max_len, e_parent] = this._select_items(elm);
		// Высчитываем предыдущий элемент
		let next_page = undefined;
		if (select_index === 0) {
			next_page = max_len;
		} else {
			next_page = select_index - 1;
		}
		// Показываем предыдущий элемент
		e_parent.querySelectorAll("img")[next_page].setAttribute("select", "1");
	}
	// Переключить на следующий элемент
	static next_page(elm) {
		let [select_index, max_len, e_parent] = this._select_items(elm);
		// Высчитываем следующий элемент
		let next_page = undefined;
		if (select_index === max_len) {
			next_page = 0;
		} else {
			next_page = select_index + 1;
		}
		// Показываем следующий элемент
		e_parent.querySelectorAll("img")[next_page].setAttribute("select", "1");
	}
	// Перелистывания фото на мобильных устройствах
	static touch_move() {
		//!! Это распространяется на галерии !!! сделать для всех галерей !!!
		let q = document.querySelector(".Gallery");
		// Выбранное фото
		let elm = q.querySelector('img[select="1"]');
		// Получаем ширину выбранного фото
		let doorstep = elm.width / 3;
		console.log(doorstep);
		// Старт перемещения пальца
		let pos_start = 0;
		// Сколько пройдено пальцем
		let dif = 0;
		let is_start = false;
		// Обрабатываем начало перемещения
		q.addEventListener("touchstart", (e) => {
			pos_start = e.targetTouches[0].clientX;
			is_start = true;
		});
		// Обработка перемещения пальца
		q.addEventListener("touchmove", (e) => {
			dif = e.targetTouches[0].clientX - pos_start;
			// Движение пальца влево от середины
			if (dif < -1) {
				dif *= -1;
				console.log(`${dif} - ${doorstep}`);
				// Ждем случая когда палец пройдет треть фотографии, тогда перелистываем на следующие фото
				if (dif > doorstep) {
					if (is_start === true) {
						is_start = false;
						console.log("last_img");
						Gallery.last_page(elm);
					}
				}
			}
			// Движение пальца вправо от середины
			else {
				console.log(`${dif} - ${doorstep}`);
				// Ждем случая когда палец пройдет треть фотографии, тогда перелистываем на следующие фото
				if (dif > doorstep) {
					if (is_start === true) {
						is_start = false;
						console.log("next_img");
						Gallery.next_page(elm);
					}
				}
			}
		});
	}
	static init() {
		this.touch_move();
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

	// Скрыть информацию о горячих клавишах, нужно для мобильных устройств
	static hide_info_hot_key() {
		// Удаляем подсказки горячих клавиш
		document.querySelectorAll(".hot_key_info").forEach((e) => {
			e.remove();
		});
	}

	// Инициализация логики компонентов программы
	static init() {
		let platform = this.get_platform();

		if (platform === "pc") {
			this.hot_key();
		} else if (platform === "phone") {
			this.hide_info_hot_key();
		}
		CLS_mddry_menu.init();
		Gallery.init();
	}
	// Определить платформу, телефон или ПК
	static get_platform() {
		if (
			/Android|webOS|iPhone|iPad|iPod|BlackBerry|BB|PlayBook|IEMobile|Windows Phone|Kindle|Silk|Opera Mini/i.test(
				navigator.userAgent
			)
		) {
			// Мобильный
			/*
                1. На телефонах отключаем подсказки горячих клавиш
            */
			return "phone";
		} else {
			// Пк
			return "pc";
		}
	}
}

// Событие загрузки страницы
window.onload = function () {
	InitApp.init();
};

// ------------------------------------000---------------------------------------------- //
