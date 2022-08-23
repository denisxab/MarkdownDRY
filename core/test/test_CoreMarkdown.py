from pytest import mark
from testfull_pack.file import ReadTextFile

from core.core_html import html_head
from core.core_markdown import CoreMarkdown
from core.core_markdown_dry import StoreDoc


def _next_test():
    StoreDoc.clear()


class Test_Pub:
    def setup(self):
        _next_test()

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/Ul.md',
                         '03f0f9219f111451991d555d2302987cbdee6c204dbaefae0d50879560943b80'),
            ReadTextFile('./dataset/pub/out/Ul.html',
                         '676d114d16109fea39ab1fa2eea6b817b8ba5f6ff37b1c646d4b368108ab3aaa'),
        ]
    ])
    def test_Ul(self, T_in_data, T_check_data):
        res = CoreMarkdown.Ul(T_in_data.text)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/Ol.md',
                         '12641df4ca9d25be3ee10468307ee62b00f2c60e3031d398eb15f7fab8340904'),
            ReadTextFile('./dataset/pub/out/Ol.html',
                         '7ec45b67a7af8ca5fe461e792ed00e4426b2af48d2b67112ea82f406f93a3eef'),
        ]
    ])
    def test_Ol(self, T_in_data, T_check_data: ReadTextFile):
        res = CoreMarkdown.Ol(T_in_data.text)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/Ol_and_Ul.md',
                         '3986ed6af56e5af944606c8e308304f11e02900be96b5733075aa02d2c89b9df'),
            ReadTextFile('./dataset/pub/out/Ol_and_Ul.html',
                         'c050f2fcf6cc44d1bd19315002040e98430d9c09fb481085e166fa6fbcfd2ef0'),
        ]
    ])
    def test_Ol_and_Ul(self, T_in_data, T_check_data: ReadTextFile):
        res = CoreMarkdown.Ol(T_in_data.text)
        res = CoreMarkdown.Ul(res)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/Hr.md',
                         '98a8d57899581e381ce83cb127c46a55515ea3515ae48e8790087b644b5a21c3'),
            ReadTextFile('./dataset/pub/out/Hr.html',
                         'a460cbaf4c6c1600de1c06d8ef7b027b50c192fa2ed80e55d1e3032d5f564ac6'),
        ]
    ])
    def test_Hr(self, T_in_data, T_check_data: ReadTextFile):
        res = CoreMarkdown.Hr(T_in_data.text)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/Hr.md',
                         '98a8d57899581e381ce83cb127c46a55515ea3515ae48e8790087b644b5a21c3'),
            ReadTextFile('./dataset/pub/out/Hr.html',
                         'a460cbaf4c6c1600de1c06d8ef7b027b50c192fa2ed80e55d1e3032d5f564ac6'),
        ]
    ])
    def test_Hr(self, T_in_data, T_check_data: ReadTextFile):
        res = CoreMarkdown.Hr(T_in_data.text)
        # T_check_data.write(res)
        assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/in/Br.md',
                         '4e017e6fd20df2593861277426e5e60d8edd9fd0f561c454c17de33ccf1423ae'),
            ReadTextFile('./dataset/pub/out/Br.html',
                         None),
        ]
    ])
    def test_Br(self, T_in_data, T_check_data: ReadTextFile):
        res = f"{html_head}{CoreMarkdown.Br(T_in_data.text)}"
        # T_check_data.write(res)
        assert res == T_check_data.text
