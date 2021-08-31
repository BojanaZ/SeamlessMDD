from metamodel.element import Element


class NamedElement(Element):

    def __init__(self, _id, name, deleted=False, label=None, model=None):
        super().__init__(_id, deleted, model)
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

    def __str__(self):
        return "%d %s" % (self._id, self._name)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if not super(NamedElement, self).__eq__(other):
            return False

        if self._name != other.name:
            return False

        if self._label != other.label:
            return False

        return True
