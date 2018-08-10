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
params = [

    pytest.param(
        dict(),
        dict(
            key_name=(),
            key_index=None,
            key_binning=None,
            key_out_name=(),
            val_name=None,
            val_index=None,
            agg_class=Count,
            agg_name=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='no-key-empty-dict'
    ),
]

@pytest.mark.parametrize('arg, expected', params)
def test_complete(arg, expected):
    actual = complete_table_cfg(arg)
    assert expected == actual
    assert arg is not actual

##__________________________________________________________________||
