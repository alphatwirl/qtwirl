# Tai Sakuma <tai.sakuma@gmail.com>
import functools

from .._misc import is_dict

##__________________________________________________________________||
def config_expander(expand_func_map, default_config_key):
    return functools.partial(
        expand_config,
        func_expand_config_dict=functools.partial(
            _expand_config_dict,
            expand_func_map=expand_func_map,
            default_config_key=default_config_key
        ))

##__________________________________________________________________||
def expand_config(cfg, func_expand_config_dict):
    """expand a config into its full form

    Parameters
    ----------
    cfg : dict, None, or list of dicts and None
        Configuration

    Returns
    -------
    dict, list of dicts, or None
        Configuration in its full form


    """
    if cfg is None:
        return None

    if is_dict(cfg):
        cfg = func_expand_config_dict(cfg)
        if not cfg:
            return None
        return cfg

    # cfg is a list of dicts and None

    ret = [ ]
    for c in cfg:
        if c is None:
            continue
        c = func_expand_config_dict(c)
        if isinstance(c, list):
            ret.extend(c)
        else:
            ret.append(c)

    return ret

##__________________________________________________________________||
def _expand_config_dict(cfg, expand_func_map, default_config_key):

    config_keys = tuple(expand_func_map.keys())

    #
    if len(cfg) == 1 and list(cfg.keys())[0] in config_keys:
        # the only key is one of the config keys
        key, val = list(cfg.items())[0]
    else:
        key = default_config_key
        val = cfg
        # in other words, wrap cfg with the default config key
        # e.g., cfg = {default_config_key: cfg}

    #
    return expand_func_map[key](val)

##__________________________________________________________________||
