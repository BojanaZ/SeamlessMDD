import os

from transformation.tasks.diff_tasks.base_manual_traces_task import BaseManualTracingTask
from FirstProject.metamodel.document import Document
from FirstProject.metamodel.field import Field


class DiffDemoManualTracingTask(BaseManualTracingTask):

    def __init__(self, generator, priority=2, template_name=None):
        if template_name is not None and template_name != "":
            self._template_name = template_name
        else:
            self._template_name = "first_template.tpl"

        self._additional_templates_path = "diff_demo_task/"
        self._additional_templates = {}
        #self._template_folder_path = "../../generator_templates/"
        self.insert_additional_templates()

        super().__init__(generator=generator, priority=priority, template_name=template_name)

    def filtered_elements(self, model):
        """Return iterator over elements in model that are passed to the above template."""
        for element in model.elements:
            if type(element) == Document:
                yield element

    def insert_additional_templates(self):
        self._additional_templates["field"] = "field_template.tpl"
        self._additional_templates["fields"] = "fields_template.tpl"
        self._additional_templates["document"] = "document_template.tpl"

    def relative_path_for_element(self, diff):
        """Return relative file path receiving the generator output for given element."""
        try:
            document_name = diff.old_object_ref.name
        except:
            document_name = diff.new_object_ref.name
        return document_name + ".task1.html"

    def get_relative_path(self, filepath, element, **kwargs):
        if isinstance(element, Document):
            return os.path.join(self._additional_templates_path, self._additional_templates["document"])
        elif issubclass(type(element), Field):
            return os.path.join(self._additional_templates_path, self._additional_templates["field"])

    def get_selection_trace(self, element):
        if type(element) is Document:
            return "//body/div[@_id=\"" + str(element.id) + "\"]"
        if issubclass(type(element), Field):
            return "//body/div[@_id=\"" + str(element.parent_container.id) + "\"]/ul/li[@_id=\"" + str(element.id) + "\"]"

    def get_insertion_trace(self, element):
        if type(element) is Document:
            return "//body"
        if issubclass(type(element), Field):
            return "//body/div[@_id=\"" + str(element.parent_container.id) + "\"]/ul"

    def get_property_traces(self, element):
        properties = {}
        if type(element) is Document:
            properties["id"] = ["//body/div[@_id=\"" + str(element.id) + "\"]"]
            properties["name"] = ["//body/div[@_id=\"" + str(element.id) + "\"]/p[text()=\"My document name: " +
                                  str(element.name) + "\"]"]
            properties["project.id"] = ["//body/div[@_id=\"" + str(element.id) +
                                        "\"]/p[text()=\"Parent project id:  " + str(element.parent_container.id) + "\"]"]
            properties["project.name"] = ["//body/div[@_id=\"" + str(element.id) +
                                          "\"]/p[text()=\"Parent project name:  " + str(element.parent_container.name) + "\"]"]

        if issubclass(type(element), Field):
            properties["id"] = ["//li[@_id]"]

            properties["label"] = ["//li[@_id=\"" +
                                   str(element.id) + "\"]//label[text()=\"Field (" + str(element.label) + ")\"]"]

            properties["name"] = ["//li[@_id=\"" + str(element.id) + "\"]"]

        return properties
