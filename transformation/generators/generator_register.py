import dill
import json
from utilities.utilities import get_file_path_for_format, get_class_from_parent_module
from utilities.utilities import get_project_root


class GeneratorRegister(dict):

    def __init__(self, project_path=None):
        super(GeneratorRegister, self).__init__()

        file_paths = get_file_path_for_format("generators", ["json", "dill"], project_path)

        if project_path is None:
            self._project_path = get_project_root()
        else:
            self._project_path = project_path

        self._data_path_dill = file_paths["dill"]
        self._data_path_json = file_paths["json"]

    def get_generator_by_id(self, id_):
        return self[id_]

    @property
    def data_path_dill(self):
        return self._data_path_dill

    @data_path_dill.setter
    def data_path_dill(self, value):
        self._data_path_dill = value

    @property
    def data_path_json(self):
        return self._data_path_json

    @data_path_json.setter
    def data_path_json(self, value):
        self._data_path_json = value

    @property
    def project_path(self):
        return self._project_path

    @project_path.setter
    def project_path(self, value):
        self._project_path = value

    @staticmethod
    def new_id_generator():
        id_ = 0
        while True:
            yield id_
            id_ += 1

    def generate_new_id(self):
        id_generator = self.new_id_generator()
        while True:
            id_ = next(id_generator)
            if id_ not in self:
                return id_

    def register(self, generator):
        generator_id = self.generate_new_id()
        self[generator_id] = generator
        generator.id = generator_id

    def save_to_dill(self, path=None):

        if path is None:
            path = self._data_path_dill

        with open(path, "wb") as file:
            dill.dump(self, file)

    def load_from_dill(self, path=None):
        if path is None:
            path = self._data_path_dill

        try:
            with open(path, "rb") as file:
                return dill.load(file)
        except OSError:
            print("Unable to load generators.")

    def save_to_json(self, path=None):

        if path is None:
            path = self._data_path_json

        with open(path, "w") as file:
            generators_json = self.to_json()
            file.write(generators_json)

    def load_from_json(self, path=None):

        if path is None:
            path = self._data_path_json

        with open(path, "r") as file:
            content = file.read()
            return GeneratorRegister.from_json(content)

    def to_json(self):
        # generators = {}
        # for key, value in self._generators.items():
        #     generators[key] = value.to_dict()
        dict = GeneratorsJSONEncoder().default(self)
        return json.dumps(dict, indent=4)

    def to_dict(self):
        return GeneratorsJSONEncoder().default(self)

    def from_json(self, loaded_content):

        if type(loaded_content) == str:
            loaded_content = json.loads(loaded_content)

        new_register = GeneratorRegister()
        new_register.data_path_json = loaded_content["data_path_json"]
        new_register.data_path_dill = loaded_content["data_path_dill"]

        for generator_id, generator_dict in loaded_content["generator_register"].items():
            gen_type = get_class_from_parent_module(self._project_path, "transformation.generators")
            generator = gen_type.from_json(generator_dict)
            generator_id = int(generator_id)
            generator.id = generator_id
            new_register[generator_id] = generator
            for task in generator.tasks:
                task.generator = generator

        return new_register

    def __eq__(self, other):
        if self.data_path_json != other.data_path_json:
            return False

        if self.data_path_dill != other.data_path_dill:
            return False

        for generator_id, generator in self.items():
            if generator_id not in other:
                return False
            if generator != other[generator_id]:
                return False

        return True

    def __ne__(self, other):
        return not self == other


class GeneratorsJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, GeneratorRegister):
            object_dict = {
                "generator_register": {key: value.to_dict() for (key, value) in object_.items()},
                "data_path_dill": object_.data_path_dill,
                "data_path_json": object_.data_path_json
            }

            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)
