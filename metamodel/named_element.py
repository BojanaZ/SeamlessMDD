from metamodel.element import Element
from view.tree_view_mixin import TreeViewMixin

from pyecore.ecore import MetaEClass, EAttribute, EString


class NamedElement(Element, TreeViewMixin, metaclass=MetaEClass):

    _name = EAttribute(eType=EString, derived=False, changeable=True)
    _label = EAttribute(eType=EString, derived=False, changeable=True)

    def __init__(self, _id=-1, name="", deleted=False, label=None, model=None, **kwargs):
        if kwargs:
            raise AttributeError('unexpected arguments: {}'.format(kwargs))

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

    def convert_to_tree_view_dict(self):
        parent_dict = super().convert_to_tree_view_dict()
        text = self._label
        if self._label is None or self._label == "":
            text = self._name
        parent_dict["text"] = text
        parent_dict["name"] = self._name
        parent_dict["label"] = self._label
        return parent_dict

    def update(self, **kwargs):
        if "name" in kwargs:
            self._name = kwargs["name"]

        if "label" in kwargs:
            self._label = kwargs["label"]
