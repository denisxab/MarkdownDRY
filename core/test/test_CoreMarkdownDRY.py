import pathlib
from json import dumps, loads
from pathlib import Path

from pytest import mark
from testfull_pack.file import ReadTextFile

from core.core_html import html_head
from core.core_markdown_dry import CoreMarkdownDRY, StoreDoc


def _next_test():
    StoreDoc.clear()


# pathlib.Path('./dataset/out/...').write_text(res)


self_path: pathlib.Path = Path(__file__).parent / 'dataset/in'


@mark.parametrize(['T_in_data', 'T_check_data', 'T_store'], [
    [
        ReadTextFile('./dataset/in/Ссылочный блок использование.md',
                     '6bb9453f0f70c533ce130dbf72d2c896335be90c71c0ab206cac4935cb4e468c'),
        ReadTextFile('./dataset/out/Ссылочный блок использование.md',
                     '14ce7f53d427c7e27092317e6bddf74ab13f8a3dd932391a14c5f080c28f5fe2'),
        ReadTextFile('./dataset/out/ReferenceBlock Store.json',
                     '6eb3d9e7619e95b75d7a17a61b1b865a1e17cbe7c42001c01b21888246b2fa59')
    ]
])
def test_UseReferenceBlock(T_in_data, T_check_data, T_store):
    _next_test()
    res = CoreMarkdownDRY.UseReferenceBlock(T_in_data.text, loads(T_store.text))
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
    [
        ReadTextFile('./dataset/in/Ссылочный блок init.md',
                     '1e78bf102fc67858d239183742e6ad4aee9e32eaba00ebd63b25067aea57f7b5'),
        ReadTextFile('./dataset/out/Ссылочный блок init.html',
                     'cb273541601713af3b30acbea104b22d534cbcc12f599e570ea70037b730ad62'),
        ReadTextFile('./dataset/out/ReferenceBlock Store.json',
                     '6eb3d9e7619e95b75d7a17a61b1b865a1e17cbe7c42001c01b21888246b2fa59')
    ]
])
def test_ReferenceBlock(T_in_data, T_check_data, T_check_store):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.ReferenceBlock(T_in_data.text)}"
    assert res == T_check_data.text
    assert dumps(StoreDoc.ReferenceBlock, ensure_ascii=False) == T_check_store.text


@mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
    [
        ReadTextFile('./dataset/in/Раскрываемые блок.md',
                     '7ecc3dece8c790cf5b530e7af1193e71438cf645136b3239f768cee0c2ddc758'),
        ReadTextFile('./dataset/out/Раскрываемые блок.html',
                     'c30e69e530e3ff547ff6837b21bb00dd7f4dde24db872c1f1f573f1c29f7fdf5'),
        ReadTextFile('./dataset/out/DropdownBlock Store.json',
                     'b976fb7c8af5edc9dfe5ae21680640f56f7cd709bc4eb1a214324c8f3b1f739a')
    ]
])
def test_DropdownBlock(T_in_data, T_check_data: ReadTextFile, T_check_store):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.DropdownBlock(T_in_data.text)}"
    assert res == T_check_data.text
    assert dumps(StoreDoc.DropdownBlock, ensure_ascii=False) == T_check_store.text


