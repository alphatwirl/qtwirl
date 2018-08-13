# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.expander import _expand_config_dict

##__________________________________________________________________||
params = [
    pytest.param(
        dict(abc_cfg=dict(A=1)),
        ['abc_cfg'],
        'abc_cfg',
        dict(abc_cfg=dict(expanded=dict(A=1))),
        id='simple'
    ),

    pytest.param(
        dict(A=1),
        ['abc_cfg'],
        'abc_cfg',
        dict(abc_cfg=dict(expanded=dict(A=1))),
        id='default'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)),
        ['abc_cfg'],
        'abc_cfg',
        dict(abc_cfg=dict(expanded=dict(xyz_cfg=dict(A=1)))),
        id='default'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)),
        ['abc_cfg', 'xyz_cfg'],
        'abc_cfg',
        dict(xyz_cfg=dict(A=1)),
        id='no-expansion'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)),
        ['abc_cfg'],
        None,
        dict(xyz_cfg=dict(A=1)),
        id='no-default'
    ),

    pytest.param(
        dict(A=1),
        ['abc_cfg', 'xyz_cfg'],
        'xyz_cfg',
        dict(xyz_cfg=dict(A=1)),
        id='default-no-expansion'
    ),

]

@pytest.mark.parametrize('cfg, config_keys, default_config_key, expected', params)
def test_expand_config_dict(cfg, config_keys, default_config_key, expected):
    expand_func_map = {
        'abc_cfg': lambda c : dict(abc_cfg=dict(expanded=c)),
        }
    actual = _expand_config_dict(cfg, expand_func_map, config_keys, default_config_key)
    assert expected == actual
    assert actual is not cfg

##__________________________________________________________________||
