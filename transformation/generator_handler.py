import json
import os
import dill

from element_generator_table import ElementGeneratorTable
from transformation.generators.generator_register import GeneratorRegister
from transformation.conflict_resolution.question_registry import QuestionRegistry
from transformation.tasks.task_heap import Heap
from utilities.utilities import get_project_root
from diff.diff_store import DiffStore

from preview.preview import Preview


class GeneratorHandler(object):

    def __init__(self, project=None):
        project_path = project.path
        if project_path is None:
            project_path = get_project_root()

        self._element_generator_table = ElementGeneratorTable(project=project)
        self._generators = GeneratorRegister(project=project)
        self._question_registry = QuestionRegistry()

        if project_path is None:
            project_path = get_project_root()

        self._project = project

        self._data_loading_path = os.path.join(project_path, 'storage')

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        self._project = value

    @property
    def data_loading_path(self):
        return self._data_loading_path

    @data_loading_path.setter
    def data_loading_path(self, value):
        self._data_loading_path = value

    @property
    def generators(self):
        return self._generators

    @generators.setter
    def generators(self, value):
        self._generators = value

    @property
    def question_registry(self):
        return self._question_registry

    @question_registry.setter
    def question_registry(self, value):
        self._question_registry = value

    @property
    def element_generator_table(self):
        return self._element_generator_table

    @element_generator_table.setter
    def element_generator_table(self, value):
        self._element_generator_table = value

    def register(self, generator):
        self._generators.register(generator)

    def get_generator(self, generator_id):
        return self._generators[generator_id]

    def to_json(self):
        table = self.element_generator_table.to_dict()
        generators = self._generators.to_dict()
        question_registry = self._question_registry.to_dict()

        return json.dumps({
            '_data_loading_path': self._data_loading_path,
            'element_generator_table': table,
            '_generators': generators,
            "_question_registry": question_registry
        }, indent=4)

    def save_to_json(self, path=None):
        content = self.to_json()

        if path is None:
            path = os.path.join(self._data_loading_path, "handler.json")

        with open(path, "w") as file:
            file.write(content)

    def save_to_dill(self, path=None):

        if path is None:
            path = os.path.join(self._data_loading_path, "handler.dill")

        with open(path, "wb") as file:
            dill.dump(self, file)

    def load_from_json(self, path=None):
        if path is None:
            path = os.path.join(self._data_loading_path, "handler.json")

        try:
            with open(path, "r") as file:
                json_content = json.load(file)
                return self.from_json(json_content)
        except OSError:
            print("Unable to load generator handler.")

    def from_json(self, content):

        if type(content) == str:
            content = json.loads(content)

        self.data_loading_path = content['_data_loading_path']
        self.generators = self._generators.from_json(content['_generators'], self.project)
        self.element_generator_table.register_from_json(content['element_generator_table'])
        self._question_registry = QuestionRegistry.from_json(content['_question_registry'])
        return self

    def load_from_dill(self, path=None):
        if path is None:
            path = os.path.join(self._data_loading_path, "handler.dill")

        try:
            with open(path, "rb") as file:
                return dill.load(file)
        except OSError:
            print("Unable to load generators.")

    def __eq__(self, other):
        if self.data_loading_path != other.data_loading_path:
            return False

        if self.generators != other.generators:
            return False

        if self.element_generator_table != other.element_generator_table:
            return False

        return True

    def __ne__(self, other):
        return not self == other

    def update_element_generator_table(self, generator_element_table_update_pairs, version_id):
        for element_id, generator_id in generator_element_table_update_pairs:
            self._element_generator_table.update_last_generated_versions(element_id, generator_id, version_id)

    def get_active_generators(self):
        generator_list = []
        for gen_id in self.element_generator_table.get_active_generators():
            generator_list.append(self._generators[gen_id])
        return generator_list

    def initialize(self):
        self.generate_answered_questions()

    def build_task_heap(self, generator_list):
        task_heap = Heap()
        sorted_tasks = []
        for generator in generator_list:
            task_heap.extend(generator.tasks)
            task_heap.sort()
            sorted_tasks = task_heap.get_items()
        return sorted_tasks

    def finalize(self, generator_list, table_update_pairs, data_manipulation, model_version_number,
                 write_to_storage=True):
        if write_to_storage:
            for generator in generator_list:
                generator.flush()
                self.update_element_generator_table(table_update_pairs,
                                                    model_version_number)
            data_manipulation.update_model_after_generation()
        else:
            for generator in generator_list:
                generator.reload()

    def generate_diffs(self, diffs, task, last_generated_version, latest_model_version, outfolder):
        for property_diffs in diffs.values():
            for property_diff in property_diffs:
                preview = Preview(last_generated_version, latest_model_version)
                task.preview = preview
                questions = task.run(property_diff, outfolder)
                yield questions, outfolder, preview

    def generate_all_generators(self, data_manipulation, outfolder_name=None, write_to_storage=True):

        self.initialize()

        generator_list = self.get_active_generators()
        sorted_tasks = self.build_task_heap(generator_list)

        outfolder_full_path = os.path.join(self.project.path, outfolder_name)

        model = data_manipulation.get_latest_model()
        latest_model_version = data_manipulation.get_latest_version_number()

        generator_element_table_update_pairs = []

        for task in sorted_tasks:
            generator_id = task.generator.id
            elements = task.filtered_elements(model)
            for element in elements:
                connection_data = self.element_generator_table.get_connection_data(element.id, generator_id)
                last_generated_version = 0
                if connection_data["value"]:
                    last_generated_version = connection_data["last_generated_version"]

                generator_element_table_update_pairs.append((element.id, generator_id))
                old_and_new_element_pairs = data_manipulation.generate_old_and_new_pairs(last_generated_version,
                                                                                         [element])
                diffs = DiffStore.get_diffs_for_model_elements(old_and_new_element_pairs)
                for property_diffs in diffs.values():
                    for property_diff in property_diffs:
                        preview = Preview(last_generated_version, latest_model_version, self.project)
                        task.preview = preview
                        questions = task.run(property_diff, outfolder_full_path)
                        yield questions, outfolder_full_path, preview

        self.finalize(generator_list, generator_element_table_update_pairs, data_manipulation,
                      latest_model_version, write_to_storage)

    def generate_single_generator(self, data_manipulation, generator_id, outfolder=None, write_to_storage=True):

        self.initialize()
        generator = self._generators[generator_id]

        sorted_tasks = self.build_task_heap([generator])
        latest_model_version = data_manipulation.get_latest_version_number()

        generator_element_table_update_pairs = []

        for task in sorted_tasks:
            for element in task.filtered_elements(data_manipulation):
                connection_data = self.element_generator_table.get_connection_data(element.id, generator_id)
                if connection_data["value"]:
                    last_generated_version = connection_data["last_generated_version"]
                    generator_element_table_update_pairs.append((element.id, generator_id))

                    old_and_new_element_pairs = data_manipulation.generate_old_and_new_pairs(last_generated_version,
                                                                                             [element])
                    diffs = DiffStore.get_diffs_for_model_elements(old_and_new_element_pairs)

                    for property_diffs in diffs.values():
                        for property_diff in property_diffs:
                            preview = Preview(last_generated_version, latest_model_version)
                            task.preview = preview
                            questions = task.run(property_diff, outfolder)
                            yield questions, outfolder, preview

            self.finalize([generator], generator_element_table_update_pairs,
                          data_manipulation, latest_model_version, write_to_storage)
            data_manipulation.update_model()

    def generate_single_element(self, element, data_manipulation, outfolder=None, write_to_storage=True):

        self.initialize()

        generator_ids = self.element_generator_table.get_generator_ids(element.id)
        generator_list = []

        for generator_id in generator_ids:
            generator = self._generators.get_generator_by_id(generator_id)
            generator_list.append(generator)

        sorted_tasks = self.build_task_heap(generator_list)

        generator_element_table_update_pairs = []
        model = data_manipulation.get_latest_model()
        latest_model_version = data_manipulation.get_latest_version_number()

        for task in sorted_tasks:
            for model_element in task.filtered_elements(model):

                connection_data = self.element_generator_table.get_connection_data(model_element.id, task.generator.id)
                if connection_data["value"]:
                    last_generated_version = connection_data["last_generated_version"]
                    generator_element_table_update_pairs.append((element.id, task.generator.id))

                    old_and_new_element_pairs = data_manipulation.generate_old_and_new_pairs(last_generated_version,
                                                                                             [model_element])
                    diffs = DiffStore.get_diffs_for_model_elements(old_and_new_element_pairs)
                    for property_diffs in diffs.values():
                        for property_diff in property_diffs:
                            preview = Preview(last_generated_version, latest_model_version)
                            task.preview = preview
                            questions = task.run(property_diff, outfolder)
                            yield questions, outfolder, preview

        self.finalize(generator_list, generator_element_table_update_pairs,
                      data_manipulation, latest_model_version, write_to_storage)

    def generate_answered_questions(self):
        for question in self._question_registry.questions.values():
            if question.is_answered():
                question.chosen_answer.assignment_set.execute_set()


if __name__ == '__main__':
    handler = GeneratorHandler()
    handler = handler.load_from_json('../storage/handler.json')
    table = handler.element_generator_table
