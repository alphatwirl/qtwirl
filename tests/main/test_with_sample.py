# Tai Sakuma <tai.sakuma@gmail.com>
import os
import numpy as np
import pandas as pd

import pytest

from pandas.util.testing import assert_frame_equal

import alphatwirl

from qtwirl import qtwirl

##__________________________________________________________________||
pytestmark = pytest.mark.filterwarnings('ignore::RuntimeWarning')

##__________________________________________________________________||
TESTDATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

SAMPLE_ROOT_FILE_DIR = os.path.join(TESTDATADIR, 'root')
SAMPLE_ROOT_FILE_NAMES = [
    'sample_chain_01.root',
    'sample_chain_02.root',
    'sample_chain_03_zombie.root',
    'sample_chain_04.root',
]
SAMPLE_ROOT_FILE_PATHS = [os.path.join(SAMPLE_ROOT_FILE_DIR, n) for n in SAMPLE_ROOT_FILE_NAMES]

##__________________________________________________________________||
def test_with_sample_one_dict():

    ##
    sample_paths = SAMPLE_ROOT_FILE_PATHS

    ##
    RoundLog = alphatwirl.binning.RoundLog
    reader_cfg = dict(
        key_name='jet_pt',
        key_binning=RoundLog(0.1, 100),
        key_index='*',
        key_out_name='jet_pt'
    )

    results = qtwirl(
        sample_paths,
        reader_cfg=reader_cfg,
        tree_name='tree',
        process=16,
        quiet=False,
        max_events_per_process=500
    )

    ##
    tbl_dir = os.path.join(TESTDATADIR, 'tbl')
    tbl_path = os.path.join(tbl_dir, '00', 'tbl_n.jet_pt-w.txt')
    tbl = pd.read_table(tbl_path, delim_whitespace=True)

    ##
    assert_frame_equal(tbl, results, check_names=True)

##__________________________________________________________________||
def test_with_sample():

    ##
    sample_paths = SAMPLE_ROOT_FILE_PATHS

    ##
    RoundLog = alphatwirl.binning.RoundLog
    from scribblers.essentials import FuncOnNumpyArrays
    reader_cfg = [
        dict(selection_cfg=dict(All=('ev: ev.njets[0] > 4', ))),
        dict(key_name='jet_pt',
             key_binning=RoundLog(0.1, 100),
             key_index='*',
             key_out_name='jet_pt'),
        dict(key_name='met',
             key_binning=RoundLog(0.1, 100)),
        dict(
            key_name=('njets', 'met'),
            key_binning=(None, RoundLog(0.2, 100, min=50, underflow_bin=0))), # use None
        dict(reader=FuncOnNumpyArrays(
            src_arrays=['jet_pt'],
            out_name='ht',
            func=np.sum)),
        dict(key_name='ht',
             key_binning=RoundLog(0.1, 100)),
    ]

    results = qtwirl(
        sample_paths,
        reader_cfg=reader_cfg,
        tree_name='tree',
        process=16,
        quiet=False,
        max_events_per_process=500
    )

    #
    assert 4 == len(results)

    ##
    tbl_dir = os.path.join(TESTDATADIR, 'tbl')
    tbl_paths = [
        os.path.join(tbl_dir, '01', 'tbl_n.jet_pt-w.txt'),
        os.path.join(tbl_dir, '01', 'tbl_n.met.txt'),
        os.path.join(tbl_dir, '01', 'tbl_n.njets.met.txt'),
        os.path.join(tbl_dir, '01', 'tbl_n.ht.txt'),
    ]
    tbls = [pd.read_table(p, delim_whitespace=True) for p in tbl_paths]

    ##
    assert_frame_equal(tbls[0], results[0], check_names=True)
    assert_frame_equal(tbls[1], results[1], check_names=True, check_less_precise=True)
    assert_frame_equal(tbls[2], results[2], check_names=True)
    assert_frame_equal(tbls[3], results[3], check_names=True)

##__________________________________________________________________||