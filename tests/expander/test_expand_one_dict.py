# Tai Sakuma <tai.sakuma@gmail.com>
import logging
import pytest

from qtwirl._parser.expander import _expand_one_dict

##__________________________________________________________________||
params = [
    pytest.param(
        dict(abc_cfg=dict(A=1)),
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(abc_cfg=dict(expanded=dict(A=1))),
        id='simple'
    ),

    pytest.param(
        dict(A=1), # without config key, e.g, 'abc_cfg'
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(abc_cfg=dict(expanded=dict(A=1))),
        id='default'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)), # 'xyz_cfg' is not a config key
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(abc_cfg=dict(expanded=dict(xyz_cfg=dict(A=1)))),
        id='default'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)), # 'xyz_cfg' is a config key
        dict(
            config_keys=['abc_cfg', 'xyz_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(xyz_cfg=dict(A=1)),
        id='no-expansion'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)),
        dict(
            config_keys=['abc_cfg'],
            default_config_key=None, # default is None
        ),
        dict(xyz_cfg=dict(A=1)),
        id='no-default'
    ),

    pytest.param(
        dict(A=1),
        dict(
            config_keys=['abc_cfg', 'xyz_cfg'],
            default_config_key='xyz_cfg',
        ),
        dict(xyz_cfg=dict(A=1)), # not expanded
        id='default-no-expansion'
    ),

    pytest.param(
        dict(A=1),
        dict(
            config_keys=['abc_cfg', 'def_cfg'],
            default_config_key='def_cfg',
        ),
        dict(def_cfg=dict(expanded=dict(A=1))),
        id='no-shared-option' # expand_def_cfg() doesn't take `shared`
    ),

]

def expand_abc_cfg(cfg, shared):
    return dict(abc_cfg=dict(expanded=cfg))

def expand_def_cfg(cfg): # doesn't take shared
    return dict(def_cfg=dict(expanded=cfg))

@pytest.mark.parametrize('cfg, shared, expected', params)
def test_expand_one_dict(cfg, shared, expected):
    shared['expand_func_map'] = {
        'abc_cfg': expand_abc_cfg,
        'def_cfg': expand_def_cfg,
        }
    actual = _expand_one_dict(cfg, shared)
    assert expected == actual
    assert actual is not cfg

##__________________________________________________________________||
params = [
    pytest.param(
        dict(abc_cfg=dict(A=1), xyz=2),
        dict(
            config_keys=['abc_cfg'],
            default_config_key=None, # default None
        ),
        dict(abc_cfg=dict(A=1), xyz=2),
        id='two-items'
    ),

    pytest.param(
        dict(xyz_cfg=dict(A=1)), # 'xyz_cfg' not a config key
        dict(
            config_keys=['abc_cfg'],
            default_config_key=None, # default None
        ),
        dict(xyz_cfg=dict(A=1)),
        id='not-config-key'
    ),
]

@pytest.mark.parametrize('cfg, shared, expected', params)
def test_expand_one_dict_warning(cfg, shared, expected, caplog):
    shared['expand_func_map'] = {
        'abc_cfg': expand_abc_cfg,
        }
    with caplog.at_level(logging.WARNING):
        actual = _expand_one_dict(cfg, shared)

    assert expected == actual
    assert actual is not cfg

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'WARNING'
    assert 'expander' in caplog.records[0].name
    assert 'a config key cannot be determined' in caplog.records[0].msg


##__________________________________________________________________||
params = [
    pytest.param(
        dict(abc_cfg=dict(A=1)),
        dict(
            config_keys=['abc_cfg'],
            default_config_key='abc_cfg',
        ),
        dict(abc_cfg=dict(expanded=dict(shared_applied=dict(A=1)))),
        id='simple'
    ),
]

def apply_shared(cfg, shared):
    ret = cfg.copy()
    if 'abc_cfg' in ret:
        ret['abc_cfg'] = dict(shared_applied=ret['abc_cfg'])
    return ret

@pytest.mark.parametrize('cfg, shared, expected', params)
def test_expand_one_dict_apply(cfg, shared, expected):
    shared['expand_func_map'] = {'abc_cfg': expand_abc_cfg}
    shared['func_apply'] = apply_shared
    actual = _expand_one_dict(cfg, shared)

    assert expected == actual
    assert actual is not cfg

##__________________________________________________________________||
