from json import dumps, loads
from pathlib import Path

from pytest import mark
from testfull_pack.file import ReadTextFile

from core.core_html import html_head, HTML_JS
from core.core_markdown_dry import CoreMarkdownDRY, StoreDoc


def _next_test():
    StoreDoc.clear()


class Test_Dev:

    def setup(self):
        """Выполнятся перед вызовом каждого метода"""
        _next_test()
        self.path = (Path(__file__).parent / 'dataset/in').__str__()

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_store'], [
        [
            ReadTextFile('./dataset/dev/in/Ссылочный блок использование.md',
                         '6bb9453f0f70c533ce130dbf72d2c896335be90c71c0ab206cac4935cb4e468c'),
            ReadTextFile('./dataset/dev/out/Ссылочный блок использование.md',
                         '14ce7f53d427c7e27092317e6bddf74ab13f8a3dd932391a14c5f080c28f5fe2'),
            ReadTextFile('./dataset/dev/out/ReferenceBlock Store.json',
                         '6eb3d9e7619e95b75d7a17a61b1b865a1e17cbe7c42001c01b21888246b2fa59')
        ]
    ])
    def test_UseReferenceBlock(self, T_in_data, T_check_data, T_store):
        _next_test()
        res = CoreMarkdownDRY.UseReferenceBlock(T_in_data.text, loads(T_store.text))
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/dev/in/Ссылочный блок init.md',
                         '1e78bf102fc67858d239183742e6ad4aee9e32eaba00ebd63b25067aea57f7b5'),
            ReadTextFile('./dataset/dev/out/Ссылочный блок init.html',
                         'cb273541601713af3b30acbea104b22d534cbcc12f599e570ea70037b730ad62'),
            ReadTextFile('./dataset/dev/out/ReferenceBlock Store.json',
                         '6eb3d9e7619e95b75d7a17a61b1b865a1e17cbe7c42001c01b21888246b2fa59')
        ]
    ])
    def test_ReferenceBlock(self, T_in_data, T_check_data, T_check_store):
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.ReferenceBlock(T_in_data.text)}"
        assert res == T_check_data.text
        assert dumps(StoreDoc.ReferenceBlock, ensure_ascii=False) == T_check_store.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/dev/in/Раскрываемые блок.md',
                         '7ecc3dece8c790cf5b530e7af1193e71438cf645136b3239f768cee0c2ddc758'),
            ReadTextFile('./dataset/dev/out/Раскрываемые блок.html',
                         'c30e69e530e3ff547ff6837b21bb00dd7f4dde24db872c1f1f573f1c29f7fdf5'),
            ReadTextFile('./dataset/dev/out/DropdownBlock Store.json',
                         'b976fb7c8af5edc9dfe5ae21680640f56f7cd709bc4eb1a214324c8f3b1f739a')
        ]
    ])
    def test_DropdownBlock(self, T_in_data, T_check_data: ReadTextFile, T_check_store):
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.DropdownBlock(T_in_data.text)}"
        assert res == T_check_data.text
        assert dumps(StoreDoc.DropdownBlock, ensure_ascii=False) == T_check_store.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/dev/in/Выделение блоков.md',
                         'd4d824f4816265727c318e863e97d8d4cb33cf15c141564971317c492c33356b'),
            ReadTextFile('./dataset/dev/out/Выделение блоков.html',
                         '5fbb33014c57dab06ce16fd6f8d761174ab86b25132c6addad0bdd25addb818c')
        ]
    ])
    def test_HighlightBlock(self, T_in_data, T_check_data: ReadTextFile):
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.HighlightBlock(T_in_data.text)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/dev/in/Фото галерея.md',
                         '503f487023874d1b86bd2909b3b912a7733a7a1a517ee4abc582875fe4995cbc'),
            ReadTextFile('./dataset/dev/out/Фото галерея.html',
                         '152e56ab9f048dbc978de3b7439b0dff36cbe615e19be71cb35b24b4f196cd03'),

        ]
    ])
    def test_PhotoGallery(self, T_in_data, T_check_data):
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.PhotoGallery(T_in_data.text)}"
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/dev/in/Многостраничные кодблоки.md',
                         'a198f7638825185af55882584ff42c68b770f138a5719ad84dd2bb3e1aab13f0'),
            ReadTextFile('./dataset/dev/out/Многостраничные кодблоки.html',
                         'c75d1dbd988ebd0d4f6c416e601c8a2f9191a95e461c039301312da3461f964f'),

        ]
    ])
    def test_MultiPageCode(self, T_in_data, T_check_data: ReadTextFile):
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.MultiPageCode(T_in_data.text)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/dev/in/Вставить кода из файла.md',
                         'c4819749a44277248d9bab900a4113bd69d3f55f47866b4c361d92d790278cec'),
            ReadTextFile('./dataset/dev/out/Вставить кода из файла.html',
                         '4b1aab4e0c89ca3e93f2c1c646eadf5fcf88b940f9c41a59ba1bce71dd900451'),

        ]
    ])
    def test_InsertCodeFromFile(self, T_in_data, T_check_data):
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.InsertCodeFromFile(T_in_data.text, self.path)}"
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/dev/in/Ссылки на структурные элементы кода.md',
                         'a2b6047c604859ba2669bcb1d25aa614d9dae4b1c8c746c743015ad08807fba7'),
            ReadTextFile('./dataset/dev/out/Ссылка на блоки кода.html',
                         'd4db30cc9c9885c63c1477b6fd9e3360da1c759884ebab4cd0733efa0b715f0e'),
        ]
    ])
    def test_LinkCode(self, T_in_data, T_check_data):
        """Детальная проверка"""
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.LinkCode(T_in_data.text, self.path)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', ], [
        [
            ReadTextFile('./dataset/dev/in/LinkCode.md',
                         'c77157a38180065e90324d5f4aff8c28cee84c602012c64236417a7b832b5dc6'),
            ReadTextFile('./dataset/dev/out/LinkCode.html',
                         'c9db2874fde90aa14ee3836b829dd4a304f6fdd800a6d5f9732ad258764d9f90'),

        ]
    ])
    def test_LinkCode_Simple(self, T_in_data, T_check_data: ReadTextFile):
        """Быстрая проверка"""
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.LinkCode(T_in_data.text, self.path)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/dev/in/HeaderMain.md',
                         'fa42ff7eb6b27267f7da60391fde3f99ff98907a33fd2cc2b444cf0cab4cda1b'),
            ReadTextFile('./dataset/dev/out/HeaderMain.html',
                         '71180c9bf7f4eef6ecafeea145dfaee3d9b91cf7e3066029853bb8575fc30e14'),
            ReadTextFile('./dataset/dev/out/HeaderMain Store.json',
                         '04902898b5e10020d58fc63e12fc73a644a1187ec1cba8d42615ac8c747d118d')

        ]
    ])
    def test_HeaderMain(self, T_in_data, T_check_data: ReadTextFile, T_check_store):
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.HeaderMain(T_in_data.text)}"
        assert dumps(StoreDoc.HeaderMain.date, ensure_ascii=False) == T_check_store.text
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/dev/in/ВложенныеПеременные.md',
                         '84f450f1f3845fdb0bd175364ee4f6380a9376b25f12c7a7be62b48093b92bf0'),
            ReadTextFile('./dataset/dev/out/ВложенныеПеременные.html',
                         'de921c18d4b041ac6ca8dcc76f4f8b2b812cabf23e7e7a9a1d7bf1e508beff92'),
            ReadTextFile('./dataset/dev/out/ВложенныеПеременные.json',
                         'be2e0b305e353dbea29ac22bad4528f12d02541bc1a9de3e4210843500917928')

        ]
    ])
    def test_DepVars(self, T_in_data, T_check_data, T_check_store):
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
            ReadTextFile('./dataset/dev/in/Многострочные таблицы.md',
                         'ebe0d41edc96e97ad9c59024ecd51d612983869d76a6329db8966287d178d38c'),
            ReadTextFile('./dataset/dev/out/Многострочные таблицы.html',
                         '662ccdb7e4fb06bcfa91a7ff936e752bf2c0940eccb9b7f3bba2553a2f3229a4')
        ]
    ])
    def test_MultilineTables(self, T_in_data, T_check_data):
        _next_test()
        res = f"{html_head}{CoreMarkdownDRY.MultiLineTables(T_in_data.text)}"
        assert res == T_check_data.text


