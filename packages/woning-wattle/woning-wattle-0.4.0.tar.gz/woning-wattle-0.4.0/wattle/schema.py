import yaml

from wattle.nodes import Nested, ParentReference, List


class Schema(object):
    def __init__(self, root_obj):
        self.root_obj = Nested(root_obj)

    def read_dict(self, d):
        obj = self.root_obj.load(d)
        self.create_parent_references(obj, self.root_obj, parent=None)
        return obj

    def read(self, input_file):
        with open(input_file, 'r') as f:
            content = yaml.load(f)
        return self.read_dict(content)

    read_yml = read

    def create_parent_references(self, obj, obj_type, parent=None):
        for field_name, field_type in obj_type.get_fields():
            if isinstance(field_type, ParentReference):
                # we must attach the parent reference to the current object
                setattr(obj, field_name, parent)
            elif isinstance(field_type, List):
                # it's a list of elements so we create parent references
                # for all the items in the list. Their parent will be the
                # node that contains the list.
                for item in getattr(obj, field_name):
                    self.create_parent_references(
                        item,
                        field_type.type,
                        parent=obj)
            elif isinstance(obj_type, Nested):
                # we go recursively to the nested object's fields and
                # build the parent references for their fields.
                self.create_parent_references(
                    getattr(obj, field_name),
                    field_type,
                    parent=obj
                )
