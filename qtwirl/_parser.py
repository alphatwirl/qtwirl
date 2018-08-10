# Tai Sakuma <tai.sakuma@gmail.com>
import os
import alphatwirl

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
        cfg = _wrap_table_cfg(reader_cfg)
        cfg = _expand_cfg(cfg)
        if not cfg:
            return None
        else:
            return cfg

    # reader_cfg is a list

    ret = [ ]
    for cfg in reader_cfg:
        if cfg is None:
            continue
        cfg = _wrap_table_cfg(cfg)
        cfg = _expand_cfg(cfg)
        if isinstance(cfg, list):
            ret.extend(cfg)
        else:
            ret.append(cfg)

    return ret

def _expand_cfg(cfg):
    # cfg: a dict with one item
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
def complete_table_cfg(cfg):

    default_agg_class = alphatwirl.summary.Count
    default_vocn_for_default_agg_class = ('n', 'nvar')

    default_weight = alphatwirl.summary.WeightCalculatorOne()

    default_cfg = dict(
        key_name=( ),
        key_index=None,
        key_binning=None,
        val_name=None,
        val_index=None,
        agg_class=default_agg_class,
        weight=default_weight,
        sort=True,
        nevents=None,
    )

    ret = default_cfg
    ret.update(cfg)

    ret['key_out_name'] = ret.get('key_out_name', ret['key_name'])

    if isinstance(ret['key_name'], str):
        ret['key_name'] = (ret['key_name'], )
        ret['key_out_name'] = (ret['key_out_name'], )
        if ret['key_index'] is not None:
            ret['key_index'] = (ret['key_index'], )
        if ret['key_binning'] is not None:
            ret['key_binning'] = (ret['key_binning'], )

    if isinstance(ret['val_name'], str):
        ret['val_name'] = (ret['val_name'], )
        if ret['val_index'] is not None:
            ret['val_index'] = (ret['val_index'], )

    use_default_agg_class = 'agg_class' not in cfg
    if 'agg_name' not in ret:
        if use_default_agg_class:
            ret['agg_name'] = default_vocn_for_default_agg_class
        else:
            ret['agg_name'] = ret['val_name'] if ret['val_name'] is not None else ()

    if isinstance(ret['agg_name'], str):
        ret['agg_name'] = (ret['agg_name'], )

    return ret

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
