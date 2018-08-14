# Tai Sakuma <tai.sakuma@gmail.com>
"""

A generic tool to expand config written in dict and a list of dict.

This module is not specific to qtwirl and might become an independent
package in the future.


"""

import functools

from .._misc import is_dict

##__________________________________________________________________||
def config_expander(expand_func_map=None, config_keys=None,
                    default_config_key=None):
    """return a function that expands a config

    Parameters
    ----------
    expand_func_map : dict, optional
        A map from a config key to a function that expands the config
        for the key

    config_keys : list, optional
        A list of extra config keys that are not in keys of
        ``expand_func_map``.

    default_config_key: str, optional
        A default key

    Returns
    -------
    function
        A function that expands a config

    """

    if expand_func_map is None:
        expand_func_map = {}

    if config_keys is None:
        config_keys = []

    config_keys =set(config_keys)
    config_keys.update(expand_func_map.keys())

    if default_config_key is not None:
        config_keys.add(default_config_key)

    func_expand_config_dict = functools.partial(
        _expand_config_dict,
        expand_func_map=expand_func_map,
        config_keys=config_keys,
        default_config_key=default_config_key
    )
    functools.update_wrapper(func_expand_config_dict, _expand_config_dict)

    ret_pre = functools.partial(
        expand_config,
        func_expand_config_dict=func_expand_config_dict
    )

    ret = functools.partial(ret_pre, func_self=ret_pre)
    return ret

##__________________________________________________________________||
def expand_config(cfg, func_expand_config_dict,
                  default_dict=None, func_self=None):
    """expand a config into its full form

    Parameters
    ----------
    cfg : dict, None, or list of dicts and None
        Configuration

    func_expand_config_dict : function
        A function that expands a config dict

    default_dict : dict, optional

    func_self : function, optional
        A function that expands a config, to be used for recursive
        call, e.g., this function with ``func_expand_config_dict``
        determined by ``funtools.partial()``.

    Returns
    -------
    dict, list of dicts, or None
        Configuration in its full form

    """

    if cfg is None:
        return None

    func_self = functools.partial(func_self, func_self=func_self)

    if is_dict(cfg):
        cfg = func_expand_config_dict(
            cfg, default_dict=default_dict, func_expand_config=func_self)
        if not cfg:
            return None
        return cfg

    # cfg is a list of dicts and None

    ret = [ ]
    for c in cfg:
        if c is None:
            continue
        c = func_expand_config_dict(
            c, default_dict=default_dict, func_expand_config=func_self)

        if c is None:
            continue

        if isinstance(c, list):
            c = [e for e in c if e is not None]
            ret.extend(c)
        else:
            ret.append(c)

    return ret

##__________________________________________________________________||
def _expand_config_dict(
        cfg, expand_func_map, config_keys, default_config_key,
        default_cfg_stack=None, func_expand_config=None):
    """expand a piece of config

    Parameters
    ----------
    cfg : dict
        Configuration
    expand_func_map : dict
    config_keys : list
    default_config_key: str
    default_cfg_stack : list of dict
    func_expand_config : function

    Returns
    -------
    dict, list
        Expanded configuration

    """

    config_keys = set(config_keys)
    config_keys.add('default')

    #
    if len(cfg) == 1 and list(cfg.keys())[0] in config_keys:
        # the only key is one of the config keys
        key, val = list(cfg.items())[0]
    elif default_config_key is not None:
        key = default_config_key
        val = cfg
    else:
        # key isn't determined. return a copy
        return dict(cfg) # copy

    #
    if default_cfg_stack is None:
        default_cfg_stack = [ ]

    #
    # if key == 'default':
    #     new_default_dict = default_dict.copy()
    #     for k, v in val[0].items():
    #         new_default_dict[k] = new_default_dict.get(k, {})
    #         new_default_dict[k].update(v)
    #     return func_expand_config(val[1], default_dict=new_default_dict)

    new_val = {}
    for default_cfg in default_cfg_stack:
        new_val.update(default_cfg.get(key, {}))
        new_val.update(val)
    val = new_val

    #
    if key in expand_func_map:
        expand_func = expand_func_map[key]
        return expand_func(val)

    return {key: val}

##__________________________________________________________________||
