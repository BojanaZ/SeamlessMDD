from metamodel.typed_mixin import TypedMixin
from metamodel.field import Field
from pyecore.ecore import *


class TypedField(Field, TypedMixin, metaclass=MetaEClass):
    def __init__(self, _id=-1, name="", type_="", deleted=False, label=None, model=None, container=None):
        super().__init__(_id, name, deleted, label, model, container)
        if type_ == "":
            self._type = "string"
        else:
            self._type = type_

        self.attributes_for_dict.extend(['_type'])

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    def convert_to_tree_view_dict(self):
        parent_dict = super().convert_to_tree_view_dict()
        parent_dict['field_type'] = self.type
        return parent_dict

    def update(self, **kwargs):
        super().update(**kwargs)

        if "field-type" in kwargs:
            self._type = kwargs["field-type"]

