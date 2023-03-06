import json
import os
from utilities.utilities import get_project_root
from transformation.conflict_resolution.question import Question


class QuestionRegistry(object):

    def __init__(self):
        self._questions = {}

    @staticmethod
    def new_question_id_generator():
        id_ = 0
        while True:
            yield id_
            id_ += 1

    def generate_new_question_id(self):
        id_generator = self.new_question_id_generator()
        while True:
            id_ = next(id_generator)
            if id_ not in self._questions:
                return id_

    def register_question(self, question):
        question_id = self.generate_new_question_id()
        self._questions[question_id] = question
        question.id = question_id
        for answer in question.answers:
            answer.id = self.generate_new_answer_id()

    @staticmethod
    def new_answer_id_generator():
        id_ = 0
        while True:
            yield id_
            id_ += 1

    def generate_new_answer_id(self):
        id_generator = self.new_answer_id_generator()
        while True:
            id_ = next(id_generator)
            if self.check_if_answer_id_is_available(id_):
                return id_

    def check_if_answer_id_is_available(self, id_):
        for question in self._questions.values():
            for answer in question.answers:
                if answer.id == id_:
                    return False
        return True

    @property
    def questions(self):
        return self._questions

    @questions.setter
    def questions(self, questions_):
        self._questions = questions_

    def to_json(self):
        return json.dumps(self, cls=QuestionRegistryJSONEncoder)

    @classmethod
    def from_json(cls, data):

        if type(data) == str:
            data = json.loads(data)

        new_object = cls()

        new_object._questions = {}
        for id_, question in data["_questions"].items():
            question = Question.from_json(question)
            if id_ is None:
                new_object.register_question(question)
            else:
                new_object._questions[int(id_)] = question
        return new_object

    def to_dict(self):
        return QuestionRegistryJSONEncoder().default(self)

    @staticmethod
    def load_from_json(path=None):
        if not path:
            path = os.path.join(get_project_root(), "files", "question_registry.json")

        try:
            with open(path, "r") as file:
                content = file.read()
                loaded_content = json.loads(content)
                return QuestionRegistry.from_json(loaded_content)
        except OSError:
            print("Unable to load question registry.")

    def save_to_json(self, path=None):
        if not path:
            path = os.path.join(get_project_root(), "files", "question_registry.json")

        try:
            with open(path, "w") as file:
                content = self.to_dict()
                json.dump(content, file, default=lambda o: o.to_dict(), indent=4)
        except OSError:
            print("Unable to load question registry.")

    def __eq__(self, other):
        if len(self._questions) != len(other.questions):
            return False

        for question_id, question in self._questions.items():
            if question_id not in other.questions:
                return False
            if other.questions[question_id] != self._questions[question_id]:
                return False

        return True

    def __ne__(self, other):
        return not self == other


class QuestionRegistryJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, QuestionRegistry):

            object_dict = {"_questions": {key: value.to_dict() for (key, value) in object_.questions.items()}}
            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)