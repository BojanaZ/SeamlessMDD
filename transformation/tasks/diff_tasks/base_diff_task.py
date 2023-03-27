from multigen.jinja import TemplateFileTask
from transformation.tasks.priority_mixin import PriorityMixin
from transformation.tasks.base_task_json_encoder import BaseTaskJSONEncoder
import json
from transformation.tasks.validation_task import ValidationTask
from diff.operation_type import OperationType
from tracing.trace_type import TraceType
from tracing.trace import Trace


class BaseDiffTask(ValidationTask, PriorityMixin):

    def __init__(self, priority=2, template_name=None, generator=None):
        super().__init__(generator=generator)
        self.priority = priority
        if template_name is not None:
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

    def generate_file(self, element, filepath):
        """Actual file generation from model element."""
        raise NotImplementedError()

    @classmethod
    def from_json(cls, data):
        return cls(data['_priority'], data['_template_name'])

    def to_json(self):
        return json.dumps(self, cls=BaseTaskJSONEncoder)

    def to_dict(self):
        return BaseTaskJSONEncoder().default(self)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if self.priority != other.priority:
            return False

        if self._template_name != other.template_name:
            return False

        if self.global_context != other.global_context:
            return False

        return True

    def __ne__(self, other):
        return not self == other

    def get_element(self, diff):
        element = diff.new_object_ref

        if diff.operation_type == OperationType.REMOVE:
            element = diff.old_object_ref
        elif diff.operation_type == OperationType.SUBELEMENT_ADD:
            element = diff.new_value
        elif diff.operation_type == OperationType.SUBELEMENT_CHANGE:
            element = diff.new_object_ref.elements[diff.key]
        elif diff.operation_type == OperationType.SUBELEMENT_REMOVE:
            element = diff.old_value
        return element

    def insert_traces(self, diff):

        element = self.get_element(diff)

        if self._generator.tracer.has_traces(element.id, self._generator.id):
            return

        if diff.operation_type in [OperationType.SUBELEMENT_ADD,
                                   OperationType.ADD]:
            trace_type = TraceType.INSERTION
            trace_path = self.get_insertion_trace(element)
        else:
            trace_type = TraceType.SELECTION
            trace_path = self.get_selection_trace(element)

        trace = Trace(trace_type, trace_path)
        self._generator.tracer.add_element_trace(element.id, self._generator.id, trace)
