from abc import ABC

from transformation.tasks.diff_tasks.base_diff_task import BaseDiffTask


class DiffDemoTask(BaseDiffTask, ABC):

    def __init__(self, priority=2, _template_name=None, **kwargs):
        if not _template_name:
            self._template_name = _template_name
        else:
            self._template_name = "documents_output_template.html"
        super().__init__(priority=priority, template_name=_template_name)

    @property
    def template_name(self):
        return self._template_name

    def filtered_elements(self, model):
        """Return iterator over elements in model that are passed to the above template."""
        for document in model.elements:
            yield document

    def relative_path_for_element(self, document):
        """Return relative file path receiving the generator output for given element."""
        return "./"+document.name+".task1.html"

    def generate_content(self, element, filepath):
        """Actual file generation from model element."""
        raise NotImplementedError()
