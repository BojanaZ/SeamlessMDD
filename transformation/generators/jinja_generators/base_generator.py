from multigen.jinja import JinjaGenerator
import os
import json
from json import JSONEncoder
from utilities.utilities import get_class_from_parent_module, get_project_root


class BaseGenerator(JinjaGenerator):

    def __init__(self, id_=-1, file_path="", file_content="", file_template_path=""):
        self._id = id_
        self._file_path = file_path
        self._file_content = file_content
        self._file_template_path = file_template_path

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

    def create_environment(self, **kwargs):
        """
        Return a new Jinja environment.

        Derived classes may override method to pass additional parameters or to change the template
        loader type.
        """
        return super().create_environment(**kwargs)

    def generate(self, model, outfolder):
        super().generate(model, outfolder)

    def flush(self):
        with open(self._file_path, 'w') as file:
            file.write(self._file_content)

    def to_json(self):
        return json.dumps(self, cls=BaseGeneratorJSONEncoder)

    @classmethod
    def from_json(cls, data):

        if type(data) == str:
            data = json.loads(data)

        new_object = cls()

        if data['tasks']:
            new_object.tasks = []
            environment = new_object.create_environment()
            for task in data['tasks']:
                _type = get_class_from_parent_module(task['class'], 'transformation.tasks')
                task = _type.from_json(task)
                task.environment = environment
                new_object.tasks.append(task)

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


class BaseGeneratorJSONEncoder(JSONEncoder):

    def default(self, object_):

        if isinstance(object_, BaseGenerator):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if
                           key not in ['tasks', '__len__']}

            object_dict['class'] = type(object_).__name__

            if hasattr(object_, "tasks"):
                object_dict["tasks"] = []

                for task in object_.tasks:
                    task_dict = task.to_dict()
                    object_dict["tasks"].append(task_dict)

            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return JSONEncoder.default(self, object_)
