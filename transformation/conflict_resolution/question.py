import json
from transformation.conflict_resolution.answer import Answer


class Question(object):

    def __init__(self, title, text):
        self._id = None
        self._title = title
        self._text = text
        self._answers = []
        self._chosen_answer_id = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id_):
        self._id = id_

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @property
    def answers(self):
        return self._answers

    @answers.setter
    def answers(self, answers_):
        self._answers = answers_

    @property
    def chosen_answer_id(self):
        return self._chosen_answer_id

    @chosen_answer_id.setter
    def chosen_answer_id(self, chosen_answer_id):
        self._chosen_answer_id = chosen_answer_id

    def to_json(self):
        return json.dumps(self, cls=QuestionJSONEncoder)

    @classmethod
    def from_json(cls, data):

        if type(data) == str:
            data = json.loads(data)

        new_object = cls(data["_title"], data["_text"])
        new_object._id = int(data["_id"])
        new_object._answers = [Answer.from_json(answer) for answer in data["_answers"]]
        new_object._chosen_answer_id = int(data["_chosen_answer_id"])
        return new_object

    def to_dict(self):
        return QuestionJSONEncoder().default(self)

    def __eq__(self, other):
        if self._id != other.id:
            return False

        if self._text != other.text:
            return False

        if self._title != other.title:
            return False

        if self._chosen_answer_id != other.chosen_answer_id:
            return False

        if len(self._answers) != len(other.answers):
            return False

        for answer in self.answers:
            found = False
            for other_answer in other.answers:
                if answer.id == other_answer.id:
                    found = True
                    if answer != other_answer:
                        return False

            if not found:
                return False

        return True

    def __ne__(self, other):
        return not self == other


class QuestionJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, Question):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if key not in ["_answers"]}
            object_dict["_answers"] = [value.to_dict() for value in object_.answers]
            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
