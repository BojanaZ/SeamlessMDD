from transformation.tasks.diff_tasks.base_diff_task import BaseDiffTask
from transformation.assignment.assignment import Assignment
from transformation.assignment.assignment_set import AssignmentSet
from metamodel.document import Document
from metamodel.field import Field
from utilities.utilities import class_object_to_underscore_format
from jinja2 import Template
import os
from diff.operation_type import OperationType
from tracing.manual_tracing import IManualTracing
from transformation.conflict_resolution.question import Question
from transformation.conflict_resolution.answer import Answer
from messages.question_text import *
from messages.question_titles import *
from messages.answer_text import *
from utilities.exceptions import GenerationValidationException


class DiffDemoManualTracingTask(BaseDiffTask, IManualTracing):

    def __init__(self, generator, priority=2, template_name_=None):
        if template_name_ is not None and template_name_ != "":
            self._template_name = template_name_
        else:
            self._template_name = "first_template.tpl"

        self._additional_templates_path = "diff_demo_task/"
        self._additional_templates = {}
        self._template_folder_path = "../../generator_templates/"
        self.insert_additional_templates()

        super().__init__(priority=priority, template_name=template_name_, generator=generator)

    @property
    def template_name(self):
        return self._template_name

    def filtered_elements(self, model):
        """Return iterator over elements in model that are passed to the above template."""
        documents = (document for document in model.elements.values() if type(document) == Document)
        for document in documents:
            yield document

    def insert_additional_templates(self):
        self._additional_templates["field"] = "field_template.tpl"
        self._additional_templates["fields"] = "fields_template.tpl"
        self._additional_templates["document"] = "document_template.tpl"

    def should_generate(self, model, element):
        for filtered_element in self.filtered_elements(model):
            if element.id == filtered_element.id:
                return True

        return False

    def relative_path_for_element(self, diff):
        """Return relative file path receiving the generator output for given element."""
        try:
            document_name = diff.old_object_ref.name
        except:
            document_name = diff.new_object_ref.name
        return document_name + ".task1.html"

    def add(self, diff, filepath):

        if os.path.isfile(filepath):
            relative_path = os.path.join(self._additional_templates_path, self._additional_templates["document"])
        else:
            relative_path = self._template_name

        template_file = open(self._template_folder_path + relative_path)
        template = template_file.read()
        template_file.close()
        content = Template(template).render(element=diff.new_object_ref)
        parser = self._generator.get_parser(filepath)

        if os.path.isfile(filepath):
            tracer = self._generator.tracer
            for trace in tracer.get_traces(diff.new_object_ref.id, self._generator.id):
                parser.insert_element_by_path(trace.old_path, content)
        else:
            parser.parser.parseStr(content)

    def add_with_file(self, diff, filepath):
        template_file = open(self._template_folder_path + self._additional_templates["document"])
        template = template_file.read()
        template_file.close()
        content = Template(template).render(element=diff.new_object_ref)
        parser = self._generator.get_parser(filepath)
        parser.parser.parseStr(content)

    def remove(self, diff, filepath):
        id_ = diff.old_object_ref.id
        self._generator.get_parser(filepath).remove_element_by_id(id_)

    def change(self, diff, filepath):
        parser = self._generator.get_parser(filepath)
        tracer = self._generator.tracer

        if diff.operation_type in [OperationType.CHANGE]:
            old_element = diff.old_object_ref
            new_element = diff.new_object_ref
        else:
            old_element = diff.old_object_ref.elements[diff.key]
            new_element = diff.new_object_ref.elements[diff.key]

        for trace in tracer.get_traces(diff.key, self._generator.id):
            old_property_xpaths = self.get_property_traces(old_element)[diff.property_name]
            new_property_xpaths = self.get_property_traces(new_element)[diff.property_name]
            template_file = open(os.path.join("../templates/",
                                              self._template_name))
            template = template_file.read()
            template_file.close()

            content = Template(template).render(element=diff.new_object_ref)

            for old_property_xpath, new_property_xpath in zip(old_property_xpaths, new_property_xpaths):
                parser.update_element_by_path(old_property_xpath, new_property_xpath, content)

    def subelement_add(self, diff, filepath):
        parser = self._generator.get_parser(filepath)
        tracer = self._generator.tracer
        for trace in tracer.get_traces(diff.new_value.id, self._generator.id):
            template_file = open(os.path.join(self._template_folder_path,
                                              self._additional_templates_path,
                                              self._additional_templates["field"]))
            template = template_file.read()
            template_file.close()
            content = Template(template).render(element=diff.new_value)

            parser.insert_element_by_path(trace.old_path, content)

    def subelement_remove(self, diff, filepath):
        parser = self._generator.get_parser(filepath)
        parser.remove_element_by_id(diff.old_value.id)

    def subelement_change(self, diff, filepath):
        parser = self._generator.get_parser(filepath)
        parser.update_element_by_id(diff.key, diff.property_name, diff.new_value)

    def check_if_element_exists(self, id_, filepath):
        parser = self._generator.get_parser(filepath)
        return parser.check_if_element_exists(id_)

    def ignore(self, diff, filepath):
        pass

    def raise_issue(self, diff, filepath):
        raise GenerationValidationException("Resolve issue later")

    def recreate(self, diff, filepath):
        if diff.operation_type is OperationType.CHANGE:
            self.add(diff, filepath)
        elif diff.operation_type is OperationType.SUBELEMENT_CHANGE:
            self.subelement_add(diff, filepath)

    def recreate_parent(self, diff, filepath):
        if diff.operation_type is OperationType.SUBELEMENT_CHANGE:
            if not os.path.isfile(filepath):
                self.add(diff, filepath)
        elif diff.operation_type is OperationType.SUBELEMENT_ADD:
            self.subelement_add(diff, filepath)
        elif diff.operation_type is OperationType.SUBELEMENT_REMOVE:
            pass

    def compare_versions(self, diff, filepath):
        pass

    def generate_file(self, diff, filepath):
        """Actual file generation from model element."""

        self.insert_traces(diff)

        method = None
        questions = []

        if diff.operation_type == OperationType.ADD:
            method = self.add

        elif diff.operation_type == OperationType.REMOVE:
            exists, element = self.check_if_element_exists(diff.key, filepath)
            if exists:
                method = self.remove
            else:
                question = Question(DOES_NOT_EXIST_TITLE, DOES_NOT_EXIST_TEXT.format(str(diff.old_object_ref)))
                question.element_xpath = self.generator.get_parser(filepath).get_element_xpath(element)
                assignment_set_a1 = AssignmentSet(Assignment(self.ignore))
                assignment_set_a1.setup_context(diff=diff, filepath=filepath)
                a1 = Answer(IGNORE, assignment_set_a1)

                assignment_set_a2 = AssignmentSet(Assignment(self.raise_issue))
                assignment_set_a2.setup_context(diff=diff, filepath=filepath)
                a2 = Answer(RAISE_ISSUE, assignment_set_a2)
                question.answers = [a1, a2]
                questions.append(question)

        elif diff.operation_type in [OperationType.CHANGE, OperationType.SUBELEMENT_CHANGE]:
            exists, element = self.check_if_element_exists(diff.key, filepath)
            if exists:
                self.compare_versions(diff, filepath)
                method = self.change
            else:
                question = Question(DOES_NOT_EXIST_TITLE, DOES_NOT_EXIST_TEXT.format(str(diff.old_object_refl)))
                question.element_xpath = self.generator.get_parser(filepath).get_element_xpath(element)
                assignment_set_a1 = AssignmentSet(Assignment(self.ignore))
                assignment_set_a1.setup_context(diff=diff, filepath=filepath)
                a1 = Answer(IGNORE, assignment_set_a1)

                assignment_set_a2 = AssignmentSet(Assignment(self.recreate))
                assignment_set_a2.setup_context(diff=diff, filepath=filepath)
                a2 = Answer(RECREATE, assignment_set_a2)
                question.answers = [a1, a2]
                questions.append(question)

        elif diff.operation_type == OperationType.SUBELEMENT_ADD:
            parent_element = diff.old_object_ref
            exists, element = self.check_if_element_exists(parent_element.id, filepath)
            if not exists:
                question = Question(DOES_NOT_EXIST_TITLE, DOES_NOT_EXIST_TEXT.format(str(parent_element)))
                assignment_set_a1 = AssignmentSet(Assignment(self.ignore))
                assignment_set_a1.setup_context(diff=diff, filepath=filepath)
                a1 = Answer(IGNORE, assignment_set_a1)

                assignment_set_a2 = AssignmentSet(Assignment(self.recreate_parent), Assignment(self.subelement_add))
                assignment_set_a2.setup_context(diff=diff, filepath=filepath)
                a2 = Answer(RECREATE, assignment_set_a2)
                question.answers = [a1, a2]
                questions.append(question)

            new_element = diff.new_value
            exists, element = self.check_if_element_exists(new_element.id, filepath)
            if exists:
                question = Question(ALREADY_EXISTS_TITLE, ALREADY_EXISTS_TITLE.format(str(new_element)))
                question.element_xpath = self.generator.get_parser(filepath).get_element_xpath(element)
                assignment_set_a1 = AssignmentSet(Assignment(self.ignore))
                assignment_set_a1.setup_context(diff=diff, filepath=filepath)
                a1 = Answer(IGNORE, assignment_set_a1)

                assignment_set_a2 = AssignmentSet(Assignment(self.subelement_add))
                assignment_set_a2.setup_context(diff=diff, filepath=filepath)
                a2 = Answer(ADD, assignment_set_a2)
                question.answers = [a1, a2]
                questions.append(question)
            else:
                method = self.subelement_add

        elif diff.operation_type == OperationType.SUBELEMENT_REMOVE:
            parent_element = diff.old_object_ref
            exists, element = self.check_if_element_exists(parent_element.id, filepath)
            if not exists:
                question = Question(DOES_NOT_EXIST_TITLE, DOES_NOT_EXIST_TEXT.format(str(parent_element)))
                assignment_set_a1 = AssignmentSet(Assignment(self.ignore))
                assignment_set_a1.setup_context(diff=diff, filepath=filepath)
                a1 = Answer(IGNORE, [self.ignore])

                assignment_set_a2 = AssignmentSet(Assignment(self.recreate), Assignment(self.subelement_remove))
                assignment_set_a2.setup_context(diff=diff, filepath=filepath)
                a2 = Answer(RECREATE, assignment_set_a2)
                question.answers = [a1, a2]
                questions.append(question)
            else:
                method = self.subelement_remove

        elif diff.operation_type == OperationType.SUBELEMENT_CHANGE:
            parent_element = diff.old_object_ref
            exists, element = self.check_if_element_exists(parent_element.id, filepath)
            if not exists:
                question = Question(DOES_NOT_EXIST_TITLE, DOES_NOT_EXIST_TEXT.format(str(parent_element)))
                question.element_xpath = self.generator.get_parser(filepath).get_element_xpath(element)
                assignment_set_a1 = AssignmentSet(Assignment(self.ignore))
                assignment_set_a1.setup_context(diff=diff, filepath=filepath)
                a1 = Answer(IGNORE, assignment_set_a1)

                assignment_set_a2 = AssignmentSet(Assignment(self.recreate))
                assignment_set_a2.setup_context(diff=diff, filepath=filepath)
                a2 = Answer(RECREATE, assignment_set_a2)
                question.answers = [a1, a2]
                questions.append(question)
            else:
                method = self.subelement_change

        assignment_set = AssignmentSet(Assignment(method))
        assignment_set.setup_context(diff=diff, filepath=filepath, task=self)
        return assignment_set, questions

    def evaluate_single_element_template(self, diff):
        folder_name = class_object_to_underscore_format(type(self))
        path = os.path.join(self._generator.templates_path, folder_name)

    def get_traces(self, diff):
        return self._generator.tracer.get_traces(diff.key, self._generator.id)

    def get_selection_trace(self, element):
        if type(element) is Document:
            return "//body/div[@_id=\"" + str(element.id) + "\"]"
        if issubclass(type(element), Field):
            return "//body/div[@_id=\"" + str(element.container.id) + "\"]/ul/li[@_id=\"" + str(element.id) + "\"]"

    def get_insertion_trace(self, element):
        if type(element) is Document:
            return "//body"
        if issubclass(type(element), Field):
            return "//body/div[@_id=\"" + str(element.container.id) + "\"]/ul"

    def get_property_traces(self, element):
        properties = {}
        if type(element) is Document:
            properties["id"] = ["//body/div[@_id=\"" + str(element.id) + "\"]"]
            properties["name"] = ["//body/div[@_id=\"" + str(element.id) + "\"]/p[text()=\"My document name: " +
                                  str(element.name) + "\"]"]
            properties["project.id"] = ["//body/div[@_id=\"" + str(element.id) +
                                        "\"]/p[text()=\"Parent project id:  " + str(element.container.id) + "\"]"]
            properties["project.name"] = ["//body/div[@_id=\"" + str(element.id) +
                                          "\"]/p[text()=\"Parent project name:  " + str(element.container.name) + "\"]"]

        if issubclass(type(element), Field):
            properties["id"] = ["//body/div[@_id=\"" + str(element.container.id) + "\"]/ul/li[@_id]"]
            properties["name"] = ["//body/div[@_id=\"" + str(element.container.id) + "\"]/ul/li[@_id=\"" +
                                  str(element.id) + "\"][text()=\"Field (" + str(element.name) + ")\"]",

                                  "//body/div[@_id=\"" + str(element.container.id) + "\"]/ul/li[@_id=\"" +
                                  str(element.id) + "\"]"]

        return properties
