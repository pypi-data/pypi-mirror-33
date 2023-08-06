import pytest

from wattle import Integer, Boolean, Float, String, load_schema, Choice
from wattle.exceptions import InvalidValueError
from wattle.nodes import Dict, ParentReference, Nested, List, Union


@pytest.mark.parametrize('field, value, expected_value, raises', [
    (Integer(), 10, 10, False),
    (Integer(), '10', 10, False),
    (Integer(), 'false', None, True),
    (Float(), 3.14, 3.14, False),
    (Float(), '3.14', 3.14, False),
    (Float(), 'pi', None, True),
    (String(), 10, '10', False),
    (String(), 100.11, '100.11', False),
    (String(), 'test', 'test', False),
    (String(), False, 'False', False),
    (Boolean(), 0, False, False),
    (Boolean(), 1, True, False),
    (Boolean(), 'test', True, False),
    (Boolean(), '', False, False),
    (Boolean(), False, False, False),
    (Boolean(), True, True, False),
    (Boolean(), None, False, False),
    (Dict(), {'a': 1}, {'a': 1}, False),
    (Dict(), [('a', 1)], {'a': 1}, False),
    (Dict(), {'a': 1, 'b': 2}, {'a': 1, 'b': 2}, False),
    (Dict(), 3, None, True),
])
def test_value_field(field, value, expected_value, raises):
    class Schema:
        myval = field

    schema = load_schema(Schema)
    if raises:
        with pytest.raises(InvalidValueError):
            _ = schema.read_dict({'myval': value})
    else:
        obj = schema.read_dict({'myval': value})
        assert obj.myval == expected_value


@pytest.mark.parametrize('field, default', [
    (Integer(default=3), 3),
    (String(default="a"), "a"),
    (Float(default=10.1), 10.1),
    (Boolean(default=True), True),
    (Dict(default=lambda: {'a': 3}), {'a': 3}),
])
def test_value_field_with_default(field, default):
    class Schema:
        myval = field

    schema = load_schema(Schema)
    obj = schema.read_dict({})
    assert obj.myval == default


def test_choice_field():
    class Schema:
        myval = Choice(['a', 'b', 'c'])

    schema = load_schema(Schema)
    obj = schema.read_dict({'myval': 'a'})
    assert obj.myval == 'a'
    with pytest.raises(InvalidValueError):
        _ = schema.read_dict({'myval': 'd'})
    obj = schema.read_dict({})
    assert obj.myval == 'a'


def test_parent_reference_field():
    class Layer2:
        parent = ParentReference()
        name = String()

    class Layer1:
        layer2 = Nested(Layer2)
        name = String()

    schema = load_schema(Layer1)
    obj = schema.read_dict({'name': 'layer1', 'layer2': {'name': 'layer2'}})
    assert isinstance(obj, Layer1)
    assert isinstance(obj.layer2, Layer2)
    assert obj.name == 'layer1'
    assert obj.layer2.name == 'layer2'
    assert isinstance(obj.layer2.parent, Layer1)
    assert obj is obj.layer2.parent


def test_parent_reference_field_in_list():
    class Leaf:
        name = String()
        parent = ParentReference()

    class Root:
        leafs = List(Leaf)

    schema = load_schema(Root)
    root = schema.read_dict({'leafs': [{'name': 'a'}, {'name': 'b'}]})
    assert isinstance(root, Root)
    assert len(root.leafs) == 2
    assert isinstance(root.leafs[0].parent, Root)


def test_union_field():
    class Class1:
        name = String()

    class Class2:
        number = Integer()

    class Root:
        item = Union(Class1, Class2)

    schema = load_schema(Root)
    root = schema.read_dict({'item': {'type': 'Class1', 'name': 'test'}})
    assert isinstance(root.item, Class1)
    assert root.item.name == 'test'


def test_nested_field_default():
    class Leaf:
        name = String()

        @classmethod
        def get_default(cls):
            instance = cls()
            instance.name = 'default'
            return instance

    class Root:
        leaf = Nested(Leaf, default=Leaf.get_default())

    schema = load_schema(Root)
    root = schema.read_dict({})
    assert isinstance(root.leaf, Leaf)
    assert root.leaf.name == 'default'


def test_nested_field_collect_unknown():
    class Leaf:
        name = String()

    class Root:
        leaf = Nested(Leaf, collect_unknown='extra')

    schema = load_schema(Root)
    root = schema.read_dict({
        'leaf': {
            'name': 'test',
            'color': 'green',
            'thickness': 'very'
        }
    })
    assert isinstance(root.leaf, Leaf)
    assert isinstance(root.leaf.extra, dict)
    assert root.leaf.extra == {'color': 'green', 'thickness': 'very'}
