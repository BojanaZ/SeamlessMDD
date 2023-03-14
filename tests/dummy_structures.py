from metamodel.model import Model
from metamodel.project import Project
from metamodel.document import Document
from metamodel.field import Field

from transformation.conflict_resolution.question_registry import QuestionRegistry
from transformation.conflict_resolution.answer import Answer
from transformation.conflict_resolution.question import Question


def dummy_data():

    model = Model()

    project = Project(1, "MyProject", False, None, model)

    model.root = project

    document1 = Document(11, "Document1", False, None, model)
    document2 = Document(12, "Document2", False, None, model)
    project.add(document1)
    project.add(document2)

    field1 = Field(89, "Fifi1", False, None, model)
    field2 = Field(90, "Fifi2", False, None, model)
    field3 = Field(91, "Fifi3", False, None, model)
    field4 = Field(92, "Fifi4", False, None, model)
    field5 = Field(93, "Fifi5", False, None, model)

    document1.add(field1)
    document1.add(field2)
    document1.add(field3)
    document2.add(field4)
    document2.add(field5)

    return model


def question_registry():
    question_registry = QuestionRegistry()
    q1 = Question("Test question 1", "What?")
    a11 = Answer("Answer 11")
    a12 = Answer("Answer 12")
    a13 = Answer("Answer 13")
    q1.answers = [a11, a12, a13]
    question_registry.register_question(q1)
    q1.chosen_answer_id = a13.id

    q2 = Question("Test question 2", "Why?")
    a21 = Answer("Answer 21")
    a22 = Answer("Answer 22")
    q2.answers = [a21, a22]
    question_registry.register_question(q2)
    q2.chosen_answer_id = a22.id

    return question_registry
