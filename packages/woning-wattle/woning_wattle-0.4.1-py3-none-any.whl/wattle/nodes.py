import types
from textwrap import indent

from wattle.exceptions import MissingFieldError, InvalidValueError


class NotSet(object):
    pass


class NoValue(object):
    pass


class Node(object):
    def __init__(self, type, *, default=NotSet):
        self.type = type
        self.default = default

    def get_fields(self):
        """List the fields defined on the wrapped type.

        Returns an empty list for wrapped builtins.
        """
        fields = []
        for attr_name in dir(self.get_type()):
            attr_val = getattr(self.get_type(), attr_name)
            if isinstance(attr_val, Node):
                fields.append((attr_name, attr_val))
        return fields

    def get_default(self):
        if callable(self.default):
            return self.default()
        else:
            return self.default

    def load(self, data):
        """Loads the object or value from data.

        This handles the value constraints and passes the actual loading to
        self.load_from_data
        """
        data_provided = data is not NoValue
        default_provided = self.default is not NotSet
        if not data_provided and not default_provided:
            raise MissingFieldError()
        if not data_provided and default_provided:
            return self.get_default()
        value = self.load_from_data(data)
        return value

    def get_type(self):
        return self.type

    def load_from_data(self, data):
        raise NotImplementedError()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<{} of type {}>".format(self.__class__.__name__,
                                        self.get_type())


class Value(Node):
    def load_from_data(self, data):
        try:
            return self.get_type()(data)
        except (ValueError, TypeError):
            raise InvalidValueError(
                'Unable to convert {} to {}'.format(
                    repr(data),
                    self.get_type().__class__.__name__))


class ParentReference(Node):
    """The resulted field will have a reference to the direct parent.

    In the case when the type that has a ParentReference field is within
    a List, the parent is considered to be the element which contains the list.
    """

    def __init__(self):
        super(ParentReference, self).__init__(None, default=None)

    def load_from_data(self, data):
        return data

    def __str__(self):
        return "<ParentReference>"


class Nested(Node):
    def __init__(self, type, *, default=NotSet, collect_unknown=False):
        """A node of the specified type.

        Arguments:
            type: The type of the child node
            default: a callable or a default value that will be used if the
                specified node does not appear in the input
            collect_unknown (False or str): If, specified, the unknown fields
                will be collected in a dict accessible through the
                attribute with the specified name
        """
        super(Nested, self).__init__(type, default=default)
        assert collect_unknown is False or isinstance(collect_unknown, str)
        self.collect_unknown = collect_unknown

    def load_from_data(self, data):
        instance = self.get_type()()
        for field_name, field_type in self.get_fields():
            data_obj = data.get(field_name, NoValue)
            try:
                loaded_value = field_type.load(data_obj)
            except MissingFieldError as e:
                e.add_layer(field_name)
                raise e
            setattr(instance, field_name, loaded_value)
        if self.collect_unknown:
            unknown = {}
            fields = [f[0] for f in self.get_fields()]
            for k, v in data.items():
                if k not in fields:
                    unknown[k] = v
            setattr(instance, self.collect_unknown, unknown)
        return instance


class Union(Nested):
    def __init__(self, *types, default=NotSet):
        super(Union, self).__init__(types, default=default)
        self.types = {t.__name__: t for t in types}

    def load_from_data(self, data):
        self.type = self.types[data.get('type')]
        return super(Union, self).load_from_data(data)


class List(Node):
    def __init__(self, type, *, default=NotSet):
        if not isinstance(type, Node):
            type = Nested(type)
        super(List, self).__init__(type, default=default)

    def load_from_data(self, data):
        instances = []
        for field_def in data:
            value = self.get_type().load(field_def)
            instances.append(value)
        return instances


class Choice(Node):
    def __init__(self, choices):
        self.choices = choices
        super(Choice, self).__init__(None, default=choices[0])

    def load_from_data(self, data):
        if data not in self.choices:
            raise InvalidValueError('Invalid value for {}'.format(self))
        return data


class BaseValue(Value):
    type = str

    def __init__(self, default=NotSet):
        super(BaseValue, self).__init__(self.get_type(), default=default)

    def __str__(self):
        return "<{}>".format(self.__class__.__name__)


class Integer(BaseValue):
    type = int


class Float(BaseValue):
    type = float


class String(BaseValue):
    pass


class Boolean(BaseValue):
    type = bool


class Dict(BaseValue):
    type = dict
