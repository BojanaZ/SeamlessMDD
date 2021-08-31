from metamodel.Container import Container

class Project(Container):

    def __init__(self, id):
        super().__init__(id)
        self._versions = []

    @property
    def versions(self):
        return self._versions

    @versions.setter
    def versions(self, versions):
        self._versions = versions

