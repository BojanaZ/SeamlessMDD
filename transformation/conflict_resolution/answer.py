import json
import os
from utilities.utilities import get_project_root


class Answer(object):

    def __init__(self, text, task=None):
        self._id = None
        self._text = text
        self._task = task

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
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

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

        if self._task != other.task:
            return False

        return True

    def __ne__(self, other):
        return not self == other


class AnswerJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Answer):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if
                           key not in ['_task']}

            if object_.task is not None:
                object_dict["_task"] = object_.task.id
            else:
                object_dict["_task"] = None

            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
