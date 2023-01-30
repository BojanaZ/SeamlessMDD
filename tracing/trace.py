import json


class Trace(object):

    def __init__(self, old_path=None, new_path=None, id_=-1):
        self._id = id_
        self._old_path = old_path
        self._new_path = new_path

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_):
        self._id = id_

    @property
    def old_path(self):
        return self._old_path

    @old_path.setter
    def old_path(self, path):
        self._old_path = path

    @property
    def new_path(self):
        return self._new_path

    @new_path.setter
    def new_path(self, path):
        self._new_path = path

    def to_json(self):
        return json.dumps(self, cls=TraceJSONEncoder)

    @classmethod
    def from_json(cls, data):
        new_object = cls(old_path=data["_old_path"], new_path=data["_new_path"], id_=data["_id"])
        return new_object


class TraceJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Trace):
            object_dict = {key: value for (key, value) in object_.__dict__.items()}
            return object_dict
        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
