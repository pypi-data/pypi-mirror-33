"""
Make sure to run with `python -m pytest` instead of `pytest`. That
way the root project directory is added to sys.path.
"""

from encase import Encase


def test_list_of_encase_instances():
    e_one = Encase()
    e_two = Encase()
    e_three = Encase()

    e_one.value1 = 'Value 1'
    e_two.value2 = 'Value 2'
    e_three.value3 = 'Value 3'

    L = [e_one, e_two, e_three]
    assert L[0].value1 == 'Value 1'
    assert L[1].value2 == 'Value 2'
    assert L[2].value3 == 'Value 3'


def test_nested_encase_instances():
    parent = Encase()
    parent.child = Encase()
    parent.child.grandchild = Encase()

    parent.child.grandchild.name = 'Ryan'
    assert parent.child.grandchild.name == 'Ryan'


def test_nested_mix_encase_lists():
    parent = Encase()
    parent.L = []
    parent.L.append(Encase())
    parent.L[0].test = 'Example Value'
    assert parent.L[0].test == 'Example Value'


def test_existing_dict_to_encase():
    d = {
        'key1': 'Value 1',
        'key2': 'Value 2',
        'key3': 'Value 3'
    }
    e = Encase(d)
    assert e.key1 == 'Value 1'
    assert e.key2 == 'Value 2'
    assert e.key3 == 'Value 3'


def test_existing_complex_object_to_encase():
    d = {
        'key1': ['list_object_1', 'list_object_2', 'list_object_3'],
        'key2': [
            {'child': 'Test Value 1'},
            {'child': 'Test Value 2'}
        ]
    }
    e = Encase(d)

    assert e.key1[0] == 'list_object_1'
    assert e.key1[1] == 'list_object_2'
    assert e.key1[2] == 'list_object_3'
    assert e.key2[0].child == 'Test Value 1'
    assert e.key2[1].child == 'Test Value 2'
