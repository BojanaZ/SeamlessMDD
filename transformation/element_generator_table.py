import dill
import json
import os

from utilities.exceptions import ElementNotFoundError, GeneratorNotFoundError
from utilities.utilities import get_project_root


class ElementGeneratorTable(object):

    def __init__(self, project_path):
        self._by_element = {}
        self._by_generator = {}

        if project_path is None:
            project_path = get_project_root()

        self._data_loading_path = os.path.join(project_path, 'files')

    @property
    def data_loading_path(self):
        return self._data_loading_path

    @data_loading_path.setter
    def data_loading_path(self, value):
        self._data_loading_path = value

    def save_to_dill(self, filename=None):
        if filename is None:
            filename = "table.dill"
        path = os.path.join(self._data_loading_path, filename)

        with open(path, "wb") as file:
            dill.dump(self, file)

    @staticmethod
    def load_from_dill(self, filename=None):
        if filename is None:
            if filename is None:
                filename = "table.dill"
        path = os.path.join(self._data_loading_path, filename)

        with open(path, "rb") as file:
            return dill.load(file)

    def to_json(self):
        table_by_element = {}

        for element_id, generators in self._by_element.items():
            table_by_element[element_id] = []
            for generator_id, value in generators.items():
                table_by_element[element_id].append((generator_id, value))

        table = {'table_by_element': table_by_element}

        return json.dumps(table, default=lambda o: o.to_dict(), indent=4)

    def to_dict(self):
        table_by_element = {}

        for element_id, generators in self._by_element.items():
            table_by_element[element_id] = []
            for generator_id, value in generators.items():
                table_by_element[element_id].append((generator_id, value))

        return {'table_by_element': table_by_element}

    def to_simple_json(self):
        """Converts table to element id to generator id mapping"""
        table_by_element = {}
        table_by_generator = {}

        for element, generators in self._by_element.items():
            table_by_element[element.id] = {}
            for generator, value in generators.items():
                table_by_element[element.id][generator.id] = value

        for generator, elements in self._by_generator.items():
            table_by_generator[generator.id] = {}
            for element, value in elements.items():
                table_by_generator[generator.id][element.id] = value

        table_ = {'table_by_element': table_by_element,
                  'table_by_generator': table_by_generator}

        return json.dumps(table_)

    @staticmethod
    def from_simple_json(content):
        return json.loads(content)

    def from_json(self, table_):
        if type(table_) == str:
            table_ = json.loads(table_)

        table_by_element = table_['table_by_element']

        found_element_ids = set()
        all_json_generators_ids = set()
        found_old_generator_ids = set()

        for element_id, generators in self._by_element.items():
            element_found = False
            for json_element_id, json_generators in table_by_element.items():
                if element_id == int(json_element_id):
                    element_found = True
                    found_element_ids.add(element_id)
                    for generator_id, value in generators.items():
                        for json_generator_id, json_value in json_generators:
                            if generator_id == json_generator_id:
                                found_old_generator_ids.add(generator_id)
                                self.update_pair(element_id, generator_id, json_value)
                                break
                        else:
                            self.remove_connection(element_id, generator_id)
                    break
            if not element_found:
                self.deactivate_element(element_id)

        for json_element_id, json_generators in table_by_element.items():
            element_id = int(json_element_id)
            if element_id not in found_element_ids:
                raise ElementNotFoundError("Deserialized element not registered.")

        for json_element_id, json_generators in table_by_element.items():
            for json_generator_id, json_value in json_generators:
                all_json_generators_ids.add(json_generator_id)

        for json_generator_id in all_json_generators_ids:
            if json_generator_id not in found_old_generator_ids:
                raise GeneratorNotFoundError("Deserialized generator is not registered.")

    def register_from_json(self, table_):
        if type(table_) == str:
            table_ = json.loads(table_)

        table_by_element = table_['table_by_element']

        found_element_ids = set()
        found_old_generator_ids = set()

        for element_id, generators in self._by_element.items():
            element_found = False
            for json_element_id, json_generators in table_by_element.items():
                if element_id == int(json_element_id):
                    element_found = True
                    found_element_ids.add(element_id)
                    for generator_id, value in generators.items():
                        for json_generator_id, json_value in json_generators:
                            if generator_id == json_generator_id:
                                found_old_generator_ids.add(generator_id)
                                self.load_pair(element_id, generator_id, json_value)
                                break
                        else:
                            self.remove_connection(element_id, generator_id)
                    break
            if not element_found:
                self.deactivate_element(element_id)

        for json_element_id, json_generators in table_by_element.items():
            for json_generator_id, json_value in json_generators:
                if json_generator_id not in found_old_generator_ids:
                    self.load_pair(int(json_element_id), json_generator_id, json_value)

    def update_for_all_generators(self, element_id, value=True):
        if element_id not in self._by_element:
            self._by_element[element_id] = {}

        for key in self._by_generator.keys():
            last_generated_version = self._by_generator[key][element_id]["last_generated_version"]
            self._by_generator[key][element_id] = {"value": value, "last_generated_version": last_generated_version}
            self._by_element[element_id][key] = {"value": value, "last_generated_version": last_generated_version}

    def update_pair(self, element_id, generator_id, value=True):

        if element_id not in self._by_element:
            self._by_element[element_id] = {}

        if generator_id not in self._by_element[element_id]:
            last_generated_version = -1
        else:
            last_generated_version = self._by_element[element_id][generator_id]["last_generated_version"]

        self._by_element[element_id][generator_id] = {"value": value, "last_generated_version": last_generated_version}

        if generator_id not in self._by_generator:
            self._by_generator[generator_id] = {}

        if element_id not in self._by_generator[generator_id]:
            last_generated_version = -1
        else:
            last_generated_version = self._by_generator[generator_id][element_id]["last_generated_version"]

        self._by_generator[generator_id][element_id] = {"value": value, "last_generated_version": last_generated_version}

    def load_pair(self, element_id, generator_id, value):

        if element_id not in self._by_element:
            self._by_element[element_id] = {}

        self._by_element[element_id][generator_id] = value

        if generator_id not in self._by_generator:
            self._by_generator[generator_id] = {}

        self._by_generator[generator_id][element_id] = value

    '''
        Inserts element-generator pair to the table. If generator id is not specified, element is connected with all
        available generator.
    '''
    def insert_pair(self, element_id, generator_id):
        self.update_pair(element_id, generator_id, True)

    def get_generator_ids(self, element_id):
        return (generator_id for generator_id, value_pair
                in self._by_element[element_id].items() if value_pair["value"])

    def get_element_ids(self, generator_id):
        return (element_id for element_id in self._by_generator[generator_id] if
                self._by_generator[generator_id][element_id])

    def get_active_generators(self):
        for generator_id in self._by_generator.keys():
            for element_id, value_pair in self._by_generator[generator_id].items():
                if value_pair["value"]:
                    yield generator_id
                    break

    def check_generator_status(self, generator):
        return any(self._by_generator[generator].values())

    def change_generator_status(self, generator, new_value=True):
        for element in self._by_generator[generator].keys():
            self._by_generator[generator][element] = new_value

    def get_connection_data(self, element_id, generator_id):
        if element_id in self._by_element.keys():
            if generator_id in self._by_element[element_id]:
                return self._by_element[element_id][generator_id]
        return {"value": False, "last_generated_version": -1}

    def remove_connection(self, element_id, generator_id):
        self.update_pair(element_id, generator_id, False)

    def remove_element(self, element_id):
        if element_id in self._by_element:
            del self._by_element[element_id]
            for generator_id in self._by_generator:
                if element_id in self._by_generator[generator_id]:
                    del self._by_generator[generator_id][element_id]

    def remove_generator(self, generator_id):
        if generator_id in self._by_generator:
            del self._by_generator[generator_id]
            for element_id in self._by_element:
                if generator_id in self._by_element[element_id]:
                    del self._by_element[element_id][generator_id]

    def deactivate_element(self, element_id):
        if element_id in self._by_element:
            self.update_for_all_generators(element_id, False)

    def is_element_deactivated_for_generator(self, element_id, generator_id):
        return self.get_connection_data(element_id, generator_id)["value"]

    def deactivate_generator(self, generator_id):
        if generator_id in self._by_generator:
            for element_id in self._by_generator[generator_id]:
                self.update_pair(element_id, generator_id, False)

    def has_element_by_id(self, element_id):
        return element_id in self._by_element

    def has_generator_by_id(self, generator_id):
        return generator_id in self._by_generator

    def update_last_generated_versions(self, element_id, generator_id, last_generated_version):
        self._by_element[element_id][generator_id] = {"value": True, "last_generated_version": last_generated_version}

        self._by_generator[generator_id][element_id] = {"value": True, "last_generated_version": last_generated_version}

    def __str__(self):
        result = "| %30s " % ""
        header = "| %15s " * len(self._by_element)

        elements = self._by_element.keys()

        result += header % tuple(self._by_element.keys()) + "|\n"
        result += "=" * len(result) + "\n"
        for generator in self._by_generator:
            result += "| %30s " % generator
            for element in elements:
                if generator in self._by_element[element] and self._by_element[element][generator]:
                    result += "| %15s " % "X"
                else:
                    result += "| %15s " % "O"
            result += "|\n"

        return result

    def __eq__(self, other):

        # for generator in self._by_generator:
        #     found_other_generator = False
        #     for other_generator in other._by_generator:
        #         if generator.id == other_generator.id and generator == other_generator:
        #             found_other_generator = True
        #             other_elements = other._by_generator[other_generator]
        #
        #             found_other_element = False
        #             for element in self._by_generator[generator]:
        #                 for other_element in other_elements:
        #                     if element.id == other_element.id and element == other_element:
        #                         found_other_element = True
        #                         value = self._by_generator[generator][element]
        #                         other_value = other._by_generator[other_generator][other_element]
        #                         if value == other_value:
        #                             break
        #                 else:
        #                     return False
        #
        #             if not found_other_element:
        #                 return False
        #
        #     if not found_other_generator:
        #         return False

        for element_id, generators in self._by_element.items():
            found_other_element = False
            for other_element_id, other_generators in other._by_element.items():
                if element_id == other_element_id:
                    found_other_element = True

                    found_other_generator = False
                    for generator_id, value in generators.items():
                        for other_generator_id, other_value in other_generators.items():
                            if generator_id == other_generator_id:
                                found_other_generator = True
                                value = self._by_element[element_id][generator_id]
                                if value == other_value:
                                    break
                        else:
                            return False

                    if not found_other_generator:
                        return False

            if not found_other_element:
                return False

        return True

    def save_to_json(self, filename=None):
        content = self.to_json()

        if filename is None:
            filename = "table.json"

        file_path = os.path.join(self._data_loading_path, filename)

        with open(file_path, "w") as file:
            file.write(content)
