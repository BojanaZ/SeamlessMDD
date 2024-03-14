import json
from json import JSONEncoder
from pyecore.ecore import *


class Element(EObject, metaclass=MetaEClass):

    _id = EAttribute(eType=EInt, derived=False, changeable=True)
    _deleted = EAttribute(eType=EBoolean, derived=False, changeable=True)

    def __init__(self, _id=-1, deleted=False, model=None, container=None, **kwargs):

        if kwargs:
            raise AttributeError('unexpected arguments: {}'.format(kwargs))

        super().__init__()

        self._id = _id
        self.parent_container = container
        self._model = model

        self._deleted = deleted

        self.attributes_for_dict = ['_deleted', '_id']

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_):
        self._id = id_

    @property
    def parent_container(self):
        return self._parent_container

    @parent_container.setter
    def parent_container(self, container):
        self._parent_container = container

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

    @property
    def deleted(self):
        return self._deleted

    @deleted.setter
    def deleted(self, deleted=True):
        self._deleted = deleted

    def to_json(self):
        return json.dumps(self, cls=ElementJSONEncoder)

    @classmethod
    def from_json(cls, data: dict):
        new_object = cls(_id=data["_id"], name=data["_name"], deleted=data["_deleted"])
        return new_object

    def __hash__(self):
        return id(self)

    def __eq__(self, other):

        if type(self) != type(other):
            return False

        if self._id != other.id:
            return False

        if self._deleted != other.deleted:
            return False

        if self._parent_container is not None and other.parent_container is not None:
            if self._parent_container.id != other.parent_container.id:
                return False
        else:
            if self._parent_container != other.parent_container:
                return False

        return True

    def __ne__(self, other):
        return not self == other

    def to_dict(self):
        return ElementJSONEncoder().default(self)

    def get_first_level_dict(self):
        return {key: value for (key, value) in self.__dict__.items()}

    def convert_to_tree_view_dict(self):
        return {"id": self._id, "state": {"opened": True}, "type": self.__class__.__name__}

    def update(self, **kwargs):
        raise NotImplemented()


class ElementJSONEncoder(JSONEncoder):
    def default(self, object_):

        if isinstance(object_, Element):

            object_dict = {}
            for attr in object_.attributes_for_dict:
                object_dict[attr] = getattr(object_, attr)

            object_dict["class"] = type(object_).__name__
            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)


