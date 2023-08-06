import pytest

from wattle import String, load_schema, Nested
from wattle.exceptions import MissingFieldError


def test_missing_value_hierarchy():
    class Schema:
        field = String()

    schema = load_schema(Schema)
    with pytest.raises(MissingFieldError) as e:
        _ = schema.read_dict({})
    assert 'field' in str(e)

    class Layer3:
        value = String()

    class Layer2:
        layer_3 = Nested(Layer3)

    class Layer1:
        layer_2 = Nested(Layer2)

    schema = load_schema(Layer1)
    with pytest.raises(MissingFieldError) as e:
        _ = schema.read_dict({'layer_2': {'layer_3': {}}})

    assert 'layer_2.layer_3.value' in str(e)
