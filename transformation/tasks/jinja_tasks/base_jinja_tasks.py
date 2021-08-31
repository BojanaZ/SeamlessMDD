from multigen.jinja import JinjaTask
from transformation.tasks.priority_mixin import PriorityMixin
from transformation.tasks.base_task_json_encoder import BaseTaskJSONEncoder
import json

class BaseJinjaTask(JinjaTask, PriorityMixin):

    def __init__(self, priority=2, formatter=None, template_name=None):
        super().__init__(formatter=formatter)
        self.priority = priority
        self._template_name = 'model_data.tpl'
        if template_name:
            self._template_name = template_name

    @property
    def template_name(self):
        return self._template_name

    def filtered_elements(self, model):
        """Return iterator over elements in model that are passed to the above template."""
        for element in model:
            yield element

    def relative_path_for_element(self, document):
        """Return relative file path receiving the generator output for given element."""
        return "./"+document.name+".html"

    @classmethod
    def from_json(cls, data: dict):
        #return cls(formatter=data['formatter'], template_name=data["_template_name"])
        return cls(**data)

    def to_json(self):
        return json.dumps(self, cls=BaseTaskJSONEncoder)

    def to_dict(self):
        return BaseTaskJSONEncoder().default(self)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if self.priority != other.priority:
           return False

        if self._template_name != other._template_name:
            return False

        if self.global_context != other.global_context:
            return False

        return True

    def __ne__(self, other):
        return not self == other
