# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._parser.expander import config_expander


##__________________________________________________________________||
def propagate_default(cfg, func_expand_config):
    print cfg
    print func_expand_config
    print func_expand_config.func
    print func_expand_config.args
    print func_expand_config.keywords
    pass

def expand_abc_cfg(cfg):
    return dict(abc_cfg=dict(expanded=cfg))

##__________________________________________________________________||
def test_config_expander():
    expand_func_map = {
        'abc_cfg': expand_abc_cfg,
        ## 'default': propagate_default,
    }
    config_keys = [ ]
    default_config_key = 'abc_cfg'
    expand_config=config_expander(
        expand_func_map=expand_func_map,
        config_keys=config_keys,
        default_config_key=default_config_key
    )

    cfg = dict(
        default=(
            dict(abc_cfg=dict(A=5, C=4)),
            dict(A=1, B=2)
        )
    )
    expected = {'abc_cfg': {'expanded': dict(A=1, B=2, C=4)}}
    assert expected == expand_config(cfg)

    cfg = dict(
        default=(
            dict(abc_cfg=dict(B=3, C=2, E=8)),
            dict(
                default=(
                    dict(abc_cfg=dict(A=5, C=4)),
                    dict(A=1, B=2)
            )))
    )
    expected = {'abc_cfg': {'expanded': dict(A=1, B=2, C=4, E=8)}}
    assert expected == expand_config(cfg)

##__________________________________________________________________||