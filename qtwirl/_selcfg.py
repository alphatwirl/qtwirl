# Tai Sakuma <tai.sakuma@gmail.com>
import os

from ._misc import is_dict

##__________________________________________________________________||
def complete_selection_cfg(cfg):
    """complete a selection config.

    Parameters
    ----------
    cfg : dict
        A table config

    Returns
    -------
    dict
        A completed selection config

    """

    default_cfg = dict(
        count=False,
        store_file=False
    )

    default_file_name = 'tbl_selection_count.txt'

    cfg = _wrap_cfg(cfg)

    ret = default_cfg
    ret.update(cfg)

    if ret['store_file']:
        if 'file_path' not in ret:
            file_dir = ret.get('file_dir', '')
            file_name = ret.get('file_name', default_file_name)
            ret['file_path'] = os.path.join(file_dir, file_name)

    return ret

##__________________________________________________________________||
def _wrap_cfg(cfg):

    if isinstance(cfg, str):
        return dict(condition=cfg)

    if is_dict(cfg):
        if 'condition' not in cfg:
            return dict(condition=cfg)

    return cfg
##__________________________________________________________________||
