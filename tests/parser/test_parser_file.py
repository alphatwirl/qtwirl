# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from qtwirl._parser.input import parse_file

##__________________________________________________________________||
@pytest.mark.parametrize('arg, expected', [
    pytest.param(['A.root', 'B.root'], ['A.root', 'B.root'], id='list'),
    pytest.param('A.root', ['A.root'], id='string'),
    pytest.param([ ], [ ], id='empty-list'),
    pytest.param('', [ ], id='empty-string'),
])
def test_parse_file(arg, expected):
    assert expected == parse_file(arg)

##__________________________________________________________________||
