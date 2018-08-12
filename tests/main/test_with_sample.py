# Tai Sakuma <tai.sakuma@gmail.com>
import os
import numpy as np
import pandas as pd

import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from pandas.util.testing import assert_frame_equal

import alphatwirl

from qtwirl import qtwirl

##__________________________________________________________________||
pytestmark = pytest.mark.filterwarnings('ignore::RuntimeWarning')

##__________________________________________________________________||
def test_with_sample_one_dict():

    ##
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    sample_basenames = [
        'sample_chain_01.root',
        'sample_chain_02.root',
        'sample_chain_03_zombie.root',
        'sample_chain_04.root',
    ]
    sample_paths = [os.path.join(sample_dir, b) for b in sample_basenames]

    ##
    tbl_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tbl')
    tbl_paths = [
        os.path.join(tbl_dir, '00', 'tbl_n.jet_pt-w.txt'),
        os.path.join(tbl_dir, '00', 'tbl_n.met.txt'),
    ]
    tbls = [pd.read_table(p, delim_whitespace=True) for p in tbl_paths]

    ##
    RoundLog = alphatwirl.binning.RoundLog
    reader_cfg = dict(
        key_name=('jet_pt', ),
        key_binning=(RoundLog(0.1, 100), ),
        key_index=('*', ),
        key_out_name=('jet_pt', ))

    results = qtwirl(
        file=sample_paths,
        reader_cfg=reader_cfg,
        tree_name='tree',
        process=16,
        quiet=False,
        max_events_per_process=500
    )

    ##
    assert_frame_equal(tbls[0], results, check_names=True)

##__________________________________________________________________||
def test_with_sample():

    ##
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    sample_basenames = [
        'sample_chain_01.root',
        'sample_chain_02.root',
        'sample_chain_03_zombie.root',
        'sample_chain_04.root',
    ]
    sample_paths = [os.path.join(sample_dir, b) for b in sample_basenames]

    ##
    tbl_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tbl')
    tbl_paths = [
        os.path.join(tbl_dir, '01', 'tbl_n.jet_pt-w.txt'),
        os.path.join(tbl_dir, '01', 'tbl_n.met.txt'),
        os.path.join(tbl_dir, '01', 'tbl_n.njets.met.txt'),
        os.path.join(tbl_dir, '01', 'tbl_n.ht.txt'),
    ]
    tbls = [pd.read_table(p, delim_whitespace=True) for p in tbl_paths]

    ##
    RoundLog = alphatwirl.binning.RoundLog
    from scribblers.essentials import FuncOnNumpyArrays
    reader_cfg = [
        dict(selection_cfg=dict(All=('ev: ev.njets[0] > 4', ))),
        dict(key_name=('jet_pt', ),
             key_binning=(RoundLog(0.1, 100), ),
             key_index=('*', ),
             key_out_name=('jet_pt', )),
        dict(key_name=('met', ),
             key_binning=(RoundLog(0.1, 100), )),
        dict(
            key_name=('njets', 'met'),
            key_binning=(None, RoundLog(0.2, 100, min=50, underflow_bin=0))), # use None
        dict(reader=FuncOnNumpyArrays(
            src_arrays=['jet_pt'],
            out_name='ht',
            func=np.sum)),
        dict(key_name=('ht', ),
             key_binning=(RoundLog(0.1, 100), )),
    ]

    results = qtwirl(
        file=sample_paths,
        reader_cfg=reader_cfg,
        tree_name='tree',
        process=16,
        quiet=False,
        max_events_per_process=500
    )

    #
    assert 4 == len(results)

    ##
    assert_frame_equal(tbls[0], results[0], check_names=True)
    assert_frame_equal(tbls[1], results[1], check_names=True, check_less_precise=True)
    assert_frame_equal(tbls[2], results[2], check_names=True)
    assert_frame_equal(tbls[3], results[3], check_names=True)

##__________________________________________________________________||
