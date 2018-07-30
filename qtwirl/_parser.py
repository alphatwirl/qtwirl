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

    if _is_dict(reader_cfg):
        return _wrap_table_cfg(reader_cfg)

    ret = [_wrap_table_cfg(c) for c in reader_cfg]

    return ret

def _wrap_table_cfg(cfg):
    config_keys = ('table_cfg', 'selection_cfg', 'reader')
    default_config_key = 'table_cfg'
    if len(cfg) == 1 and list(cfg.keys())[0] in config_keys:
        # already wrapped
        return cfg

    return {default_config_key: cfg}

##__________________________________________________________________||
def complete_table_cfg(cfg):

    default_summary_class = alphatwirl.summary.Count
    default_vocn_for_default_summary_class = ('n', 'nvar')

    default_weight = alphatwirl.summary.WeightCalculatorOne()

    default_cfg = dict(
        keyAttrNames=( ),
        keyIndices=None,
        binnings=None,
        valAttrNames=None,
        valIndices=None,
        summaryClass=default_summary_class,
        weight=default_weight,
        sort=True,
        nevents=None,
    )

    ret = default_cfg
    ret.update(cfg)

    ret['keyOutColumnNames'] = ret.get('keyOutColumnNames', ret['keyAttrNames'])

    if isinstance(ret['keyAttrNames'], str):
        ret['keyAttrNames'] = (ret['keyAttrNames'], )
        ret['keyOutColumnNames'] = (ret['keyOutColumnNames'], )
        if ret['keyIndices'] is not None:
            ret['keyIndices'] = (ret['keyIndices'], )
        if ret['binnings'] is not None:
            ret['binnings'] = (ret['binnings'], )

    if isinstance(ret['valAttrNames'], str):
        ret['valAttrNames'] = (ret['valAttrNames'], )
        if ret['valIndices'] is not None:
            ret['valIndices'] = (ret['valIndices'], )

    use_default_summary_class = 'summaryClass' not in cfg
    if 'summaryColumnNames' not in ret:
        if use_default_summary_class:
            ret['summaryColumnNames'] = default_vocn_for_default_summary_class
        else:
            ret['summaryColumnNames'] = ret['valAttrNames'] if ret['valAttrNames'] is not None else ()

    if isinstance(ret['summaryColumnNames'], str):
        ret['summaryColumnNames'] = (ret['summaryColumnNames'], )

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
