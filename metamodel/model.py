from utilities.exceptions import ElementNotFoundError
from utilities.utilities import iterable, get_class_from_parent_module

from metamodel.project import Project

import json
from json import JSONEncoder

from pyecore.ecore import *
from metamodel.element import Element
from metamodel.named_element import NamedElement


class Model(EObject, metaclass=MetaEClass):
    _version = EAttribute(eType=EInt)
    _root = EReference(name='_root', eType=Element, containment=False)
    _elements = EReference(name='_elements', eType=NamedElement, ordered=True, unique=True, changeable=True,
                           containment=True, upper=-1)

    def __init__(self, root_element=None, version=None, **kwargs):
        if kwargs:
            raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__(**kwargs)

        #if version is not None:
        self._version = version
        if root_element is not None:
            self._root = root_element

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, root):
        self._root = root
        if root not in self._elements:
            self._elements.append(root)

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = EOrderedSet()
        for _id, element in elements.items():
            self._elements.append(element)

    def add_element(self, element):
        if element in self:
            self._elements.append(element)
            element.model = self

    def find_element_by_index(self, element_id):
        for index in range(len(self._elements)):
            if self._elements[index].id == element_id:
                return index
        return -1

    def get_element(self, element_id):
        index = self.find_element_by_index(element_id)
        if index != -1:
            return self._elements[index]
        else:
            raise ElementNotFoundError("Element with id " + str(element_id) + " is not part of the current model.")

    def remove_element(self, element):
        if element.container:
            element.container.elements.remove(element)
        self._elements.remove(element)

    def __contains__(self, item):
        return self.find_element_by_index(item.id) != -1

    def __getitem__(self, item):
        return self.get_element(item)

    def __setitem__(self, key, value):
        index = self.find_element_by_index(key)
        self._elements[index] = value

    def __iter__(self):
        for element in self._elements:
            yield element

            if iterable(element):
                for subelement in iter(element):
                 yield subelement

    def to_json(self):
        return json.dumps(self, cls=ModelJSONEncoder, default=lambda o:o.to_dict(), indent=4)

    @classmethod
    def from_json(cls, data):

        if type(data) == str:
            data = json.loads(data)

        root_element = data["_root_element"]
        root_class = root_element["class"]
        class_type = get_class_from_parent_module(root_class, "metamodel")
        root_element_object = class_type.from_json(root_element)

        new_object = cls()
        new_object._root_element = root_element_object
        new_object.version = data['_version']

        elements = {
            root_element_object.id: root_element_object
        }

        for subelement in root_element_object.get_all_subelements():
            elements[subelement.id] = subelement

        new_object.elements = elements

        for element in elements.values():
            element.model = new_object

        return new_object

    def deepcopy(self):
        json = self.to_json()
        return Model.from_json(json)

    def to_dict(self):
        return ModelJSONEncoder().default(self)

    def get_first_level_dict(self):
        return {key: value for (key, value) in self.__dict__.items()}

    def __hash__(self):
        return id(self)

    def __eq__(self, other):

        if type(self) != type(other):
            return False

        if self._root_element is not None and other.root is not None:
            if self._root_element.id != other.root.id:
                return False
        else:
            if self._root_element != other.root:
                return False

        if len(self._elements) != len(other.elements):
            return False

        for element in self._elements:
            if element.id not in other.elements:
                return False

            other_element = other.elements.find_element(element.id)
            if element != other_element:
                return False

        return True

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "Model[{} {}]".format(self._version, self._root_element)

    def convert_to_tree_view_dict(self):
        model_dict = {"text": "Model",
                      "id": -1,
                      "type": self.__class__.__name__,
                      "state": {"opened": True},
                      "version": self._version,
                      "children": [child_element.convert_to_tree_view_dict() for child_element
                                   in self._elements
                                   if isinstance(child_element, Project)]}
        return model_dict


class ModelJSONEncoder(JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Model):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if key not in ['_elements', '_root_element']}
            elements = {}

            for element in object_.elements:
                elements[element.id] = element.to_dict()

            object_dict['_elements'] = elements
            object_dict['_root_element'] = object_.root.to_dict()
            object_dict["class"] = type(object_).__name__
            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)



