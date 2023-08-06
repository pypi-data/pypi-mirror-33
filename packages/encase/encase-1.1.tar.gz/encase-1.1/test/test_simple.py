"""
Make sure to run with `python -m pytest` instead of `pytest`. That
way the root project directory is added to sys.path.
"""

import pytest

from encase import Encase


def test_get_dot_notation():
    e = Encase({'test': 'value'})
    assert e.test == 'value'


def test_set_dot_notation():
    e = Encase()
    e.new_value = 'New Value'
    assert e['new_value'] == 'New Value'


def test_get_method():
    e = Encase({'test': 'value'})
    assert e.get('test') == 'value'


def test_set_method():
    e = Encase()
    e.set('test_key', 'Example Value')
    assert e['test_key'] == 'Example Value'


def test_set_value_as_list():
    e = Encase()
    L = ['value1', 'value2', 'value3']
    e.new_list = L
    assert e.new_list[0] == 'value1'
    assert e.new_list[1] == 'value2'
    assert e.new_list[2] == 'value3'


def test_method_overwrite_prevention():
    e = Encase()
    with pytest.raises(AttributeError):
        e.copy = 'Some Value'
