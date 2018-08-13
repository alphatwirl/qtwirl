# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._parser.expander import config_expander

##__________________________________________________________________||
def test_config_expander_simple():
    expand_func_map = {'abc_cfg': lambda c : dict(abc_cfg=dict(expanded=c))}
    config_keys = [ ]
    default_config_key = 'abc_cfg'
    expand_config = config_expander(
        expand_func_map = expand_func_map,
        config_keys = config_keys,
        default_config_key = default_config_key
    )

    assert {'abc_cfg': {'expanded': {'A': 1}}} == expand_config(dict(A=1))

##__________________________________________________________________||
