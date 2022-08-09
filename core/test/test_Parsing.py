from pathlib import Path

from pytest import mark
from testfull_pack.file import ReadTextFile

from core.core_markdown_dry import StoreDoc
from core.core_parsing import Parsing


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
            ReadTextFile('./dataset/pub/out/Полноценный пример 1.html',
                         None),

        ]
    ])
    def test_CallParsing(self, T_in_data, T_check_data):
        res = Parsing(T_in_data.text).goPars(self.path)
        print(res)
        # assert res == T_check_data.text
