# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from qtwirl._parser.expander import expand_config

##__________________________________________________________________||
def test_expand_config_none():
    cfg = None
    mock_func= mock.Mock()
    expected = None
    actual = expand_config(cfg, mock_func)
    assert expected == actual

@pytest.mark.parametrize('cfg', [dict(), dict(A=1)])
@pytest.mark.parametrize('func_ret', [None, [], {}, dict(A=1), [dict(B=2, C=3)]])
def test_expand_config_dict(cfg, func_ret):
    if func_ret:
        expected = func_ret
    else:
        expected = None
    mock_func= mock.Mock()
    mock_func.return_value = func_ret
    actual = expand_config(cfg, mock_func)
    assert expected == actual

@pytest.fixture()
def mock_func():
    ret = mock.Mock()
    ret.return_value = None
    return ret

@pytest.mark.parametrize(
    'cfg, func_side_eff, expected', [
        ([], [], []),
        ([None],[None], []),
        ([None],[dict(X=1)], []),
        ([None],[[]], []),
        ([None],[[dict(X=1)]], []),
        ([None],[[dict(X=1), dict(Y=2)]], []),
        ([dict(A=1)], [None], []),
        ([dict(A=1)], [dict(X=1)], [dict(X=1)]),
        ([dict(A=1)], [[]], []),
        ([dict(A=1)], [[dict(X=1)]], [dict(X=1)]),
        ([dict(A=1)], [[dict(X=1), dict(Y=2)]], [dict(X=1), dict(Y=2)]),
        ([dict(A=1)], [[dict(X=1), dict(Y=2), None]], [dict(X=1), dict(Y=2)]),

        ([dict(A=1), None], [None, dict(X=1)], []),
        ([dict(A=1), None], [dict(X=1), dict(X=1)], [dict(X=1)]),
        ([dict(A=1), None], [[], dict(X=1)], []),
        ([dict(A=1), None], [[dict(X=1)], dict(X=1)], [dict(X=1)]),
        ([dict(A=1), None], [[dict(X=1), dict(Y=2)], dict(X=1)], [dict(X=1), dict(Y=2)]),
        ([dict(A=1), None], [[dict(X=1), dict(Y=2), None], dict(X=1)], [dict(X=1), dict(Y=2)]),

        ([dict(A=1), dict(B=2)], [None, None], []),
        ([dict(A=1), dict(B=2)], [dict(X=1), None], [dict(X=1)]),
        ([dict(A=1), dict(B=2)], [dict(X=1), dict(Y=2)], [dict(X=1), dict(Y=2)]),
        ([dict(A=1), dict(B=2)], [dict(X=1), [dict(Y=2), dict(Z=3)]], [dict(X=1), dict(Y=2), dict(Z=3)]),
        ([dict(A=1), dict(B=2)], [dict(X=1), [dict(Y=2), dict(Z=3), None]], [dict(X=1), dict(Y=2), dict(Z=3)]),

    ]
)
def test_expand_config_list(cfg, func_side_eff, expected):
    mock_func= mock.Mock()
    mock_func.side_effect = func_side_eff
    actual = expand_config(cfg, mock_func)
    assert expected == actual

##__________________________________________________________________||
