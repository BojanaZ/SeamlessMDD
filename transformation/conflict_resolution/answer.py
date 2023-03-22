import json


class Answer(object):

    def __init__(self, text, assignment_set=None):
        self._id = None
        self._text = text
        self._assignment_set = assignment_set

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
    def assignment_set(self):
        return self._assignment_set

    @assignment_set.setter
    def assignment_set(self, assignment_set):
        self._assignment_set = assignment_set

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

    def is_the_same(self, other):
        if self._text != other.text:
            return False

        if len(self._assignment_set) != len(other.assignment_set):
            return False
        return True

    def __eq__(self, other):
        if self._id != other.id:
            return False

        if self._text != other.text:
            return False

        if len(self._assignment_set) != len(other.assignment_set):
            return False

        for assignment in self._assignment_set:
            for other_assignment in other.assignment_set:
                if assignment == other_assignment:
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
                           key not in ['_assignment_set']}

            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
