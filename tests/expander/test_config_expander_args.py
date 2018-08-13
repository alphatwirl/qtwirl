# Tai Sakuma <tai.sakuma@gmail.com>
import sys
import functools
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.expander import config_expander

##__________________________________________________________________||
@pytest.fixture()
def mock_funtools(monkeypatch):
    ret = mock.Mock()
    module = sys.modules['qtwirl._parser.expander']
    monkeypatch.setattr(module, 'functools', ret)
    return ret

params = [
    pytest.param(
        dict(),
        dict(expand_func_map={}, config_keys=set([]), default_config_key=None),
        id='empty'),

    pytest.param(
        dict(expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg}),
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=set(['abc_cfg']), default_config_key=None),
        id='empty-config-keys'),

    pytest.param(
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=['def_cfg']
        ),
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=set(['abc_cfg', 'def_cfg']), default_config_key=None),
        id='default-none'),

    pytest.param(
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=['def_cfg'], default_config_key='abc_cfg'
        ),
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=set(['abc_cfg', 'def_cfg']),
            default_config_key='abc_cfg'),
        id='default-in-list'),

    pytest.param(
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=['def_cfg'], default_config_key='xyz_cfg'
        ),
        dict(
            expand_func_map={'abc_cfg': mock.sentinel.expand_abc_cfg},
            config_keys=set(['abc_cfg', 'def_cfg', 'xyz_cfg']),
            default_config_key='xyz_cfg'),
        id='default-not-in-list'),
]

@pytest.mark.parametrize('kwargs, expected', params)
def test_config_expander_args_to_expand_config_dict(
        kwargs, expected, mock_funtools) :
    """test if args to expand_config_dict() are correctly initialized

    """

    config_expander(**kwargs)
    args_to_expand_config_dict = mock_funtools.partial.call_args_list[0][1]
    assert expected == args_to_expand_config_dict

##__________________________________________________________________||
