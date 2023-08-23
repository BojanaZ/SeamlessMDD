from metamodel.container import Container


class Project(Container):

    def __init__(self, _id=-1, name="", deleted=False, label=None, model=None):
        super().__init__(_id, name, deleted, label, model)


