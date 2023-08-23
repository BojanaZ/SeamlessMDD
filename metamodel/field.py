from metamodel.named_element import NamedElement


class Field(NamedElement):

    def __init__(self, _id=-1, name="", deleted=False, label=None, model=None):
        super().__init__(_id, name, deleted, label, model)

