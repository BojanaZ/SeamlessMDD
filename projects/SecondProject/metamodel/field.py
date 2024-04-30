from .named_element import NamedElement
from pyecore.ecore import MetaEClass


class Field(NamedElement, metaclass=MetaEClass):

    def __init__(self, _id=-1, name="", deleted=False, label=None, model=None, container=None,  **kwargs):
        if kwargs:
            raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__(_id, name, deleted, label, model, container)

