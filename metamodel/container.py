from metamodel.named_element import NamedElement
from utilities.utilities import get_class_from_parent_module
import json
from json import JSONEncoder


class Container(NamedElement):

    def __init__(self, _id, name, deleted=False, label=None, model=None):
        super().__init__(_id, name, deleted, label, model)
        self._elements = {}

    @property
    def elements(self):
        return self._elements

    @elements.setter
    def elements(self, elements):
        self._elements = {}
        for _id, element in elements.items():
            self._elements[_id] = element

    def get_element(self, id_):
        return self._elements[id_]

    def add(self, element):
        if element.id not in self._elements:
            self._elements[element.id] = element

        element.container = self

        if self._model and element.id not in self.model:
            self.model[id] = element

    def __iter__(self):
        for element in self._elements:
            yield element

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
        for element in self._elements.values():
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

        for element_id, element in self._elements.items():
            if element_id not in other.elements:
                return False

            other_element = other.elements[element_id]
            if element != other_element:
                return False

        return True

    def __ne__(self, other):
        return not self == other

    def to_dict(self):
        return ContainerJSONEncoder().default(self)


class ContainerJSONEncoder(JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Container):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if key not in ['_model', '_elements',
                                                                                                  '_container']}
            elements = {key: value.to_dict() for (key, value) in object_.elements.items()}

            object_dict['_elements'] = elements
            object_dict["class"] = type(object_).__name__
            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