@mark.parametrize(['T_in_data', 'T_check_data'], [
    [
        ReadTextFile('./dataset/in/Выделение блоков.md',
                     'd4d824f4816265727c318e863e97d8d4cb33cf15c141564971317c492c33356b'),
        ReadTextFile('./dataset/out/Выделение блоков.html',
                     '5fbb33014c57dab06ce16fd6f8d761174ab86b25132c6addad0bdd25addb818c')
    ]
])
def test_HighlightBlock(T_in_data, T_check_data: ReadTextFile):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.HighlightBlock(T_in_data.text)}"
    # T_check_data.write(res)
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data'], [
    [
        ReadTextFile('./dataset/in/Фото галерея.md',
                     '503f487023874d1b86bd2909b3b912a7733a7a1a517ee4abc582875fe4995cbc'),
        ReadTextFile('./dataset/out/Фото галерея.html',
                     '152e56ab9f048dbc978de3b7439b0dff36cbe615e19be71cb35b24b4f196cd03'),

    ]
])
def test_PhotoGallery(T_in_data, T_check_data):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.PhotoGallery(T_in_data.text)}"
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data'], [
    [
        ReadTextFile('./dataset/in/Многостраничные кодблоки.md',
                     'a198f7638825185af55882584ff42c68b770f138a5719ad84dd2bb3e1aab13f0'),
        ReadTextFile('./dataset/out/Многостраничные кодблоки.html',
                     'c75d1dbd988ebd0d4f6c416e601c8a2f9191a95e461c039301312da3461f964f'),

    ]
])
def test_MultiPageCode(T_in_data, T_check_data: ReadTextFile):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.MultiPageCode(T_in_data.text)}"
    # T_check_data.write(res)
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data'], [
    [
        ReadTextFile('./dataset/in/Математический Размах.md',
                     'e5de21331b0ac36342f02a5411a7af7611ca2b56a7de8e3fd456bcd649dcfd14'),
        ReadTextFile('./dataset/out/Математический Размах.html',
                     'bc2df24d7436ec351b100b1475123aa13eb3cfa6408f713ed183f37c7272e7c4'),

    ]
])
def test_MathSpan(T_in_data, T_check_data):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.MathSpan(T_in_data.text)}"
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data', '_self_path'], [
    [
        ReadTextFile('./dataset/in/Вставить кода из файла.md',
                     'c4819749a44277248d9bab900a4113bd69d3f55f47866b4c361d92d790278cec'),
        ReadTextFile('./dataset/out/Вставить кода из файла.html',
                     '4b1aab4e0c89ca3e93f2c1c646eadf5fcf88b940f9c41a59ba1bce71dd900451'),
        self_path
    ]
])
def test_InsertCodeFromFile(T_in_data, T_check_data, _self_path):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.InsertCodeFromFile(T_in_data.text, _self_path)}"
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data', '_self_path'], [
    [
        ReadTextFile('./dataset/in/Ссылки на структурные элементы кода.md',
                     'a2b6047c604859ba2669bcb1d25aa614d9dae4b1c8c746c743015ad08807fba7'),
        ReadTextFile('./dataset/out/Ссылка на блоки кода.html',
                     '01c2432308ae79e7f11249c23790c6dd21d273aa28e12a174efb0f9a87ef2081'),
        self_path
    ]
])
def test_LinkCode(T_in_data, T_check_data, _self_path):
    """Детальная проверка"""
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.LinkCode(T_in_data.text, _self_path)}"
    # T_check_data.write(res)
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data', '_self_path'], [
    [
        ReadTextFile('./dataset/in/LinkCode.md',
                     None),
        ReadTextFile('./dataset/out/LinkCode.html',
                     None),
        self_path
    ]
])
def test_LinkCode_Simple(T_in_data, T_check_data: ReadTextFile, _self_path):
    """Быстрая проверка"""
    # TODO: Записать данные из файла в JS строку, продумать логику показать этот код пользователю
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.LinkCode(T_in_data.text, _self_path)}"
    # T_check_data.write(res)
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
    [
        ReadTextFile('./dataset/in/HeaderMain.md',
                     'fa42ff7eb6b27267f7da60391fde3f99ff98907a33fd2cc2b444cf0cab4cda1b'),
        ReadTextFile('./dataset/out/HeaderMain.html',
                     None),
        ReadTextFile('./dataset/out/HeaderMain Store.json',
                     '04902898b5e10020d58fc63e12fc73a644a1187ec1cba8d42615ac8c747d118d')

    ]
])
def test_HeaderMain(T_in_data, T_check_data: ReadTextFile, T_check_store):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.HeaderMain(T_in_data.text)}"
    assert dumps(StoreDoc.HeaderMain.date, ensure_ascii=False) == T_check_store.text
    # T_check_data.write(res)
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
    [
        ReadTextFile('./dataset/in/ВложенныеПеременные.md',
                     '84f450f1f3845fdb0bd175364ee4f6380a9376b25f12c7a7be62b48093b92bf0'),
        ReadTextFile('./dataset/out/ВложенныеПеременные.html',
                     'de921c18d4b041ac6ca8dcc76f4f8b2b812cabf23e7e7a9a1d7bf1e508beff92'),
        ReadTextFile('./dataset/out/ВложенныеПеременные.json',
                     'be2e0b305e353dbea29ac22bad4528f12d02541bc1a9de3e4210843500917928')

    ]
])
def test_DepVars(T_in_data, T_check_data, T_check_store):
    """Вложенные обращения к переменным"""
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.HeaderMain(T_in_data.text)}"
    # Проведем расчеты данных которые сформированные через переменные
    res = CoreMarkdownDRY.MathSpan(res)
    assert dumps(StoreDoc.HeaderMain.date, ensure_ascii=False) == T_check_store.text
    # T_check_data.write(res)
    assert res == T_check_data.text


@mark.parametrize(['T_in_data', 'T_check_data'], [
    [
        ReadTextFile('./dataset/in/Многострочные таблицы.md',
                     'ebe0d41edc96e97ad9c59024ecd51d612983869d76a6329db8966287d178d38c'),
        ReadTextFile('./dataset/out/Многострочные таблицы.html',
                     '662ccdb7e4fb06bcfa91a7ff936e752bf2c0940eccb9b7f3bba2553a2f3229a4')

    ]
])
def test_MultilineTables(T_in_data, T_check_data):
    _next_test()
    res = f"{html_head}{CoreMarkdownDRY.MultiLineTables(T_in_data.text)}"
    assert res == T_check_data.text
