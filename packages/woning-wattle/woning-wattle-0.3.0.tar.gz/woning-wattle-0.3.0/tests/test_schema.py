import pytest

from wattle import Value, load_schema, String, Float, Boolean, Integer
from wattle.exceptions import MissingFieldError


def test_schema_required():
    class Schema:
        myval = Value(int)

    schema = load_schema(Schema)
    obj = schema.read_dict({'myval': 3})
    assert isinstance(obj, Schema)
    assert obj.myval == 3

    with pytest.raises(MissingFieldError):
        _ = schema.read_dict({})


def test_schema_default_value():
    class Schema:
        myval = Value(int, default=3)

    schema = load_schema(Schema)
    obj = schema.read_dict({'myval': 5})
    assert obj.myval == 5

    obj = schema.read_dict({})
    assert obj.myval == 3


def test_proper_value_is_received_in_load_from_data():
    class MyValue(Value):
        def __init__(self):
            super(MyValue, self).__init__(str, default='a')

        def load_from_data(self, data):
            assert isinstance(data, str)
            assert data in ('test', 'a')
            return data

    class Schema:
        myval = MyValue()

    schema = load_schema(Schema)
    obj = schema.read_dict({'myval': 'test'})
    assert obj.myval == 'test'
    obj = schema.read_dict({})
    assert obj.myval == 'a'
