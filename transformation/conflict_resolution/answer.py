import json
import os
from utilities.utilities import get_project_root


class Answer(object):

    def __init__(self, text, executable_set=None):
        self._id = None
        self._text = text
        self._executable_set = executable_set

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_):
        self._id = id_

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @property
    def executable_set(self):
        return self._executable_set

    @executable_set.setter
    def executable_set(self, executable_set):
        self._executable_set = executable_set

    def to_json(self):
        return json.dumps(self, cls=AnswerJSONEncoder)

    @classmethod
    def from_json(cls, data):

        if type(data) == str:
            data = json.loads(data)

        new_object = cls(data["_text"])
        new_object._id = int(data["_id"])

        return new_object

    def to_dict(self):
        return AnswerJSONEncoder().default(self)

    def __eq__(self, other):
        if self._id != other.id:
            return False

        if self._text != other.text:
            return False

        if len(self._executable_set) != len(other.executable_set):
            return False

        for executable in self._executable_set:
            for other_executable in other.executable_set:
                if executable == other_executable:
                    break
            else:
                return False
        return True

    def __ne__(self, other):
        return not self == other


class AnswerJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Answer):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if
                           key not in ['_tasks']}

            if object_.tasks is not None:
                object_dict["_tasks"] = object_.tasks.id
            else:
                object_dict["_tasks"] = None

            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
