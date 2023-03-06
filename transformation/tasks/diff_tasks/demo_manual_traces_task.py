from transformation.tasks.diff_tasks.base_diff_task import BaseDiffTask
from metamodel.document import Document
from utilities.utilities import class_name_to_underscore_format
from utilities.exceptions import ParsingError
from jinja2 import Template
import os
from jinja_variable_extraction.jinja2schema_extraction import relevant_jinja_variables2
from tracing.trace import Trace
from diff.operation_type import OperationType


class DiffDemoTask(BaseDiffTask):

    def __init__(self, generator, priority=2, template_name_=None):
        if template_name_ is not None and template_name_ != "":
            self._template_name = template_name_
        else:
            self._template_name = "first_template.tpl"

        self._generator = generator

        super().__init__(priority=priority)

    @property
    def generator(self):
        return self._generator

    @generator.setter
    def generator(self, gen):
        self._generator = gen

    @property
    def template_name(self):
        return self._template_name

    def filtered_elements(self, model):
        """Return iterator over elements in model that are passed to the above template."""
        documents = (document for document in model.elements.values() if type(document) == Document)
        for document in documents:
            yield document

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
        return "./" + document_name + ".task1.html"

    def trace_generate_file(self, diff, filepath):
        """Actual file generation from model element."""

        leaf = True
        if diff.operation_type in [OperationType.SUBELEMENT_ADD, OperationType.SUBELEMENT_CHANGE,
                                   OperationType.SUBELEMENT_REMOVE]:
            leaf = False

        print("###")
        relevant_paths_and_elements = self.insert_traces(diff)

        print(relevant_paths_and_elements)
        print("###")
        if diff.operation_type == OperationType.ADD and not os.path.isfile(filepath):
            template_file = open("./templates/" + self._template_name)
            template = template_file.read()
            template_file.close()
            content = Template(template).render(element=diff.new_object_ref)
            file = open(filepath, "w")
            file.write(content)
            file.close()
            return

        parser = self._generator.get_parser(filepath)

        if diff.operation_type == OperationType.ADD:
            for relevant_path_and_element in relevant_paths_and_elements:
                parser.insert_element_by_path(relevant_path_and_element['old_path'],
                                              relevant_path_and_element['new_path'])

        if diff.operation_type == OperationType.REMOVE:
            id_ = diff.old_object_ref.id
            parser.remove_element_by_id(id_)

        elif diff.operation_type == OperationType.CHANGE:
            for relevant_path_and_element in relevant_paths_and_elements:
                elements = parser.get_elements_by_path(relevant_path_and_element["old_path"])
                if len(elements) > 0:
                    for element in elements:
                        parser.update_element(element, relevant_path_and_element['new_path'])
                else:
                    raise ParsingError("HTMLParser could not retrieve elements when performing " +
                                       str(diff.operation_type) + " operation.")

        elif diff.operation_type == OperationType.SUBELEMENT_ADD:
            for relevant_path_and_element in relevant_paths_and_elements:
                parser.insert_element_by_path(relevant_path_and_element['old_path'],
                                              relevant_path_and_element['new_path'])

        elif diff.operation_type == OperationType.SUBELEMENT_REMOVE:
            parser.remove_element_by_id(diff.old_value.id)

        elif diff.operation_type == OperationType.SUBELEMENT_CHANGE:
            parser.update_element_by_id(diff.key, diff.property_name, diff.new_value)

    def generate_file(self, diff, filepath):
        """Actual file generation from model element."""
        self.insert_traces(diff)

        if diff.operation_type == OperationType.ADD and not os.path.isfile(filepath):
            template_file = open("./templates/" + self._template_name)
            template = template_file.read()
            template_file.close()
            content = Template(template).render(element=diff.new_object_ref)
            file = open(filepath, "w")
            file.write(content)
            file.close()
            return

        parser = self._generator.get_parser(filepath)
        traces = self.get_traces(diff)

        if diff.operation_type == OperationType.ADD:
            for trace in traces:
                parser.insert_element_by_path(trace.old_path, trace.new_path)

        if diff.operation_type == OperationType.REMOVE:
            id_ = diff.old_object_ref.id
            parser.remove_element_by_id(id_)

        elif diff.operation_type == OperationType.CHANGE:
            for trace in traces:
                elements = parser.get_elements_by_path(trace.old_path)
                if len(elements) > 0:
                    for element in elements:
                        parser.update_element(element, trace.new_path)
                else:
                    raise ParsingError("HTMLParser could not retrieve elements when performing " +
                                       str(diff.operation_type) + " operation.")

        elif diff.operation_type == OperationType.SUBELEMENT_ADD:
            for trace in traces:
                parser.insert_element_by_path(trace.old_path,
                                              trace.new_path)

        elif diff.operation_type == OperationType.SUBELEMENT_REMOVE:
            parser.remove_element_by_id(diff.old_value.id)

        elif diff.operation_type == OperationType.SUBELEMENT_CHANGE:
            parser.update_element_by_id(diff.key, diff.property_name, diff.new_value)

    def evaluate_single_element_template(self, diff):
        folder_name = class_name_to_underscore_format(type(self))
        path = os.path.join(self._generator.templates_path, folder_name)

    def get_traces(self, diff):
        return self._generator.tracer.get_traces(diff.key, self._generator.id)

    def insert_traces(self, diff):
        leaf = diff.operation_type not in [OperationType.SUBELEMENT_ADD, OperationType.SUBELEMENT_CHANGE,
                                           OperationType.SUBELEMENT_REMOVE]

        relevant_paths_and_elements = relevant_jinja_variables2(diff, self._generator.templates_path,
                                                                self.template_name, leaf)
        for relevant_paths_and_element in relevant_paths_and_elements:
            old_path = relevant_paths_and_element['old_path']
            new_path = relevant_paths_and_element['new_path']
            trace = Trace(old_path, new_path)
            self._generator.tracer.add_element_trace(diff.key, self._generator.id, trace)

        return relevant_paths_and_elements
