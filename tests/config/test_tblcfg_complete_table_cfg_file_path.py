# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._tblcfg import complete_table_cfg

from alphatwirl.summary import Count, WeightCalculatorOne


def eq(self, other):
    return isinstance(other, self.__class__)
WeightCalculatorOne.__eq__ = eq

##__________________________________________________________________||
class MockSummary2:
    pass

class MockBinning:
    pass

defaultWeight = WeightCalculatorOne()
binning1 = MockBinning()
binning2 = MockBinning()

##__________________________________________________________________||
KEYS_NEED_TO_EXIST_BUT_DONT_TEST_VALUES = (
    'key_name', 'key_index', 'key_binning', 'key_out_name',
    'val_name', 'val_index', 'agg_class', 'agg_name',
    'weight', 'sort', 'nevents')

params = [

    pytest.param(
        dict(),
        dict(store_file=False),
        id='empty'),

    pytest.param(
        dict(store_file=False),
        dict(store_file=False),
        id='empty-false'),

    pytest.param(
        dict(store_file=True),
        dict(
            store_file=True,
            file_name='tbl_n.txt',
        ),
        id='empty-true'),

    pytest.param(
        dict(key_name='met', store_file=True),
        dict(
            store_file=True,
            file_name='tbl_n.met.txt',
        ),
        id='composed'),

    pytest.param(
        dict(
            key_name='met',
            store_file=True,
            file_name='tbl.given-filename.txt',
        ),
        dict(
            store_file=True,
            file_name='tbl.given-filename.txt',
        ),
        id='given'),

    pytest.param(
        dict(
            key_name='met',
            store_file=True,
            file_name_prefix='tbl_abc',
        ),
        dict(
            store_file=True,
            file_name_prefix='tbl_abc',
            file_name='tbl_abc.met.txt',
        ),
        id='prefix'),

]

@pytest.mark.parametrize('arg, expected', params)
def test_complete(arg, expected):
    actual = complete_table_cfg(arg)
    assert arg is not actual
    for k in KEYS_NEED_TO_EXIST_BUT_DONT_TEST_VALUES:
        actual.pop(k)
    assert expected == actual

##__________________________________________________________________||
