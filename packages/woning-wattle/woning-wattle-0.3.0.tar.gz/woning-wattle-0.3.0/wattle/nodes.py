import types
from textwrap import indent

from wattle.exceptions import MissingFieldError, InvalidValueError


class NotSet(object):
    pass


class NoValue(object):
    pass


def patch_str_method(obj_type, fields):
    is_base_type = obj_type in (int, float, str, bool, dict, list, tuple, None)
    is_composite = isinstance(obj_type, (list, tuple))
    if is_base_type or is_composite:
        return

    def __str__(self):
        obj_name = self.__class__.__name__
        field_strs = []
        for field in fields:
            field_val = getattr(self, field)
            field_strs.append(indent('{}: {}'.format(field, field_val), '  '))
        return "{}\n{}".format(obj_name, '\n'.join(field_strs))

    def __repr__(self):
        return str(self)

    obj_type.__str__ = __str__
    obj_type.__repr__ = __repr__


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
            data = self.get_default()
        patch_str_method(self.get_type(), [f[0] for f in self.get_fields()])
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
