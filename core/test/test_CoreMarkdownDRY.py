from json import dumps, loads
from pathlib import Path
from typing import Literal

from pytest import mark
from testfull_pack.file import ReadTextFile

from core.core_html import html_head, HTML_JS
from core.core_markdown import CoreMarkdown
from core.core_markdown_dry import CoreMarkdownDRY, StoreDoc
from core.core_parsing import ParsingBase


def _next_test():
    StoreDoc.clear()


class Test_Dev:

    def setup(self):
        """Выполнятся перед вызовом каждого метода"""
        _next_test()
        self.path = (Path(__file__).parent / 'dataset/in').__str__()

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
                         '216b0c263796c34e3cb59f0186804b746ea2b19cf3d4efa76b1a203bce5a0ccf'),
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


class Test_Pub_To_HTML:
    """
    Публичные тесты для конвертации в HTML
    """

    def setup(self):
        self.type_out: Literal['html', 'md'] = 'html'
        _next_test()

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MathSpan_Simpl.md',
                         '013b0718ccde1ab8f6082f5dff24e26a34d5b17e811f1e3d8926c53ba7546b43'),
            ReadTextFile('./dataset/pub/out/MathSpan_Simpl.html',
                         None),

        ]
    ])
    def test_MathSpan_Simpl(self, T_in_data, T_check_data):
        """Быстрая проверка"""
        res = f"{html_head}{CoreMarkdownDRY.MathSpan(T_in_data.text, self.type_out)}"
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
        res = f"{html_head}{CoreMarkdownDRY.MathSpan(CoreMarkdownDRY.HeaderMain(T_in_data.text, self.type_out), self.type_out)}{''.join(StoreDoc.LastInsert)}{HTML_JS.Hotkey.result}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MathSpan_Upgrade.md',
                         None),
            ReadTextFile('./dataset/pub/out/MathSpan_Upgrade.html',
                         None),

        ]
    ])
    def test_MathSpan_Upgrade(self, T_in_data, T_check_data):
        """
        Математическое выражение переменными и подсказками
        """
        res = f"{html_head}{CoreMarkdownDRY.MathSpan(CoreMarkdownDRY.HeaderMain(CoreMarkdown.Br(T_in_data.text), self.type_out), self.type_out)}{''.join(StoreDoc.LastInsert)}{HTML_JS.Hotkey.result}{HTML_JS.MathSpan}"
        T_check_data.write(res)
        assert res == T_check_data.text


