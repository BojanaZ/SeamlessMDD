from metamodel.typed_mixin import TypedMixin
from metamodel.field import Field


class TypedField(Field, TypedMixin):
    def __init__(self, _id, name, type_="", deleted=False, label=None, model=None):
        super().__init__(_id, name, deleted, label, model)
        if type_ == "":
            self.type = "string"
        else:
            self.type = type_
