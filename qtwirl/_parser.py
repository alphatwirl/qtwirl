# Tai Sakuma <tai.sakuma@gmail.com>

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

def _wrap_table_cfg(cfg):
    config_keys = ('table_cfg', 'selection_cfg', 'reader')
    default_config_key = 'table_cfg'
    if len(cfg) == 1 and list(cfg.keys())[0] in config_keys:
        # already wrapped
        return cfg

    return {default_config_key: cfg}

##__________________________________________________________________||
