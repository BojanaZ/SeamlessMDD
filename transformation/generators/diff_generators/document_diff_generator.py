from generators.diff_generators.base_diff_generator import BaseDiffGenerator
import os
from utilities.utilities import get_project_root
from tasks.diff_tasks.html_demo_task import DiffDemoTask
import json
from generators.jinja_generators.base_generator import BaseGeneratorJSONEncoder
from parsers.my_html_parser import MyHTMLParser


class DocumentDiffGenerator(BaseDiffGenerator):

    def __init__(self, id_=-1, file_path="", file_content="", file_template_path=""):
        super().__init__(id_, file_path, file_content, file_template_path, MyHTMLParser)
        self.tasks = []

    templates_path = os.path.join(
        get_project_root(),
        'templates'
    )

    def initialize(self):
        self.tasks = []
        self.tasks.append(DiffDemoTask(generator=self, template_name_=self._file_template_path))

        # # pass Jinja environment to tasks:
        # for task in self.tasks:
        #     task.environment = self.environment

    def generate(self, model, out_folder):
        super().generate(model, out_folder)

    # def add_task(self, task):
    #     # pass Jinja environment to tasks:
    #     for task in self.tasks:
    #         task.environment = self.environment

    def to_json(self):
        return json.dumps(self, cls=BaseGeneratorJSONEncoder)

    def to_dict(self):
        return BaseGeneratorJSONEncoder().default(self)

    def __str__(self):
        return str(type(self).__name__)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if not super(BaseDiffGenerator, self).__eq__(other):
            return False

        for task in self.tasks:
            for other_task in other.tasks:
                if task == other_task:
                    break
            else:
                return False

        return True

    def __ne__(self, other):
        return not self == other
