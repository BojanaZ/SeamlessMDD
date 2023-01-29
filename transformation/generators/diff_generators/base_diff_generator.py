from multigen.generator import TemplateGenerator
import os
import json
from utilities.utilities import get_project_root, get_class_from_parent_module
from generators.jinja_generators.base_generator import BaseGeneratorJSONEncoder


class BaseDiffGenerator(TemplateGenerator):

    def __init__(self, id_=-1, file_path="", file_content="", file_template_path="", parser_type=None):
        self._id = id_
        self._file_path = file_path
        self._file_content = file_content
        self._file_template_path = file_template_path
        self.parsers = {}
        self._parser_type = parser_type
        self._tracer = None

        super().__init__()

    # Root path where Jinja templates are found.
    templates_path = os.path.join(
        get_project_root(),
        'templates'
    )

    def initialize(self):
        raise NotImplementedError("Generators must implement initialize method.")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    @property
    def file_content(self):
        return self._file_content

    @file_content.setter
    def file_content(self, value):
        self._file_content = value

    @property
    def file_template_path(self):
        return self._file_template_path

    @file_template_path.setter
    def file_template_path(self, value):
        self._file_template_path = value

    @property
    def parser_type(self):
        return self._parser_type

    @parser_type.setter
    def parser_type(self, type_):
        self._parser_type = type_

    @property
    def tracer(self):
        return self._tracer

    @tracer.setter
    def tracer(self, new_ref):
        self._tracer = new_ref

    def get_parser(self, file_path):
        if file_path not in self.parsers:
            parser = self._parser_type(file_path)
            self.parsers[file_path] = parser

        return self.parsers[file_path]

    def generate(self, model, outfolder):
        super().generate(model, outfolder)

    def flush(self):
        for file_path, parser in self.parsers.items():
            parser.write_to_file(file_path)

    def to_json(self):
        return json.dumps(self, cls=BaseGeneratorJSONEncoder)

    @classmethod
    def from_json(cls, data):

        if type(data) == str:
            data = json.loads(data)

        new_object = cls()

        if data['tasks']:
            new_object.tasks = []
            for task in data['tasks']:
                _type = get_class_from_parent_module(task['class'], 'tasks')
                new_object.tasks.append(_type.from_json(task))

        return new_object

    def __str__(self):
        return str(type(self).__name__)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if self._id != other.id:
            return False

        if self._file_path != other.file_path:
            return False

        if self._file_content != other.file_content:
            return False

        if self._file_template_path != other.file_template_path:
            return False

        return True

    def __ne__(self, other):
        return not self == other
