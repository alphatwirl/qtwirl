# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

import alphatwirl

from qtwirl._parser.readerconfig import parse_reader_cfg

##__________________________________________________________________||
def mock_complete_table_cfg(cfg):
    return dict(mock_complete_table_cfg=cfg)

@pytest.fixture(autouse=True)
def monkeypatch_complete_table_cfg(monkeypatch):
    from qtwirl._parser import readerconfig
    monkeypatch.setattr(readerconfig, 'complete_table_cfg', mock_complete_table_cfg)

def mock_complete_selection_cfg(cfg):
    return dict(mock_complete_selection_cfg=cfg)

@pytest.fixture(autouse=True)
def monkeypatch_complete_selection_cfg(monkeypatch):
    from qtwirl._parser import readerconfig
    monkeypatch.setattr(readerconfig, 'complete_selection_cfg', mock_complete_selection_cfg)

##__________________________________________________________________||
RoundLog = mock.Mock()

tblcfg_dict1 = dict(
    key_name='jet_pt',
    key_binning=RoundLog(0.1, 100),
    key_index='*',
)


tblcfg_dict2 = dict(
    key_name='met',
    key_binning=RoundLog(0.1, 100),
)

tblcfg_dict1_completed = dict(mock_complete_table_cfg=tblcfg_dict1)
tblcfg_dict2_completed = dict(mock_complete_table_cfg=tblcfg_dict2)

selection_cfg_dict = dict(All=('ev: ev.njets[0] > 4', ))
selection_cfg_str = 'ev: ev.njets[0] > 4'

selection_cfg_dict_completed = dict(mock_complete_selection_cfg=selection_cfg_dict)
selection_cfg_str_completed = dict(mock_complete_selection_cfg=selection_cfg_str)

scribbler1 = mock.Mock()

##__________________________________________________________________||
params = [
    pytest.param(
        dict(), dict(table_cfg=dict(mock_complete_table_cfg=dict())), id='empty-dict'
    ),
    pytest.param(
        [ ], [ ], id='empty-list'
    ),
    pytest.param(
        dict(tblcfg_dict1),
        dict(table_cfg=tblcfg_dict1_completed),
        id='dict-short'
    ),
    pytest.param(
        dict(table_cfg=tblcfg_dict1),
        dict(table_cfg=tblcfg_dict1_completed),
        id='dict-full'
    ),
    pytest.param(
        [tblcfg_dict1],
        [dict(table_cfg=tblcfg_dict1_completed)],
        id='list-with-one-dict'
    ),
    pytest.param(
        [tblcfg_dict1, tblcfg_dict2],
        [
            dict(table_cfg=tblcfg_dict1_completed),
            dict(table_cfg=tblcfg_dict2_completed),
        ],
        id='two-table-cfgs-short'
    ),
    pytest.param(
        [
            dict(table_cfg=tblcfg_dict1),
            dict(tblcfg_dict2),
        ],
        [
            dict(table_cfg=tblcfg_dict1_completed),
            dict(table_cfg=tblcfg_dict2_completed),
        ],
        id='two-table-cfgs-full-short'
    ),
    pytest.param(
        [
            dict(table_cfg=tblcfg_dict1),
            dict(table_cfg=tblcfg_dict2),
        ],
        [
            dict(table_cfg=tblcfg_dict1_completed),
            dict(table_cfg=tblcfg_dict2_completed),
        ],
        id='two-table-cfgs-full'
    ),
    pytest.param(
        [
            dict(selection_cfg=selection_cfg_dict),
            tblcfg_dict1,
        ],
        [
            dict(selection_cfg=selection_cfg_dict_completed),
            dict(table_cfg=tblcfg_dict1_completed),
        ],
        id='one-selection-dict-one-table'
    ),
    pytest.param(
        [
            dict(selection_cfg=selection_cfg_str),
            tblcfg_dict1,
        ],
        [
            dict(selection_cfg=selection_cfg_str_completed),
            dict(table_cfg=tblcfg_dict1_completed),
        ],
        id='one-selection-str-one-table'
    ),
    pytest.param(
        dict(selection_cfg=selection_cfg_dict),
        dict(selection_cfg=selection_cfg_dict_completed),
        id='one-selection-dict'
    ),
    pytest.param(
        dict(selection_cfg=selection_cfg_str),
        dict(selection_cfg=selection_cfg_str_completed),
        id='one-selection-str'
    ),
    pytest.param(
        [
            dict(reader=scribbler1),
            tblcfg_dict1,
        ],
        [
            dict(reader=scribbler1),
            dict(table_cfg=tblcfg_dict1_completed),
        ],
        id='one-scribbler-one-table'
    ),
]

@pytest.mark.parametrize('arg, expected', params)
def test_parse_reader_cfg(arg, expected):
    actual = parse_reader_cfg(arg)
    assert expected == actual

##__________________________________________________________________||
