# Tai Sakuma <tai.sakuma@gmail.com>
import functools

from .expander import config_expander

from .tableconfig import complete_table_cfg
from .selectionconfig import complete_selection_cfg

##__________________________________________________________________||
def expand_table_cfg(cfg):
    return dict(table_cfg=complete_table_cfg(cfg))

def expand_selection_cfg(cfg):
    return dict(selection_cfg=complete_selection_cfg(cfg))

def expand_reader(reader):
    if isinstance(reader, list) or isinstance(reader, tuple):
        return [dict(reader=r) for r in reader if r is not None]
    return dict(reader=reader)

expand_func_map = {
    'table_cfg': expand_table_cfg,
    'selection_cfg': expand_selection_cfg,
    'reader': expand_reader,
}

default_config_key = 'table_cfg'

##__________________________________________________________________||
expand_reader_config = config_expander(
    expand_func_map=expand_func_map,
    default_config_key=default_config_key
)

##__________________________________________________________________||
