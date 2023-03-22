from abc import ABC

from multigen.jinja import TemplateFileTask
import logging
import os

_logger = logging.getLogger(__name__)


class ValidationTask(TemplateFileTask, ABC):

    def __init__(self,  generator):
        super().__init__()
        self._generator = generator
        self._methods = []
        self._questions = []
        self._preview = None

    @property
    def generator(self):
        return self._generator

    @generator.setter
    def generator(self, gen):
        self._generator = gen

    @property
    def methods(self):
        return self._methods

    @methods.setter
    def methods(self, methods_):
        self._methods = methods_

    @property
    def questions(self):
        return self._questions

    @questions.setter
    def questions(self, questions_):
        self._questions = questions_

    @property
    def preview(self):
        return self._preview

    @preview.setter
    def preview(self, preview):
        self._preview = preview

    def run(self, element, outfolder):
        """Apply this task to model element."""
        filepath = self.relative_path_for_element(element)
        if outfolder and not os.path.isabs(filepath):
            filepath = os.path.join(outfolder, filepath)

        _logger.debug('{!r} --> {!r}'.format(element, filepath))

        self.ensure_folder(filepath)
        self.preview.old_view = str(self.generator.get_parser(filepath))
        self.preview.filepath = filepath
        assignment_set, questions = self.generate_file(element, filepath)

        if len(questions) == 0:
            assignment_set.execute_set()
            assignment_set.preview = self._preview
            self.preview.new_view = str(self.generator.get_parser(filepath))
        else:
            for question in questions:
                question.task = self
            return questions
