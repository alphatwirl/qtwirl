# Tai Sakuma <tai.sakuma@gmail.com>

from ._tblcfg import complete_table_cfg

##__________________________________________________________________||
def parse_file(file):
    if isinstance(file, str):
        if not file: # empty string, i.e., ''
            return [ ]
        return [file]
    return file

##__________________________________________________________________||
def parse_reader_cfg(reader_cfg):

    if reader_cfg is None:
        return None

    if _is_dict(reader_cfg):
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
def _is_dict(obj):
    try:
        # check for mixin methods of mapping
        # https://docs.python.org/3.6/library/collections.abc.html
        obj.keys()
        obj.items()
        obj.values()
    except AttributeError:
        return False

    return True

##__________________________________________________________________||
