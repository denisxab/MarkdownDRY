from pytest import mark
from testfull_pack.file import ReadTextFile

from core.core_markdown_dry import StoreDoc
from core.core_parsing import Parsing


def _next_test():
    StoreDoc.clear()


@mark.parametrize(['T_in_data', 'T_check_data'], [
    [
        ReadTextFile('./dataset/in/Полноценный пример 1.md',
                     None),
        ReadTextFile('./dataset/out/Полноценный пример 1.html',
                     None),

    ]
])
def test_CallParsing(T_in_data, T_check_data):
    _next_test()
    res = Parsing(T_in_data.text).goPars()
    print()
    # assert res == T_check_data.text
