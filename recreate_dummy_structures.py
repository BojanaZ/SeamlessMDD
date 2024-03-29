import inspect
from functools import partial
import pyecore.ecore as Ecore
from pyecore.ecore import *

from element_generator_table import ElementGeneratorTable
from metamodel.model import Model
from metamodel.project import Project
from metamodel.document import Document
from metamodel.typed_field import TypedField
from metamodel.field import Field
from metamodel.named_element import NamedElement
from metamodel.element import Element
from metamodel.container import Container
from transformation.data_manipulation import DataManipulation
from transformation.generator_handler import GeneratorHandler
from transformation.conflict_resolution.question_registry import QuestionRegistry
from transformation.conflict_resolution.question import Question
from transformation.conflict_resolution.answer import Answer
from tracing.tracer import Tracer
from transformation.generators.jinja_generators.documents_output_generator import DocumentsOutputGenerator
from os.path import join
from utilities.utilities import get_project_root, get_generators
from tests.dummy_structures import dummy_data
from projects.project_loader import WorkspaceProject

name = 'document'
nsURI = 'http://www.example.org/document'
nsPrefix = 'document'

eClass = EPackage(name=name, nsURI=nsURI, nsPrefix=nsPrefix)

eClassifiers = {}
getEClassifier = partial(Ecore.getEClassifier, searchspace=eClassifiers)


def make():
    additional_changes()

    eClass.eClassifiers.extend([Model.eClass,
                                Element.eClass,
                                NamedElement.eClass,
                                Container.eClass,
                                Project.eClass,
                                Document.eClass,
                                Field.eClass,
                                TypedField.eClass])

    return eClass


# Mora naknadno
# Oficijalno objašnjenje, dato u inline komentaru u jednom od primera:
# As the relation is reflexive, it must be set AFTER the metaclass creation
def additional_changes():
    Element.eClass.eStructuralFeatures.append(EReference(name='_model', eType=Model, containment=False))
    Element._model = EReference(name='_model', eType=Model, containment=False)
    Element.eClass.eStructuralFeatures.append(EReference(name='_parent_container',
                                                         eType=Container,
                                                         eOpposite=Container._elements, containment=False))
    Element._parent_container = EReference(name='_parent_container',
                                                eType=Container,
                                                eOpposite=Container._elements, containment=False)


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

    path = join(get_project_root(), "storage", "table.dill")
    #with open(path, "wb") as file:
        #dill.dump(table, file)

    path = join(get_project_root(), "storage", "table.json")
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


def recreate_super_simple_dummy_data_manipulation(metamodel, project_path, write_to_file=False):
    project = Project(1, "MyProject", False, "MyProject")

    model = Model(root_element=project)

    project.model = model

    document1 = Document(11, "Document1", False, "Document1", model, project)

    field1 = TypedField(_id=111, name="Field1", type_="string", deleted=False, label="Field1", model=model,
                        container=document1)
    #field2 = TypedField(112, "Field2", "string", False, None, model, container=document1)

    document1.add(field1)
    #document1.add(field2)

    project.add(document1)

    # for element in model:
    #     element.model = model

    #model.root = project
    # document2 = Document(12, "Document2", False, None, model)
    # field3 = TypedField(113, "Field3", "string", False, None, model)
    # document2.add(field3)
    # project.add(document2)

    data_manipulation = DataManipulation(project_path)
    data_manipulation.update_model(model)

    new_model = Model()
    project = Project(1, "MyProject", False, "MyProject", new_model)
    new_model.root = project
    document1 = Document(11, "Document1", False, "Document1", new_model, project)
    project.add(document1)
    field1 = TypedField(111, "Field1", "string", False, "Field1", new_model, document1)
    field2 = TypedField(112, "Field2", "boolean", False, "Field2", new_model, document1)
    document1.add(field1)
    document1.add(field2)

    #document2 = Document(12, "Document2", False, None, new_model)
    #project.add(document2)
    #field3 = TypedField(113, "Field3", "string", False, None, new_model)
    #document2.add(field3)

    for element in new_model:
        element.model = new_model

    data_manipulation.update_model(new_model)
    data_manipulation.metamodel = metamodel
    tracer = Tracer(project_path)

    if write_to_file:
        #data_manipulation.save_to_json()
        data_manipulation.save_to_xmi()

    return data_manipulation, tracer


def recreate_dummy_diff_generator_handler(project, data_manipulation=None, tracer_=None, write_to_file=False):
    if project is None:
        project_path = get_project_root()
    else:
        project_path = project.path

    if data_manipulation is None:
        data_manipulation = DataManipulation(project_path).load_from_json()

    elements = data_manipulation.get_latest_model().elements
    handler_ = GeneratorHandler(project)

    generator_classes = get_generators(project_path, project.name)

    for generator_class in generator_classes.values():
        generator = generator_class()
        if tracer_:
            generator.tracer = tracer_
        generator.initialize()
        handler_.register(generator)

        for element in elements:
            handler_.element_generator_table.load_pair(element.id, generator.id,
                                                       {"value": True, "last_generated_version": 0})
    handler_.question_registry = QuestionRegistry()
    if write_to_file:
        handler_.save_to_json()
        tracer_.save_to_json()

    return handler_


def recreate_question_registry(file_path, write_to_file=False):

    question_registry = QuestionRegistry(file_path)
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


def main(project_path, project_name):
    metamodel = make()
    ws_project = WorkspaceProject(project_path=project_path, project_name=project_name)
    dm, tracer = recreate_super_simple_dummy_data_manipulation(metamodel, ws_project.path, True)
    handler = recreate_dummy_diff_generator_handler(ws_project, dm, tracer, True)
    question_registry = recreate_question_registry(project_path, True)


if __name__ == "__main__":
    project_path = "/Users/bojana/Documents/Private/Fakultet/doktorske/DMS-rad/SeamlessMDD/projects/FirstProject"
    main(project_path, "FirstProject")
