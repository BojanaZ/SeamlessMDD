from transformation.generators.diff_generators.base_diff_generator import BaseDiffGenerator
from transformation.tasks.diff_tasks.demo_manual_traces_task import DiffDemoManualTracingTask
from transformation.generators.encoders.generator_json_encoder import BaseGeneratorJSONEncoder
from parsers.my_html_parser import MyHTMLParser
from utilities.utilities import get_project_root
import os
import json


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
        task = DiffDemoManualTracingTask(generator=self, template_name_=self._file_template_path)
        self.tasks.append(task)

        # # pass Jinja environment to tasks:
        # for task in self.tasks:
        #     task.environment = self.environment

    def generate(self, model, out_folder):
        super().generate(model, out_folder)

    # def add_task(self, task):
    #     # pass Jinja environment to tasks:
    #     for task in self.tasks:
    #         task.environment = self.environment

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