class Test_Pub:
    """
    Тесты публичных примеров
    """

    def setup(self):
        """Выполнятся перед вызовом каждого метода"""
        _next_test()
        self.path = (Path(__file__).parent / 'dataset/pub/in').__str__()

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/InsertCodeFromFile.md',
                         'db0cb3300b33614ef2072406de60534782913406417d79a181d0c515d457b371'),
            ReadTextFile('./dataset/pub/out/InsertCodeFromFile.html',
                         None)
        ]
    ])
    def test_InsertCodeFromFile(self, T_in_data, T_check_data):
        res = f"{html_head}{CoreMarkdownDRY.InsertCodeFromFile(T_in_data.text, self.path)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', ], [
        [
            ReadTextFile('./dataset/pub/in/LinkCode_NET_GitGist.md',
                         'af1bf1e2543c80163daf049fc8da8eb47d1bca2f4f85d6e0c2505173c878dce6'),
            ReadTextFile('./dataset/pub/out/LinkCode_NET_GitGist.html',
                         None)
        ]
    ])
    def test_LinkCode_NET_GitGist(self, T_in_data, T_check_data):
        """Проверка ссылки ан GitGist"""
        res = f"{html_head}{CoreMarkdownDRY.LinkCode(T_in_data.text, self.path)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', ], [
        [
            ReadTextFile('./dataset/pub/in/LinkCode.md',
                         '9076c42a3fe2bfddd30108aaa7d29691229d6c078a0b9ca9787c0d650375083b'),
            ReadTextFile('./dataset/pub/out/LinkCode.html',
                         None),

        ]
    ])
    def test_LinkCode(self, T_in_data, T_check_data: ReadTextFile):
        """Быстрая проверка"""
        res = f"{html_head}{CoreMarkdownDRY.LinkCode(T_in_data.text, self.path)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/pub/in/HeaderMain.md',
                         '88810814dbe7c5a4089ae4c5c22748916cdddc2a239677c9d28d4faaa55b6ab3'),
            ReadTextFile('./dataset/pub/out/HeaderMain.html',
                         None),
            ReadTextFile('./dataset/pub/out/store/HeaderMain Store.json',
                         '868ad22fa9545e1dfce87c6be30bddc55f05422438f6164657b883534ff6e2a1')

        ]
    ])
    def test_HeaderMain(self, T_in_data, T_check_data: ReadTextFile, T_check_store):
        res = f"{html_head}{CoreMarkdownDRY.HeaderMain(T_in_data.text)}{HTML_JS.Hotkey.result}"
        # T_check_data.write(res)
        assert dumps(StoreDoc.HeaderMain.date, ensure_ascii=False) == T_check_store.text
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MathSpan_Simpl.md',
                         'ec42c80aa7a3437cab8ab289b9f9c498046117b8f10cc38910fcadd520e3bf97'),
            ReadTextFile('./dataset/pub/out/MathSpan_Simpl.html',
                         None),

        ]
    ])
    def test_MathSpan_Simpl(self, T_in_data, T_check_data):
        """Быстрая проверка"""
        res = f"{html_head}{CoreMarkdownDRY.MathSpan(T_in_data.text)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MathSpan.md',
                         None),
            ReadTextFile('./dataset/pub/out/MathSpan.html',
                         None),

        ]
    ])
    def test_MathSpan(self, T_in_data, T_check_data):
        res = f"{html_head}{CoreMarkdownDRY.MathSpan(CoreMarkdownDRY.HeaderMain(T_in_data.text))}{HTML_JS.Hotkey.result}"
        T_check_data.write(res)

        assert res == T_check_data.text
    # TODO: продолжить в верх MathSpan1,исправление тестов на публичные примеры
