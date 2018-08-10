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
