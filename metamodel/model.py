from utilities.exceptions import ElementNotFoundError
from utilities.utilities import iterable, get_class_from_parent_module

import json
from json import JSONEncoder


class Model(object):

    def __init__(self, root_element=None, version=None):
        self._version = version
        # access to model elements
        self._elements = {}
        self._root_element = root_element


    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def root(self):
        return self._root_element

    @root.setter
    def root(self, root):
        self._root_element = root
        if root.id not in self._elements:
            self._elements[root.id] = root

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = elements

    def add_element(self, element):
        self._elements[element.id] = element

    def get_element(self, element_id):
        try:
            return self._elements[element_id]
        except KeyError:
            raise ElementNotFoundError("Element with id " + str(id) + " is not part of the current model.")

    def check_element(self, element_id):
        return element_id in self._elements

    def remove_element(self, element):
        del self._elements[element.id]

    def __contains__(self, item):
        return self.check_element(item)

    def __getitem__(self, item):
        return self.get_element(item)

    def __setitem__(self, key, value):
        self._elements[key] = value

    def __iter__(self):
        for element in self._elements.values():
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

        for element_id, element in self._elements.items():
            if element_id not in other.elements:
                return False

            other_element = other.elements[element_id]
            if element != other_element:
                return False

        return True

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "Model[{} {}]".format(self._version, self._root_element)


class ModelJSONEncoder(JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Model):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if key not in ['_elements', '_root_element']}
            elements = {}

            for key, value in object_.elements.items():
                elements[key] = value.to_dict()

            object_dict['_elements'] = elements
            object_dict['_root_element'] = object_.root.to_dict()
            object_dict["class"] = type(object_).__name__
            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)



