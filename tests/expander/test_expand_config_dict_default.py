# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.expander import _expand_config_dict

##__________________________________________________________________||
def expand_abc_cfg(cfg, func_expand_config):
    return dict(abc_cfg=dict(expanded=cfg))

params = [
    pytest.param(
        dict(abc_cfg=dict(A=1, B=2)),
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
            default_dict=dict(abc_cfg=dict(A=10, C=40)),
        ),
        dict(abc_cfg=dict(expanded=dict(A=1, B=2, C=40))),
        id='simple'
    ),

]

@pytest.mark.parametrize('cfg, kwargs, expected', params)
def test_expand_config_dict(cfg, kwargs, expected):
    kwargs['expand_func_map'] = {
        'abc_cfg': expand_abc_cfg,
    }
    actual = _expand_config_dict(cfg, **kwargs)
    assert expected == actual
    assert actual is not cfg

##__________________________________________________________________||
