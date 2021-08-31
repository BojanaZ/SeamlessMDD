import unittest
from tests.dummy_structures import dummy_data
from transformation.data_manipulation import DataManipulation
import json

class DataManipulationSerializationTest(unittest.TestCase):

    def test_dm_dill_serialization(self):
        self.data_manipulation.save_to_dill()

        loaded_data_manipulation = self.data_manipulation.load_from_dill()

        assert self.data_manipulation == loaded_data_manipulation

    def test_dm_json_serialization_to_file(self):
        self.data_manipulation.save_to_json()
        new_dm = DataManipulation.load_from_json()

        assert self.data_manipulation == new_dm

    def test_dm_json_serialization_from_json_string(self):
        json_string = self.data_manipulation.to_json()

        new_dm = DataManipulation.from_json(json.loads(json_string))
        assert self.data_manipulation == new_dm

        json_dict = json.loads(json_string)
        json_dict["path"] = ""

        faulty_new_dm = DataManipulation.from_json(json_dict)
        assert self.data_manipulation != faulty_new_dm

    def setUp(self):

        self.data_manipulation = DataManipulation()
        self.model = dummy_data()
        self.data_manipulation.update_model(self.model)