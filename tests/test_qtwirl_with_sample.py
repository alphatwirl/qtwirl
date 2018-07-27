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
def test_with_sample():

    ##
    sample_dir = os.path.join(os.path.dirname(__file__), 'data')
    sample_basenames = [
        'sample_chain_01.root',
        'sample_chain_02.root',
        'sample_chain_03_zombie.root',
        'sample_chain_04.root',
    ]
    sample_paths = [os.path.join(sample_dir, b) for b in sample_basenames]

    ##
    tbl_dir = os.path.join(os.path.dirname(__file__), 'tbl')
    tbl_paths = [
        os.path.join(tbl_dir, 'tbl_n.jet_pt-w.txt'),
        os.path.join(tbl_dir, 'tbl_n.met.txt')
    ]
    tbls = [pd.read_table(p, delim_whitespace=True) for p in tbl_paths]

    ##
    RoundLog = alphatwirl.binning.RoundLog
    reader_cfg = dict(
        summarizer=[
            dict(keyAttrNames=('jet_pt', ),
                 binnings=(RoundLog(0.1, 100), ),
                 keyIndices=('*', ),
                 keyOutColumnNames=('jet_pt', )),
            dict(keyAttrNames=('met', ),
                 binnings=(RoundLog(0.1, 100), )),
        ])

    results = qtwirl(
        file=sample_paths,
        reader_cfg=reader_cfg,
        tree_name='tree',
        process=16,
        quiet=False,
        max_events_per_process=500
    )

    ##
    assert_frame_equal(tbls[0], results[0], check_names=True)
    assert_frame_equal(tbls[1], results[1], check_names=True, check_less_precise=True)

##__________________________________________________________________||
