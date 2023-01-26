import json
import os
import dill

from metamodel.element_generator_table import ElementGeneratorTable
from tests.dummy_structures import dummy_data
from transformation.data_manipulation import DataManipulation
from transformation.generators.generator_register import GeneratorRegister
from transformation.tasks.task_heap import Heap
from utilities.utilities import get_project_root


class GeneratorHandler(object):

    def __init__(self, loading_path=None):
        self._element_generator_table = ElementGeneratorTable()
        self._generators = GeneratorRegister()

        if loading_path is None:
            self._data_loading_path = os.path.join(get_project_root(), 'files')
        else:
            self._data_loading_path = loading_path

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

        return json.dumps({
            '_data_loading_path': self._data_loading_path,
            'element_generator_table': table,
            '_generators': generators
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
        self.generators = self._generators.from_json(content['_generators'])
        self.element_generator_table.register_from_json(content['element_generator_table'])
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

    def generate_by_element(self, model_, outfolder=None):

        task_heap = Heap()

        for model_element in model_:
            generator_list = self.element_generator_table.get_generators(model_element.id)

            for generator_id in generator_list:
                generator = self._generators[generator_id]
                generator.create_environment()
                for task in generator.tasks:
                    task_heap.add(task)

        task_heap.sort()
        sorted_tasks = task_heap.get_items()
        for task in sorted_tasks:
            for element in task.filtered_elements(model_):
                task.run(element, outfolder)
            #task.invoke()

    def generate_by_generator(self, model_, outfolder=None):

        generator_id_list = self.element_generator_table.get_active_generators()

        task_heap = Heap()

        for generator_id in generator_id_list:

            generator = self._generators.get_generator_by_id(generator_id)

            for model_element in model_:
                for task in generator.tasks:
                    task_heap.add(task)

        task_heap.sort()
        sorted_tasks = task_heap.get_items()

        for task in sorted_tasks:
            for element in task.filtered_elements(model_):
                task.run(element, outfolder)

                #task.invoke()

    def generate_single_generator(self, data_manipulation_, generator, outfolder=None):

        elements = self.element_generator_table.get_elements(generator)

        task_heap = Heap()

        task_heap.extend(generator.tasks)

        task_heap.sort()
        sorted_tasks = task_heap.get_items()

        for task in sorted_tasks:
            for element in task.filtered_elements(data_manipulation_):
                task.run(element, outfolder)

    def generate_single_element(self, element, data_manipulation, outfolder=None):
        generator_ids = self.element_generator_table.get_generators(element.id)
        task_heap = Heap()

        for generator_id in generator_ids:
            generator = self._generators.get_generator_by_id(generator_id)
            task_heap.extend(generator.tasks)

        task_heap.sort()
        sorted_tasks = task_heap.get_items()

        model = data_manipulation.get_latest_model()

        for task in sorted_tasks:
            for model_element in task.filtered_elements(model):
                if model_element == element:
                    task.run(element, outfolder)


if __name__ == '__main__':
    handler = GeneratorHandler()
    model = dummy_data()

    data_manipulation = DataManipulation()
    data_manipulation.update_model(model)
