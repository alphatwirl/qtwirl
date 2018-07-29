# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

import alphatwirl

from qtwirl._parser import parse_reader_cfg

##__________________________________________________________________||
RoundLog = mock.Mock()

tblcfg_dict1 = dict(
    keyAttrNames=('jet_pt', ),
    binnings=(RoundLog(0.1, 100), ),
    keyIndices=('*', ),
)

tblcfg_dict2 = dict(
    keyAttrNames=('met', ),
    binnings=(RoundLog(0.1, 100), ),
)

##__________________________________________________________________||
@pytest.mark.parametrize('arg, expected', [
    pytest.param(
        dict(), dict(table_cfg=dict()), id='empty-dict'
    ),
    pytest.param(
        [ ], [ ], id='empty-list'
    ),
    pytest.param(
        dict(tblcfg_dict1),
        dict(table_cfg=dict(tblcfg_dict1)),
        id='dict-short'
    ),
    pytest.param(
        dict(table_cfg=dict(tblcfg_dict1)),
        dict(table_cfg=dict(tblcfg_dict1)),
        id='dict-full'
    ),
    pytest.param(
        [dict(tblcfg_dict1)],
        [dict(table_cfg=dict(tblcfg_dict1))],
        id='list-with-one-dict'
    ),
    pytest.param(
        [
            dict(table_cfg=dict(tblcfg_dict1)),
            dict(table_cfg=dict(tblcfg_dict2)),
        ],
        [
            dict(table_cfg=dict(tblcfg_dict1)),
            dict(table_cfg=dict(tblcfg_dict2)),
        ],
        id='two_table_cfgs'
    ),
])
def test_parse_reader_cfg(arg, expected):
    # reader
    # selection_cfg
    # table_cfg
    assert expected == parse_reader_cfg(arg)

##__________________________________________________________________||
