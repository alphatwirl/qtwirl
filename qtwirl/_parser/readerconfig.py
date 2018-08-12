# Tai Sakuma <tai.sakuma@gmail.com>

from .._misc import is_dict
from .tableconfig import complete_table_cfg
from .selectionconfig import complete_selection_cfg

##__________________________________________________________________||
def expand_reader_config(reader_cfg):
    """expand a reader config into its full form

    Parameters
    ----------
    reader_cfg : dict or list of dicts
        Reader configuration

    Returns
    -------
    dict or list of dicts
        Reader configuration in its full form


    """
    if reader_cfg is None:
        return None

    if is_dict(reader_cfg):
        cfg = _expand_cfg(reader_cfg)
        if not cfg:
            return None
        else:
            return cfg

    # reader_cfg is a list

    ret = [ ]
    for cfg in reader_cfg:
        if cfg is None:
            continue
        cfg = _expand_cfg(cfg)
        if isinstance(cfg, list):
            ret.extend(cfg)
        else:
            ret.append(cfg)

    return ret

def _expand_cfg(cfg):

    cfg = _wrap_table_cfg(cfg)
    # cfg is a dict with one item

    key, val = list(cfg.items())[0]
    if key == 'table_cfg':
        return dict(table_cfg=complete_table_cfg(val))
    elif key == 'selection_cfg':
        return dict(selection_cfg=complete_selection_cfg(val))
    elif key == 'reader':
        return flatten_reader(val)
    return cfg

##__________________________________________________________________||
def _wrap_table_cfg(cfg):
    config_keys = ('table_cfg', 'selection_cfg', 'reader')
    default_config_key = 'table_cfg'
    if len(cfg) == 1 and list(cfg.keys())[0] in config_keys:
        # already wrapped
        return cfg

    return {default_config_key: cfg}

##__________________________________________________________________||
def flatten_reader(reader):
    if isinstance(reader, list) or isinstance(reader, tuple):
        return [dict(reader=r) for r in reader if r is not None]
    return dict(reader=reader)

##__________________________________________________________________||
