from exceptions import ElementNotFoundError
from metamodel.named_element import NamedElement
from utilities.utilities import get_class_from_parent_module
import json
from json import JSONEncoder

from pyecore.ecore import MetaEClass, EReference, EOrderedSet, EMetaclass


class Container(NamedElement, metaclass=MetaEClass):

    _elements = EReference('_elements', NamedElement, ordered=True, unique=True, containment=True, changeable=True,
                           upper=-1)

    def __init__(self, _id=-1, name="", deleted=False, label=None, model=None, container=None, **kwargs):
        super().__init__(_id, name, deleted, label, model, container)

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = EOrderedSet()
        for _id, element in elements.items():
            self._elements.append(element)

    def get_element(self, id_):
        return self._elements[id_]

    def add(self, element):
        if element not in self:
            self._elements.append(element)

        element.parent_container = self
        element.model = self.model

    def __contains__(self, element):
        return self.find_element_by_index(element.id) != -1

    def __iter__(self):
        for element in self._elements:
            yield element

    def find_element_by_index(self, element_id):
        for index in range(len(self._elements)):
            if self._elements[index].id == element_id:
                return index
        return -1

    def get(self, element_id):
        index = self.find_element_by_index(element_id)
        if index != -1:
            return self._elements[index]
        else:
            raise ElementNotFoundError("Element with id " + str(element_id) + " is not part of the current model.")

    def to_json(self):
        return json.dumps(self, cls=ContainerJSONEncoder)

    @classmethod
    def from_json(cls, data: dict):

        elements = {}
        for key, value in data["_elements"].items():
            c = value["class"]
            class_type = get_class_from_parent_module(c, "metamodel")
            elements[int(key)] = class_type.from_json(value)

        new_object = cls(_id=data["_id"], name=data["_name"], deleted=data["_deleted"], label=data["_label"])
        new_object.elements = elements

        for element in elements.values():
            element.container = new_object

        return new_object

    def get_all_subelements(self):
        element_list = []
        for element in self._elements:
            element_list.append(element)
            if isinstance(element, Container):
                element_list.extend(element.get_all_subelements())

        return element_list

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if not super(Container, self).__eq__(other):
            return False

        if len(self._elements) != len(other.elements):
            return False

        for element in self._elements:
            if element.id not in other.elements:
                return False

            other_element = other.elements.get(element.id)
            if element != other_element:
                return False

        return True

    def __ne__(self, other):
        return not self == other
    
    def to_dict(self):
        return ContainerJSONEncoder().default(self)

    def convert_to_tree_view_dict(self):
        parent_dict = super().convert_to_tree_view_dict()
        parent_dict["children"] = [child_dict.convert_to_tree_view_dict() for child_dict in self._elements]
        return parent_dict


class ContainerJSONEncoder(JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Container):

            object_dict = {}
            for attr in object_.attributes_for_dict:
                object_dict[attr] = getattr(object_, attr)

            elements = {element.id: element.to_dict() for element in object_.elements}

            object_dict['_elements'] = elements
            object_dict["class"] = type(object_).__name__
            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
