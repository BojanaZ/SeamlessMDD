from metamodel.element_generator_table import ElementGeneratorTable
from metamodel.model import Model
from metamodel.project import Project
from metamodel.document import Document
from metamodel.typed_field import TypedField
from transformation.data_manipulation import DataManipulation
from transformation.generator_handler import GeneratorHandler
from transformation.generators.diff_generators.document_diff_generator import DocumentDiffGenerator
from transformation.conflict_resolution.question_registry import QuestionRegistry
from transformation.conflict_resolution.question import Question
from transformation.conflict_resolution.answer import Answer
from tracing.tracer import Tracer
from transformation.generators.jinja_generators.documents_output_generator import DocumentsOutputGenerator
from os.path import join
from utilities.utilities import get_project_root
from tests.dummy_structures import dummy_data


def dummy_table():
    data = dummy_data()
    generator = DocumentsOutputGenerator()
    generator.initialize()
    table = ElementGeneratorTable()
    elements = data.elements
    for element in elements.values():
        table.insert_pair(element, generator)
    return table


def recreate_dummy_table():
    #TABLE RECREATION FOR FILE
    table = dummy_table()

    path = join(get_project_root(), "files", "table.dill")
    #with open(path, "wb") as file:
        #dill.dump(table, file)

    path = join(get_project_root(), "files", "table.json")
    with open(path, "w") as file:
        file.write(table.to_json())


def recreate_dummy_generator_handler():
    #try:
        #data_manipulation = DataManipulation().load_from_dill()
    #except:
    data_manipulation = recreate_dummy_data_manipulation()

    handler = GeneratorHandler()
    generator = DocumentsOutputGenerator()
    generator.initialize()
    handler.register(generator)

    elements = data_manipulation.get_latest_model().elements
    for element_id, element in elements.items():
        handler.element_generator_table.insert_pair(element, generator)

    handler.save_to_json()
    handler.element_generator_table.save_to_json(handler.data_loading_path)


def recreate_dummy_data_manipulation():
    model = dummy_data()

    data_manipulation = DataManipulation()
    data_manipulation.update_model(model)

    data_manipulation.save_to_json()
    #data_manipulation.save_to_dill()

    return data_manipulation


def recreate_super_simple_dummy_data_manipulation(write_to_file=False):
    model = Model()

    project = Project(1, "MyProject", False, None, model)
    model.root = project
    document1 = Document(11, "Document1", False, None, model)
    #field1 = TypedField(111, "Fifi1", "string", False, None, model)
    #field2 = TypedField(112, "Fifi2", "string", False, None, model)
    #document1.add(field1)
    #document1.add(field2)
    project.add(document1)

    # document2 = Document(12, "Document2", False, None, model)
    # field3 = TypedField(113, "Fifi3", "string", False, None, model)
    # document2.add(field3)
    # project.add(document2)

    data_manipulation = DataManipulation()
    data_manipulation.update_model(model)

    new_model = Model()
    project = Project(1, "MyProject", False, None, new_model)
    new_model.root = project
    document1 = Document(11, "Document1", False, None, new_model)
    project.add(document1)
    field1 = TypedField(111, "Fifi1", "string", False, None, new_model)
    #field2 = TypedField(112, "Fifi2", "String", False, None, new_model)
    document1.add(field1)
    #document1.add(field2)

    #document2 = Document(12, "Document2", False, None, new_model)
    #project.add(document2)
    #field3 = TypedField(113, "Fifi3", "string", False, None, new_model)
    #document2.add(field3)

    data_manipulation.update_model(new_model)
    tracer = Tracer()

    if write_to_file:
        data_manipulation.save_to_json()

    return data_manipulation, tracer


def recreate_dummy_diff_generator_handler(data_manipulation=None, tracer_=None, write_to_file=False):
    if data_manipulation is None:
        data_manipulation = DataManipulation().load_from_json()

    handler_ = GeneratorHandler()
    generator = DocumentDiffGenerator()
    if tracer_:
        generator.tracer = tracer_
    generator.initialize()
    handler_.register(generator)

    elements = data_manipulation.get_latest_model().elements
    for element_id, element in elements.items():
        handler_.element_generator_table.load_pair(element_id, generator.id,
                                                   {"value": True, "last_generated_version": 0})
    if write_to_file:
        handler_.save_to_json()
        tracer_.save_to_json()

    return handler_


def recreate_question_registry(write_to_file=False):

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

    if write_to_file:
        question_registry.save_to_json()

    return question_registry


if __name__ == "__main__":
    dm, tracer = recreate_super_simple_dummy_data_manipulation(True)
    handler = recreate_dummy_diff_generator_handler(dm, tracer, True)
    question_registry = recreate_question_registry(True)
