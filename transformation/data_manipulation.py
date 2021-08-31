from os.path import join
from utilities.utilities import get_project_root
import dill, json
from metamodel.model import Model


class VersionUnavailableError(Exception):
    pass


class DataManipulation(object):

    def __init__(self, initial_file=None):
        self._versions = {}

        if initial_file is not None:
            self.path = initial_file
        else:
            self.path = join(get_project_root(), "files", "model.dill")

        self._latest_version_number = -1

    @property
    def versions(self):
        return self._versions

    @versions.setter
    def versions(self, new_versions):
        self._versions = new_versions

    def get_next_version_number(self):
        self._latest_version_number += 1
        return self._latest_version_number

    def get_latest_version_number(self):
        return self._latest_version_number

    def get_latest_model(self):
        try:
            version_no = self.get_latest_version_number()
            return self._versions[version_no]
        except KeyError:
            raise VersionUnavailableError("Currently, no version is available.")

    def get_model_by_version(self, version=None):
        if version is None:
            return self.get_latest_model()
        try:
            version_int = int(version)
            return self._versions[version_int]
        except:
            raise VersionUnavailableError("Requested model version is unavailable.")

    def get_element_by_id(self, _id, version=None):
        model = self.get_model_by_version(version)
        return model[_id]

    def save_to_dill(self, path=None):
        if path is None:
            path = self.path

        with open(path, "wb") as file:
            dill.dump(self, file)

    def load_from_dill(self, path=None):
        if not path:
            path = self.path

        with open(path, "rb") as file:
            return dill.load(file)

    @staticmethod
    def load_from_json(path=None):
        if not path:
            path = join(get_project_root(),"files", "model.json")

        try:
            with open(path, "r") as file:
                content = file.read()
                loaded_content = json.loads(content)
                return DataManipulation.from_json(loaded_content)
        except OSError:
            print("Unable to load model.")

    def save_to_json(self, path=None):
        if not path:
            path = join(get_project_root(),"files", "model.json")

        try:
            with open(path, "w") as file:
                content = self.to_dict()
                json.dump(content, file, default=lambda o:o.to_dict(), indent=4)
        except OSError:
            print("Unable to load model.")

    def get_old_and_new_model_for_element(self, element):
        old_version = element.model.version
        return self._versions[old_version], self._versions[self._latest_version_number]

    def update_model(self, model):
        version = self.get_next_version_number()
        self._versions[version] = model
        model.version = version

    def to_json(self):
        return json.dumps(self, cls=DataManipulationJSONEncoder)

    @classmethod
    def from_json(cls, data):

        if type(data) == str:
            data = json.loads(data)

        if "path" not in data:
            path = None
        else:
            path = data["path"]

        new_object = cls(path)

        new_object._versions = {}
        for version_id, model_json in data['versions'].items():
            new_object._versions[int(version_id)] = Model.from_json(model_json)

        return new_object

    def to_dict(self):
        return DataManipulationJSONEncoder().default(self)

    def __contains__(self, version_no):
        return version_no in self._versions

    def __eq__(self, other):
        if self.path != other.path:
            return False

        if self._latest_version_number != self.get_latest_version_number():
            return False

        for version_no, model in self._versions.items():
            if version_no not in other:
                return False
            other_model = other.get_model_by_version(version_no)
            if model != other_model:
                return False

        return True

    def __ne__(self, other):
        return not self == other


class DataManipulationJSONEncoder(json.JSONEncoder):

    def default(self, object_):

        if isinstance(object_, DataManipulation):

            object_dict = {key: value for (key, value) in object_.__dict__.items() if
                           key not in ['_versions']}

            object_dict["versions"] = {}

            for version_number, model in object_.versions.items():
                object_dict["versions"][version_number] = model.to_dict()

            return object_dict

        else:

            # call base class implementation which takes care of

            # raising exceptions for unsupported types

            return json.JSONEncoder.default(self, object_)






