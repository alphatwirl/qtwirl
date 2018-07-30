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
    ret = cfg.copy()

    defaultSummaryClass = alphatwirl.summary.Count
    defaultWeight = alphatwirl.summary.WeightCalculatorOne()
    createOutFileName = alphatwirl.configure.TableFileNameComposer()
    defaultOutDir = '.'

    if 'keyAttrNames' not in ret: ret['keyAttrNames'] = ( )
    if 'binnings' not in ret: ret['binnings'] = None

    use_defaultSummaryClass = 'summaryClass' not in ret
    if use_defaultSummaryClass:
        ret['summaryClass'] = defaultSummaryClass

    if 'keyOutColumnNames' not in ret: ret['keyOutColumnNames'] = ret['keyAttrNames']
    if 'keyIndices' not in ret: ret['keyIndices'] = None
    if 'valAttrNames' not in ret: ret['valAttrNames'] = None

    if 'valOutColumnNames' not in ret:
        if use_defaultSummaryClass:
            ret['valOutColumnNames'] = ('n', 'nvar')
        else:
            ret['valOutColumnNames'] = ret['valAttrNames'] if ret['valAttrNames'] is not None else ()

    if 'valIndices' not in ret: ret['valIndices'] = None
    if 'outFile' not in ret: ret['outFile'] = True
    if 'weight' not in ret: ret['weight'] = defaultWeight
    if 'sort' not in ret: ret['sort'] = True
    if 'nevents' not in ret: ret['nevents'] = None
    if ret['outFile']:
        if 'outFileName' not in ret:
            if use_defaultSummaryClass:
                ret['outFileName'] = createOutFileName(
                    ret['keyOutColumnNames'], ret['keyIndices']
                )
            else:
                keyOutColumnNames  = ret['keyOutColumnNames'] if ret['keyOutColumnNames'] is not None else ()
                keyIndices = ret['keyIndices'] if ret['keyIndices'] is not None else (None, )*len(keyOutColumnNames)
                valOutColumnNames  = ret['valOutColumnNames'] if ret['valOutColumnNames'] is not None else ()
                valIndices = ret['valIndices'] if ret['valIndices'] is not None else (None, )*len(valOutColumnNames)
                ret['outFileName'] = createOutFileName(
                    keyOutColumnNames + valOutColumnNames,
                    keyIndices + valIndices,
                    prefix='tbl_{}'.format(ret['summaryClass'].__name__)
                )
        if 'outFilePath' not in ret: ret['outFilePath'] = os.path.join(defaultOutDir, ret['outFileName'])
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
