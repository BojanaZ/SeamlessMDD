import os
from pyecore.resources.xmi import XMIOptions
from pyecore.resources import ResourceSet, URI

from utilities.utilities import get_project_root
import dill
import json
from metamodel.model import Model


class VersionUnavailableError(Exception):
    pass


class DataManipulation(object):

    def __init__(self, initial_file=None):
        self._versions = {}

        if initial_file is not None:
            self.path = initial_file
        else:
            self.path = os.path.join(get_project_root(), "files", "model.dill")

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

    def has_version(self, version=None):
        if version is None:
            return False
        try:
            version_int = int(version)
            if version_int in self._versions:
                return True
        except:
            return False

    def update_model_after_generation(self):
        last_model = self.get_latest_model()
        next_version = self.get_next_version_number()
        new_model = last_model.deepcopy()
        new_model.version = next_version
        self._versions[next_version] = new_model
        new_model.version = next_version

    def update_model(self, model):
        next_version = self.get_next_version_number()
        self._versions[next_version] = model
        model.version = next_version

    def get_element_by_id(self, _id, version=None):
        model = self.get_model_by_version(version)
        if _id in model:
            return model[_id]
        return None

    def generate_new_element_id(self):
        while True:
            from random import randint
            id_candidate = randint(0, 10 ^ 5)
            for model_element in self.get_latest_model():
                if id_candidate == model_element.id:
                    break
            else:
                return id_candidate

    def get_old_and_new_model_for_element(self, element):
        old_version = element.model.version
        return self._versions[old_version], self._versions[self._latest_version_number]

    def generate_old_and_new_pairs(self, old_version, elements):
        old_and_new_pairs = []

        for element in elements:
            old_and_new_pairs.append(self.generate_old_and_new_pair(old_version, element))
        return old_and_new_pairs

    def generate_old_and_new_pair(self, old_version, element):
        if old_version > -1:
            old_element = self.get_element_by_id(element.id, old_version)
        else:
            old_element = None
        return old_element, element

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
            path = os.path.join(get_project_root(), "files", "model.json")

        try:
            with open(path, "r") as file:
                content = file.read()
                loaded_content = json.loads(content)
                return DataManipulation.from_json(loaded_content)
        except OSError:
            print("Unable to load model.")

    def save_to_json(self, path=None):
        if not path:
            path = os.path.join(get_project_root(), "files", "model.json")

        try:
            with open(path, "w") as file:
                content = self.to_dict()
                json.dump(content, file, default=lambda o: o.to_dict(), indent=4)
        except OSError:
            print("Unable to load model.")

    def load_from_xmi(self, metamodel, path=None):

        if not path:
            path = os.path.join(get_project_root(), "files")

        versions_folder_path = os.path.join(path, "versions")
        if not os.path.exists(versions_folder_path):
            return

        for file_name in os.listdir(versions_folder_path):
            file_path = os.path.join(versions_folder_path, file_name)
            if os.path.isfile(file_path):
                import re
                version = int(re.findall(r'\d+',file_name)[0])

                rset = ResourceSet()
                rset.metamodel_registry[metamodel.nsURI] = metamodel
                resource = rset.get_resource(URI(file_path))
                model = resource.contents[0]
                if version not in self._versions:
                    self._versions[version] = model

    def save_to_xmi(self, metamodel, path=None):
        from pyecore.resources.xmi import XMIOptions
        from pyecore.resources import ResourceSet, URI
        import os

        if not path:
            path = os.path.join(get_project_root(), "files")

        versions_folder_path = os.path.join(path, "versions")
        if not os.path.exists(versions_folder_path):
            os.makedirs(versions_folder_path)

        for version, model in self._versions.items():
            model_path = os.path.join(versions_folder_path, "model_version_{}.xmi".format(version))

            with open(model_path, "w") as file:
                file.write("")

            rset = ResourceSet()
            resource = rset.create_resource(URI(model_path))
            resource.use_uuid = True
            resource.append(model)

            rset.metamodel_registry[metamodel.nsURI] = metamodel  # register the metamodel

            options = {
                XMIOptions.OPTION_USE_XMI_TYPE: True
            }
            resource.save(options=options)

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

        new_object._latest_version_number = data["_latest_version_number"]
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






