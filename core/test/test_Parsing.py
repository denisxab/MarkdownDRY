from pathlib import Path

from pytest import mark
from testfull_pack.file import ReadTextFile

from core.core_markdown_dry import StoreDoc
from core.core_parsing import ParsingToMarkdown, ParsingToHtml


def _next_test():
    StoreDoc.clear()


class Test_Pars:
    def setup(self):
        """Выполнятся перед вызовом каждого метода"""
        _next_test()
        self.path = (Path(__file__).parent / 'dataset/pub').__str__()

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/Полноценный пример 1.md',
                         None),
            ReadTextFile('./dataset/pub/ParsingToHtml.html',
                         None),

        ]
    ])
    def test_ParsingToHtml(self, T_in_data, T_check_data):
        res = ParsingToHtml(T_in_data.text).goPars(self.path)
        # T_check_data.write(res)
        print(res)
        # assert res == T_check_data.text

    @mark.parametrize(['T_in_data', 'T_check_data'], [
        [
            ReadTextFile('./dataset/pub/Полноценный пример 1.md',
                         None),
            ReadTextFile('./dataset/pub/ParsingToMarkdown.html',
                         None),

        ]
    ])
    def test_ParsingToMarkdown(self, T_in_data, T_check_data):
        res = ParsingToMarkdown(T_in_data.text).goPars(self.path)
        T_check_data.write(res)
        print(res)
        # assert res == T_check_data.text
