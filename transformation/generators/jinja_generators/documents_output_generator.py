import json
import os
from transformation.tasks.jinja_tasks.my_task import MyTask
from transformation.generators.jinja_generators.base_generator import BaseGenerator
from transformation.generators.encoders.generator_json_encoder import BaseGeneratorJSONEncoder
from utilities.utilities import get_project_root


class DocumentsOutputGenerator(BaseGenerator):

    def __init__(self, id_=-1, file_path="", file_content="", file_template_path=""):
        self.initialize()
        super().__init__(id_, file_path, file_content, file_template_path)
        #self.tasks = []

    # Root path where Jinja templates are found.
    templates_path = os.path.join(
        get_project_root(),
        'templates'
    )

    def initialize(self, file_template_path=None):
        self.tasks = []
        if file_template_path is not None:
            self.tasks.append(MyTask(_template_name=self._file_template_path))
        else:
            self.tasks.append(MyTask(_template_name=file_template_path))

    def generate(self, model, outfolder):
        super().generate(model, outfolder)

    def flush(self):
        with open(self._file_path, 'w') as file:
            file.write(self._file_content)

    def to_json(self):
        return json.dumps(self, cls=BaseGeneratorJSONEncoder)

    def to_dict(self):
        return BaseGeneratorJSONEncoder().default(self)

    def __str__(self):
        return str(type(self).__name__)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if not super(BaseGenerator, self).__eq__(other):
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
