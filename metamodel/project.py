from metamodel.container import Container
from pyecore.ecore import MetaEClass


class Project(Container, metaclass=MetaEClass):

    def __init__(self, _id=-1, name="", deleted=False, label=None, model=None, container=None):
        super().__init__(_id, name, deleted, label, model, container)


