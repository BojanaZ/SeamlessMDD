import dill
import json
from utilities.exceptions import ElementNotFoundError, GeneratorNotFoundError
import os


class ElementGeneratorTable(object):

    def __init__(self):
        self._by_element = {}
        self._by_generator = {}

    def save_to_dill(self, path=None):
        if path is None:
            path = "../files/table.dill"

        with open(path, "wb") as file:
            dill.dump(self, file)

    @staticmethod
    def load_from_dill(path=None):
        if path is None:
            path = "../files/table.dill"

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
                                self.update_pair(element_id, generator_id, json_value)
                                break
                        else:
                            self.remove_connection(element_id, generator_id)
                    break
            if not element_found:
                self.deactivate_element(element_id)

        for json_element_id, json_generators in table_by_element.items():
            for json_generator_id, json_value in json_generators:
                if json_generator_id not in found_old_generator_ids:
                    self.update_pair(int(json_element_id), json_generator_id, json_value)

    def update_pair(self, element_id, generator_id, value=True, all_generators=False):
        if element_id not in self._by_element:
            self._by_element[element_id] = {}

        if all_generators:
            for key in self._by_generator.keys():
                self._by_generator[key][element_id] = value
                self._by_element[element_id][key] = value
            return

        self._by_element[element_id][generator_id] = value

        if generator_id not in self._by_generator:
            self._by_generator[generator_id] = {}

        self._by_generator[generator_id][element_id] = value

    '''
        Inserts element-generator pair to the table. If generator id is not specified, element is connected with all
        available generator.
    '''
    def insert_pair(self, element, generator=None):
        insert_for_all_generators = generator is None
        self.update_pair(element.id, generator.id, True, insert_for_all_generators)

    def get_generators(self, element_id):
        return (generator for generator, value in self._by_element[element_id].items() if value)

    def get_elements(self, generator):
        return (element for element in self._by_generator[generator] if
                self._by_generator[generator][element])

    def get_active_generators(self):
        return (generator for generator in self._by_generator.keys() if
                self._by_generator[generator])

    def check_generator_status(self, generator):
        return any(self._by_generator[generator].values())

    def change_generator_status(self, generator, new_value=True):
        for element in self._by_generator[generator].keys():
            self._by_generator[generator][element] = new_value

    def check_connection(self, element, generator):
        if element.id in self._by_element.keys():
            if generator.id in self._by_element[element.id]:
                return self._by_element[element.id][generator.id]
        return False

    def check_connection_by_ids(self, element_id, generator_id):
        for current_element_id in self._by_element.keys():
            if current_element_id == element_id:
                for current_generator_id in self._by_element[current_element_id].keys():
                    if current_generator_id == generator_id:
                        return self._by_element[current_element_id][current_generator_id]
        return False

    def remove_connection(self, element, generator):
        if element in self._by_element:
            if generator in self._by_element[element]:
                self._by_element[element][generator] = False
                self._by_generator[generator][element] = False

    def remove_element(self, element):
        if element in self._by_element:
            del self._by_element[element]
            for generator in self._by_generator:
                if element in self._by_generator[generator]:
                    del self._by_generator[generator][element]

    def remove_generator(self, generator):
        if generator in self._by_generator:
            del self._by_generator[generator]
            for element in self._by_element:
                if generator in self._by_element[element]:
                    del self._by_element[element][generator]

    def deactivate_element(self, element):
        if element in self._by_element:
            for generator in self._by_element[element]:
                self._by_element[element][generator] = False
            for generator in self._by_generator:
                if element in self._by_generator[generator]:
                    self._by_generator[generator][element] = False

    def is_element_deactivated(self, element):
        if element in self._by_element:
            for generator in self._by_element[element]:
                if self._by_element[element][generator]:
                    return False
            for generator in self._by_generator:
                if element in self._by_generator[generator]:
                    if self._by_generator[generator][element]:
                        return False
        return True

    def is_element_deactivated_by_id(self, element_id):
        element = self.get_element_by_id(element_id)
        if element is not None:
            return self.is_element_deactivated(element)

        return True

    def deactivate_generator(self, generator):
        if generator in self._by_generator:
            for element in self._by_generator[generator]:
                self._by_generator[generator][element] = False
            for element in self._by_element:
                if generator in self._by_element[element]:
                    self._by_element[element][generator] = False

    def turn_all_generators_for_element(self, element):
        generators = self._by_generator.keys()
        if element not in self._by_element:
            self._by_element[element] = {}
        for generator in generators:
            self._by_element[element][generator] = True

    def has_element_by_id(self, element_id):
        return self.get_element_by_id(element_id) is not None

    def get_element_by_id(self, id_):
        for element_id in self._by_element.keys():
            if id_ == element_id:
                return element_id

        return None

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

    def save_to_json(self, path=None):
        content = self.to_json()

        file_path = "table.json"
        if path is not None:
            file_path = os.path.join(path, file_path)

        with open(file_path, "w") as file:
            file.write(content)


if __name__ == '__main__':
    table = ElementGeneratorTable()
    table = table.load_from_dill()
    print(table)





