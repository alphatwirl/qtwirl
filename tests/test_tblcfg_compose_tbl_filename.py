# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._tblcfg import compose_tbl_filename

##__________________________________________________________________||
params = [
    pytest.param(
        [dict(key_out_name=('var1', 'var2', 'var3'))], { },
        'tbl.var1.var2.var3.txt',
        id='no-indices'),
    pytest.param(
        [dict(
            key_out_name=('var1', 'var2', 'var3'),
            key_index=(1, None, 2)
        )], { },
        'tbl.var1-1.var2.var3-2.txt',
        id='simple'),
    pytest.param(
        [dict(
            key_out_name=('var1', 'var2', 'var3'),
            key_index=(1, None, 2)
        )],
        dict(prefix='tbl_Sum'),
        'tbl_Sum.var1-1.var2.var3-2.txt',
        id='prefix'),
    pytest.param(
        [dict(
            key_out_name=('var1', 'var2', 'var3'),
            key_index=(1, None, 2)
        )],
        dict(suffix='hdf5'),
        'tbl.var1-1.var2.var3-2.hdf5',
        id='suffix'),
    pytest.param(
        [dict(key_out_name=( ), key_index=( ))], dict(), 'tbl.txt',
        id='empty'),
    pytest.param(
        [dict(
            key_out_name=('var1', 'var2', 'var3'),
            key_index=(1, None, '*')
        )],
        dict(),
        'tbl.var1-1.var2.var3-w.txt',
        id='star'),
    pytest.param(
        [dict(
            key_out_name=('var1', 'var2', 'var3', 'var4', 'var5'),
            key_index=(1, None, '*', '(*)', '\\1')
        )],
        dict(),
        'tbl.var1-1.var2.var3-w.var4-wp.var5-b1.txt',
        id='backref'),
    pytest.param(
        [dict(
            key_out_name=('var1', 'var2', 'var3', 'var4', 'var5'),
            key_index=(1, None, '*', '(*)', '\\1')
        )],
        dict(var_separator='#'),
        'tbl#var1-1#var2#var3-w#var4-wp#var5-b1.txt',
        id='var-separator'),
    pytest.param(
        [dict(
            key_out_name=('var1', 'var2', 'var3', 'var4', 'var5'),
            key_index=(1, None, '*', '(*)', '\\1')
        )],
        dict(idx_separator='#'),
        'tbl.var1#1.var2.var3#w.var4#wp.var5#b1.txt',
        id='idx-separator'),
]

@pytest.mark.parametrize('args, kwargs, expected', params)
def test_complete(args, kwargs, expected):
    actual = compose_tbl_filename(*args, **kwargs)
    assert expected == actual

##__________________________________________________________________||