class Test_Pub_To_MD:
    """
    Публичные тесты для конвертации в Markdown
    """

    def setup(self):
        self.type_out: Literal['html', 'md'] = 'md'
        self.path = (Path(__file__).parent / 'dataset/pub/in').__str__()
        _next_test()

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/Header_Vars_MathSpan.md',
                         '9f76b82334c75f08e6f3f862e4db6df142b81b420ef51d8a9649b40fef502aff'),
            ReadTextFile('./dataset/pub/out/Header_Vars_MathSpan.md',
                         'be2f4b5eafb298509054c61e6a754b838e44800b6d89b72579416176d94120a7'),
        ]
    ])
    def test_Header_Vars_MathSpan(self, T_in_data, T_check_data):
        """
        Математическое выражение переменными и подсказками
        """
        res1 = CoreMarkdownDRY.HeaderMain(T_in_data.text, self.type_out)
        res = CoreMarkdownDRY.MathSpan(res1, self.type_out)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MathSpan_Simpl.md',
                         '013b0718ccde1ab8f6082f5dff24e26a34d5b17e811f1e3d8926c53ba7546b43'),
            ReadTextFile('./dataset/pub/out/MathSpan_Simpl.md',
                         '4ff6899ed4d0a8198ec10eaa31b233068be52af03541d65e4b9e9ffa2770d38f'),
        ]
    ])
    def test_MathSpan_Simpl(self, T_in_data, T_check_data):
        """Быстрая проверка"""
        res = CoreMarkdownDRY.MathSpan(T_in_data.text, self.type_out)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MathSpan.md',
                         '0022143b197b892e6326267dae62a3632c17321f0d7152ca5bad4421fe1ead15'),
            ReadTextFile('./dataset/pub/out/MathSpan.md',
                         'fd5b5ddfc754c2b938b0e82016e99026cc76e60fb01671322c3ac7fcf7a0318f'),
        ]
    ])
    def test_MathSpan(self, T_in_data, T_check_data):
        res = CoreMarkdownDRY.MathSpan(CoreMarkdownDRY.HeaderMain(T_in_data.text, self.type_out), self.type_out)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/InsertCodeFromFile.md',
                         'a91e346234985ed1f3fc447c460c0c03189c46bf2e871ab00b7cea7f63213dff'),
            ReadTextFile('./dataset/pub/out/InsertCodeFromFile.md',
                         'f870d42aeedc168591f1f30249d16acd0abda14d1be495a9c9e9c57efecb8a7f')
        ]
    ])
    def test_InsertCodeFromFile(self, T_in_data, T_check_data):
        res = CoreMarkdownDRY.InsertCodeFromFile(T_in_data.text, self.path, self.type_out)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/IndisputableInsertCodeFromFile.md',
                         '4d464265bce2b39d1fbf091e58134ee67854025370ad6352b40dd8581c22e671'),
            ReadTextFile('./dataset/pub/out/IndisputableInsertCodeFromFile.md',
                         'e96d4ca044661b7dcc35da52164b1206b5e12fa5bd74bf2fa77f8b015510af27'),
        ]
    ])
    def test_IndisputableInsertCodeFromFile(self, T_in_data, T_check_data):
        res = CoreMarkdownDRY.IndisputableInsertCodeFromFile(T_in_data.text, self.path)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MultiLineTables.md',
                         '754e71650ce80e294b8dec8b618b417e8dedb1df345b629731b6def87703f366'),
            ReadTextFile('./dataset/pub/out/MultiLineTables.md',
                         'f31a28090d2ac20f71b40de78c67ac5cee48bb5c19d3714cf6fa1a65886e7b33')
        ]
    ])
    def test_MultiLineTables(self, T_in_data, T_check_data):
        res = CoreMarkdownDRY.MultiLineTables(T_in_data.text, self.type_out)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_store', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/ReferenceBlock.md',
                         'e877ab5baa36b0093b59b6c5faf9078511d3238831a87d1bc7b2fb646d0c7a12'),
            ReadTextFile('./dataset/pub/out/store/ReferenceBlock.json',
                         '1a95b66a729a8db3a7d0cc341662bfe84eefffb57a854b2e846d1cdeb5f6f6b7'),
            ReadTextFile('./dataset/pub/out/ReferenceBlock.md',
                         '76621497bef049d73dd0fe7d37eba02a22a39b9362bc0296c5c6083769330b12')
        ]
    ])
    def test_ReferenceBlock(self, T_in_data, T_check_store, T_check_data):
        res = CoreMarkdownDRY.ReferenceBlock(T_in_data.text, self.type_out)
        assert dumps(StoreDoc.ReferenceBlock, ensure_ascii=False) == T_check_store.text
        res = CoreMarkdownDRY.UseReferenceBlock(res, StoreDoc.ReferenceBlock)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_store', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/ProceduralTemplates.md',
                         'bdab6c75cb5f5b40115c14c94232092a1ff026f6d12cb99afc2d9c3c7da08ca7'),
            ReadTextFile('./dataset/pub/out/store/ProceduralTemplates.json',
                         'fd2e25639ea91b021ba094e8df54a3b62a1ced91001cb75305860772ea704820'),
            ReadTextFile('./dataset/pub/out/ProceduralTemplates.md',
                         '4ed7645458df29c75a5eb8b9f96d7e9d1604b6ad69ea08c3db891805ba881d7c')
        ]
    ])
    def test_ProceduralTemplates(self, T_in_data, T_check_store, T_check_data):
        res = CoreMarkdownDRY.ProceduralTemplates(T_in_data.text, self.type_out)
        assert dumps(StoreDoc.ProceduralTemplates.date, ensure_ascii=False) == T_check_store.text
        res = CoreMarkdownDRY.UseProceduralTemplates(res, StoreDoc.ProceduralTemplates)
        # T_check_data.write(res)
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
                         None),
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
                         '1b6363a70405c7afa7ba9eef966702df15d6129ede7974e4a9b7b9478f3c75cb'),
            ReadTextFile('./dataset/pub/out/LinkCode_NET_GitGist.html',
                         '4e5d873cb9bc9a7d0df22853993ecc5650c0dc00358ec6a4d861801608e8a8fb')
        ]
    ])
    def test_LinkCode_NET_GitGist(self, T_in_data, T_check_data):
        """Проверка ссылки ан GitGist"""
        res = f"{html_head}{CoreMarkdownDRY.LinkCode(T_in_data.text, self.path)}{ParsingBase._ReturnLastInsert()}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', ], [
        [
            ReadTextFile('./dataset/pub/in/LinkCode.md',
                         'de14fc7157327ace051259ff96c7f34648daab78c2bad6fc2e8d1991475abace'),
            ReadTextFile('./dataset/pub/out/LinkCode.html',
                         '9da98369d24ab384b957eb679e6947d6edc7c3098600c39da7038ca4e446e9e2'),
        ]
    ])
    def test_LinkCode(self, T_in_data, T_check_data: ReadTextFile):
        """Быстрая проверка"""
        res = f"{html_head}{CoreMarkdownDRY.LinkCode(T_in_data.text, self.path)}{ParsingBase._ReturnLastInsert()}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/pub/in/HeaderMain.md',
                         '88810814dbe7c5a4089ae4c5c22748916cdddc2a239677c9d28d4faaa55b6ab3'),
            ReadTextFile('./dataset/pub/out/HeaderMain.html',
                         None),
            ReadTextFile('./dataset/pub/out/store/HeaderMain.json',
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
            ReadTextFile('./dataset/pub/in/PhotoGallery.md',
                         '998afda2ac2ddbf0b9ce2c6240b817ed727361d63cd437a21aea6545d450d6e5'),
            ReadTextFile('./dataset/pub/out/PhotoGallery.html',
                         None),

        ]
    ])
    def test_PhotoGallery(self, T_in_data, T_check_data):
        res = f"{html_head}{CoreMarkdownDRY.PhotoGallery(T_in_data.text)}"
        # T_check_data.write(res)
        """
        # Конвертировать путь к изображению в base64 для того чтобы хранить фото в самом HTML файле 
        function toDataURL(url, callback) {
          var xhr = new XMLHttpRequest();
          xhr.onload = function() {
            var reader = new FileReader();
            reader.onloadend = function() {
              callback(reader.result);
            }
            reader.readAsDataURL(xhr.response);
          };
          xhr.open('GET', url);
          xhr.responseType = 'blob';
          xhr.send();
        }
        
        toDataURL(a.src, function(dataUrl) {
          console.log('RESULT:', dataUrl)
        })
        """
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/HighlightBlock.md',
                         'a1da4d84a72f2742f59f70df3a4632ec0e0eb9d0bafbf0a2d4ae344a2c5d5948'),
            ReadTextFile('./dataset/pub/out/HighlightBlock.html',
                         None)
        ]
    ])
    def test_HighlightBlock(self, T_in_data, T_check_data: ReadTextFile):
        res = f"{html_head}{CoreMarkdownDRY.HighlightBlock(T_in_data.text)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/pub/in/DropdownBlock.md',
                         '441bb9cfdad159de4ea24403b1d5cb18132db9bdfaa86799422655d776ec3ba2'),
            ReadTextFile('./dataset/pub/out/DropdownBlock.html',
                         None),
            ReadTextFile('./dataset/pub/out/store/DropdownBlock.json',
                         '6621f20dc21b13221c3d31983f13bbe337cddeb83c8e07cba69e0ecaf5b76547')
        ]
    ])
    def test_DropdownBlock(self, T_in_data, T_check_data: ReadTextFile, T_check_store):
        res = f"{html_head}{CoreMarkdownDRY.DropdownBlock(T_in_data.text)}"
        # T_check_data.write(res)
        assert res == T_check_data.text
        assert dumps(StoreDoc.DropdownBlock, ensure_ascii=False) == T_check_store.text

    @mark.parametrize(['T_in_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/pub/in/ReferenceBlock.md',
                         None),
            ReadTextFile('./dataset/pub/out/store/ReferenceBlock.json',
                         '1a95b66a729a8db3a7d0cc341662bfe84eefffb57a854b2e846d1cdeb5f6f6b7')
        ]
    ])
    def test_ReferenceBlock(self, T_in_data, T_check_store):
        CoreMarkdownDRY.ReferenceBlock(T_in_data.text)
        assert dumps(StoreDoc.ReferenceBlock, ensure_ascii=False) == T_check_store.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_store'], [
        [
            ReadTextFile('./dataset/pub/in/ReferenceBlock.md',
                         None),
            ReadTextFile('./dataset/pub/out/ReferenceBlock.md',
                         None),
            ReadTextFile('./dataset/pub/out/store/ReferenceBlock.json',
                         '1a95b66a729a8db3a7d0cc341662bfe84eefffb57a854b2e846d1cdeb5f6f6b7')
        ]
    ])
    def test_UseReferenceBlock(self, T_in_data, T_check_data, T_store):
        res = CoreMarkdownDRY.UseReferenceBlock(T_in_data.text, loads(T_store.text))
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data', 'T_check_store'], [
        [
            ReadTextFile('./dataset/pub/in/Vars.md',
                         '9c7c7fb98a49a5e201b3b8617491dbeed6d78f5b07efc5211d9861486b03b6a6'),
            ReadTextFile('./dataset/pub/out/Vars.html',
                         None),
            ReadTextFile('./dataset/pub/out/store/Vars.json',
                         '08d01840b2d2a8d72e4b2a66fa86aaba06ff44d24fa586b97c3752493891b633')

        ]
    ])
    def test_Vars(self, T_in_data, T_check_data, T_check_store):
        """Вложенные обращения к переменным"""
        res = f"{html_head}{CoreMarkdownDRY.HeaderMain(T_in_data.text)}{HTML_JS.Hotkey.result}"
        # T_check_data.write(res)
        assert dumps(StoreDoc.HeaderMain.date, ensure_ascii=False) == T_check_store.text
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/IndisputableInsertCodeFromFile.md',
                         '4d464265bce2b39d1fbf091e58134ee67854025370ad6352b40dd8581c22e671'),
            ReadTextFile('./dataset/pub/out/IndisputableInsertCodeFromFile.md',
                         'e96d4ca044661b7dcc35da52164b1206b5e12fa5bd74bf2fa77f8b015510af27'),
        ]
    ])
    def test_IndisputableInsertCodeFromFile(self, T_in_data, T_check_data):
        res = f"{CoreMarkdownDRY.IndisputableInsertCodeFromFile(T_in_data.text, self.path)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MultiPageCode.md',
                         '2b5a8a9b312f8d052853f3cd20ba3a792fe97009e2339b97da3a74e24081b0b5'),
            ReadTextFile('./dataset/pub/out/MultiPageCode.html',
                         None),

        ]
    ])
    def test_MultiPageCode(self, T_in_data, T_check_data: ReadTextFile):
        res = f"{html_head}{CoreMarkdownDRY.MultiPageCode(T_in_data.text)}"
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/MultiLineTables.md',
                         '754e71650ce80e294b8dec8b618b417e8dedb1df345b629731b6def87703f366'),
            ReadTextFile('./dataset/pub/out/MultiLineTables.html',
                         None)
        ]
    ])
    def test_MultiLineTables(self, T_in_data, T_check_data):
        res = f"{html_head}{CoreMarkdownDRY.MultiLineTables(T_in_data.text)}"
        # T_check_data.write(res)
        assert res == T_check_data.text
