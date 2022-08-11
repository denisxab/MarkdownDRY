<br>Пример агрегатных функций внутри многострочной таблицы

| Имя      | Себестоимость   | Цена за отправку  | Цена на товар с учетом отправки   |
|----------|-----------------|-------------------|-----------------------------------|
| Кукуруза | 100             | 20                | `~2,1+3,1`                        |
| НАША     |                 |                   |                                   |
| ---      | ---             | ---               | ---                               |
| Огурец   | 200             | 20                | `~2,2+3,2`                        |
| ---      | ---             | ---               | ---                               |
| Хлеб     | 450             |                   |                                   |
| Вкусный  |                 | 43                | `~sum(2,3,3,3)`                   |
| ---      | ---             | ---               | ---                               |
|          | `~avg(2,2,1,3)` | `~avg(3,3,1,3)+1` | `~10+sum(4,4,1,3)+1+avg(3,3,1,3)` |
| ---      | ---             | ---               | ---                               |

<br>Пример агрегатных функций внутри обычной таблицы

| Имя      | Себестоимость   | Цена за отправку | Цена на товар с учетом отправки |
| -------- |-----------------|------------------|---------------------------------|
| Кукуруза | 100             | 20               | `~2,1+3,1`                      |
| Помидор  | 300             | 25               | `~2,2+3,2`                      |
| Огурец   | 200             | 20               | `~2,3+3,3`                      |
| Молоко   | 400             | 30               | `~2,4+3,4`                      |
| Хлеб     | 450             | 43               | `~2,5+3,5`                      |
|          | `~avg(2,2,1,5)` | `~avg(3,3,1,5)`  | `~sum(4,4,1,5)`                 |

<br>Пример многострочной таблицы

| Метод                                           | Описание                                                    | Аргументы                   |
| ----------------------------------------------- | ----------------------------------------------------------- | --------------------------- |
| `os.remove(...)`                                | Удалить файл                                                | path=Путь к файлу           |
| ----------------------------------------------- | ----------------------------------------------------------- | ----------------------      |
| `list[start:stop:steep]`                        | Получить слайс                                              | start=Начальный индекс      |
|                                                 | ```py                                                       | stop=Конечный индекс        |
|                                                 | print('Hello Proger')                                       |                             |
|                                                 | ```                                                         | steep=Шаг                   |
| ----------------------------------------------- | ----------------------------------------------------------- | --------------------------- |
| `list.index(ЧтоИскать, Start, End)` -%3E `int`  | Возвращает `index` первого элемента со значением            | ЧтоИскать:str=Искомый текст |
|                                                 | `ЧтоИскать` (при этом поиск ведется от `Start` до `End`)    | Start:int=Старт             |
|                                                 | ![](_attachments/247f4dd8485c60f082aa5b874dde3c0a.png)      | End:int=Конец               |
| ----------------------------------------------- | ----------------------------------------------------------- | --------------------------- |
