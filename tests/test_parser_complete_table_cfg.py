# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser import complete_table_cfg

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
@pytest.mark.parametrize('arg, expected', [

    ## no key
    pytest.param(
        dict(),
        dict(
            keyAttrNames=(),
            keyIndices=None,
            binnings=None,
            keyOutColumnNames=(),
            valAttrNames=None,
            valIndices=None,
            summaryClass=Count,
            valOutColumnNames=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='no-key-empty-dict'
    ),
    pytest.param(
        dict(keyAttrNames=( ), binnings=( )),
        dict(
            keyAttrNames=(),
            keyIndices=None,
            binnings=(),
            keyOutColumnNames=(),
            valAttrNames=None,
            valIndices=None,
            summaryClass=Count,
            valOutColumnNames=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='no-key-empty-key'
    ),

    ## one key
    pytest.param(
        dict(
            keyAttrNames='met_pt',
        ),
        dict(
            keyAttrNames=('met_pt',),
            keyIndices=None,
            binnings=None,
            keyOutColumnNames=('met_pt',),
            valAttrNames=None,
            valIndices=None,
            summaryClass=Count,
            valOutColumnNames=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='one-key-no-tuple'
    ),
    pytest.param(
        dict(
            keyAttrNames='met_pt',
            binnings=binning1,
        ),
        dict(
            keyAttrNames=('met_pt',),
            keyIndices=None,
            binnings=(binning1, ),
            keyOutColumnNames=('met_pt',),
            valAttrNames=None,
            valIndices=None,
            summaryClass=Count,
            valOutColumnNames=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='one-key-one-bin-no-tuple'
    ),
    pytest.param(
        dict(
            keyAttrNames='met_pt',
            keyIndices=1,
            binnings=binning1,
            keyOutColumnNames='met',
        ),
        dict(
            keyAttrNames=('met_pt',),
            keyIndices=(1, ),
            binnings=(binning1, ),
            keyOutColumnNames=('met',),
            valAttrNames=None,
            valIndices=None,
            summaryClass=Count,
            valOutColumnNames=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='one-key-idx-bin-out-no-tuple'
    ),
    pytest.param(
        dict(
            keyAttrNames=('met_pt', ),
            binnings=(binning1, ),
        ),
        dict(
            keyAttrNames=('met_pt',),
            keyIndices=None,
            binnings=(binning1, ),
            keyOutColumnNames=('met_pt',),
            valAttrNames=None,
            valIndices=None,
            summaryClass=Count,
            valOutColumnNames=('n', 'nvar'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='one-key-tuple'
    ),

    ## summary class
    pytest.param(
        dict(
            keyAttrNames=( ),
            binnings=( ),
            summaryClass=MockSummary2,
        ),
        dict(
            keyAttrNames=(),
            keyIndices=None,
            binnings=(),
            keyOutColumnNames=(),
            valAttrNames=None,
            valIndices=None,
            summaryClass=MockSummary2,
            valOutColumnNames=(),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-empty-key-empty-val'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            summaryClass=MockSummary2,
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=None,
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=None,
            valIndices=None,
            summaryClass=MockSummary2,
            valOutColumnNames=(),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-keys-empty-vals'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            valAttrNames=('val1', ),
            summaryClass=MockSummary2,
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=None,
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=('val1', ),
            valIndices=None,
            summaryClass=MockSummary2,
            summaryColumnNames=('val1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-keys-one-val-tuple'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            valAttrNames=('val1', ),
            valIndices=('*', ),
            summaryClass=MockSummary2,
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=None,
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=('val1', ),
            valIndices=('*', ),
            summaryClass=MockSummary2,
            summaryColumnNames=('val1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-keys-one-val-idx-tuple'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            valAttrNames='val1',
            summaryClass=MockSummary2,
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=None,
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=('val1', ),
            valIndices=None,
            summaryClass=MockSummary2,
            summaryColumnNames=('val1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-keys-one-val-no-tuple'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            valAttrNames='val1',
            valIndices='*',
            summaryClass=MockSummary2,
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=None,
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=('val1', ),
            valIndices=('*', ),
            summaryClass=MockSummary2,
            summaryColumnNames=('val1', ),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-keys-one-val-idx-no-tuple'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            valAttrNames=('val1', 'val2'),
            summaryClass=MockSummary2,
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=None,
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=('val1', 'val2'),
            valIndices=None,
            summaryClass=MockSummary2,
            valOutColumnNames=('val1', 'val2'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-keys-2-vals'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            keyIndices=(None, 1),
            valAttrNames=('val1', 'val2'),
            summaryClass=MockSummary2,
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=(None, 1),
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=('val1', 'val2'),
            valIndices=None,
            summaryClass=MockSummary2,
            valOutColumnNames=('val1', 'val2'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-2-keys-2-vals-key-indices'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            valAttrNames=('val1', 'val2'),
            summaryClass=MockSummary2,
            valIndices=(2, None),
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=None,
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=('val1', 'val2'),
            valIndices=(2, None),
            summaryClass=MockSummary2,
            valOutColumnNames=('val1', 'val2'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-2-keys-2-vals-val-indices'
    ),
    pytest.param(
        dict(
            keyAttrNames=('key1', 'key2'),
            binnings=(binning1, binning2),
            keyIndices=(None, 1),
            valAttrNames=('val1', 'val2'),
            summaryClass=MockSummary2,
            valIndices=(2, 3),
        ),
        dict(
            keyAttrNames=('key1', 'key2'),
            keyIndices=(None, 1),
            binnings=(binning1, binning2),
            keyOutColumnNames=('key1', 'key2'),
            valAttrNames=('val1', 'val2'),
            valIndices=(2, 3),
            summaryClass=MockSummary2,
            valOutColumnNames=('val1', 'val2'),
            weight=defaultWeight,
            sort=True,
            nevents=None,
        ),
        id='summary-class-2-keys-2-vals-key-indices-val-indices'
    ),
])
def test_complete(arg, expected):
    actual = complete_table_cfg(arg)
    assert expected == actual
    assert arg is not actual

##__________________________________________________________________||
