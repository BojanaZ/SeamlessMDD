from Element import Element

class NamedElement(Element):

    def __init__(self, id, name, label = None):
        super().__init__(id)
        self._name = name
        self._label = label

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        self._label = label


if __name__ == '__main__':
    ne = NamedElement(4, "Bla", "efg")
    print(ne.id)
    print(ne.name)

