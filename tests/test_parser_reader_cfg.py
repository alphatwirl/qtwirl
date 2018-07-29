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

selection_cfg_dict = dict(All=('ev: ev.njets[0] > 4', ))
selection_cfg_str = 'ev: ev.njets[0] > 4'

scribbler1 = mock.Mock()

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
        [dict(tblcfg_dict1), dict(tblcfg_dict2)],
        [
            dict(table_cfg=dict(tblcfg_dict1)),
            dict(table_cfg=dict(tblcfg_dict2)),
        ],
        id='two-table-cfgs-short'
    ),
    pytest.param(
        [
            dict(table_cfg=dict(tblcfg_dict1)),
            dict(tblcfg_dict2),
        ],
        [
            dict(table_cfg=dict(tblcfg_dict1)),
            dict(table_cfg=dict(tblcfg_dict2)),
        ],
        id='two-table-cfgs-full-short'
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
        id='two-table-cfgs-full'
    ),
    pytest.param(
        [
            dict(selection_cfg=selection_cfg_dict),
            dict(tblcfg_dict1),
        ],
        [
            dict(selection_cfg=selection_cfg_dict),
            dict(table_cfg=tblcfg_dict1),
        ],
        id='one-selection-dict-one-table'
    ),
    pytest.param(
        [
            dict(selection_cfg=selection_cfg_str),
            dict(tblcfg_dict1),
        ],
        [
            dict(selection_cfg=selection_cfg_str),
            dict(table_cfg=tblcfg_dict1),
        ],
        id='one-selection-str-one-table'
    ),
    pytest.param(
        dict(selection_cfg=selection_cfg_dict),
        dict(selection_cfg=selection_cfg_dict),
        id='one-selection-dict'
    ),
    pytest.param(
        dict(selection_cfg=selection_cfg_str),
        dict(selection_cfg=selection_cfg_str),
        id='one-selection-str'
    ),
    pytest.param(
        [
            dict(reader=scribbler1),
            dict(tblcfg_dict1),
        ],
        [
            dict(reader=scribbler1),
            dict(table_cfg=tblcfg_dict1),
        ],
        id='one-scribbler-one-table'
    ),
])
def test_parse_reader_cfg(arg, expected):
    # reader
    # selection_cfg
    # table_cfg
    assert expected == parse_reader_cfg(arg)

##__________________________________________________________________||
