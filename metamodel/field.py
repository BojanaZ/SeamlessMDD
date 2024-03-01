from metamodel.named_model_element import NamedModelElement
from pyecore.ecore import MetaEClass


class Field(NamedModelElement, metaclass=MetaEClass):

    def __init__(self, _id=-1, name="", deleted=False, label=None, model=None, **kwargs):
        if kwargs:
            raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__(_id, name, deleted, label, model)

