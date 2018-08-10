# Tai Sakuma <tai.sakuma@gmail.com>
import alphatwirl

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
def compose_tbl_filename(tblcfg, prefix='tbl', suffix='txt',
                         var_separator='.', idx_separator='-'):

    key_out_name = tblcfg['key_out_name']
    key_index = tblcfg.get('key_index', None)

    if not key_out_name:
        return prefix + '.' + suffix # e.g. "tbl_n_component.txt"

    if key_index is None:
        colidxs = key_out_name
        # e.g., ('var1', 'var2', 'var3'),

        middle = var_separator.join(colidxs)
        # e.g., 'var1.var2.var3'

        ret = prefix + var_separator + middle + '.' + suffix
        # e.g., 'tbl_n_component.var1.var2.var3.txt'

        return ret

    # e.g.,
    # key_out_name = ('var1', 'var2', 'var3', 'var4', 'var5'),
    # key_index = (1, None, '*', '(*)', '\\1')

    idx_str = key_index
    # e.g., (1, None, '*', '(*)', '\\1')

    idx_str = ['w' if i == '*' else i for i in idx_str]
    # e..g, [1, None, 'w', '(*)', '\\1']

    idx_str = ['wp' if i == '(*)' else i for i in idx_str]
    # e.g., [1, None, 'w', 'wp', '\\1']

    idx_str = ['b{}'.format(i[1:]) if isinstance(i, str) and i.startswith('\\') else i for i in idx_str]
    # e.g., [1, None, 'w', 'wp', 'b1']

    idx_str = ['' if i is None else '{}{}'.format(idx_separator, i) for i in idx_str]
    # e.g., ['-1', '', '-w', '-wp', '-b1']

    colidxs = [n + i for n, i in zip(key_out_name, idx_str)]
    # e.g., ['var1-1', 'var2', 'var3-w', 'var4-wp', 'var5-b1']

    middle = var_separator.join(colidxs)
    # e.g., 'var1-1.var2.var3-w.var4-wp.var5-b1'

    ret =  prefix + var_separator + middle + '.' + suffix
    # e.g., tbl_n_component.var1-1.var2.var3-w.var4-wp.var5-b1.txt

    return ret

##__________________________________________________________________||
