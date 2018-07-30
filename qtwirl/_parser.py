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

    defaultSummaryClass = alphatwirl.summary.Count
    defaultWeight = alphatwirl.summary.WeightCalculatorOne()

    default_cfg = dict(
        keyAttrNames=( ),
        keyIndices=None,
        binnings=None,
        valAttrNames=None,
        valIndices=None,
        summaryClass=defaultSummaryClass,
        weight=defaultWeight,
        sort=True,
        nevents=None,
    )

    ret = default_cfg
    ret.update(cfg)

    use_defaultSummaryClass = 'summaryClass' not in cfg

    ret['keyOutColumnNames'] = ret.get('keyOutColumnNames', ret['keyAttrNames'])
    # TODO: this line is not tested well. The following code also passes the tests
    # ret['keyOutColumnNames'] = ret.get('keyAttrNames', ret['keyAttrNames'])

    if 'valOutColumnNames' not in ret:
        if use_defaultSummaryClass:
            ret['valOutColumnNames'] = ('n', 'nvar')
        else:
            ret['valOutColumnNames'] = ret['valAttrNames'] if ret['valAttrNames'] is not None else ()

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
