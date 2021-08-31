import unittest
import random
import json

from transformation.data_manipulation import DataManipulation
from transformation.generator_handler import GeneratorHandler
from transformation.generators.generator_register import GeneratorRegister
from transformation.generators.base_generator import BaseGenerator
from metamodel.model import Model
from tests.dummy_structures import dummy_data

from api.app import create_app


class APITest(unittest.TestCase):

    def setUp(self):
        self.data_manipulation = DataManipulation().load_from_dill()
        self.handler = GeneratorHandler().load_from_dill()

        self.app = create_app(self.data_manipulation, self.handler)
        self.client = self.app.test_client

    def test_home_get(self):
        """Test / (GET request)"""

        response = self.client().get('/')
        self.assertEqual(response.status_code, 200)
        loaded_model = Model.from_json(response.data.decode())
        self.assertEqual(loaded_model, self.data_manipulation.get_latest_model())

    def test_model_get(self):
        """Test /model (GET request)"""
        response = self.client().get('/model')
        self.assertEqual(response.status_code, 200)
        loaded_model = Model.from_json(response.data.decode())
        self.assertEqual(loaded_model, self.data_manipulation.get_latest_model())

        # All versions are removed
        self.data_manipulation.versions = {}

        other_response = self.client().get('/model')
        self.assertEqual(other_response.status_code, 404)

    def test_model_post(self):
        """Test /model (POST request)

        Test case deletes random element, then posts it.
        """

        new_model = dummy_data()
        element_key_to_delete = random.choice(list(new_model.elements.keys()))
        new_model.elements[element_key_to_delete].deleted = True
        test_json = new_model.to_json()

        result = self.client().post(
            '/model',
            json=test_json)

        self.assertEqual(result.status_code, 201)

        result = self.client().get('/model')
        data = Model.from_json(result.data.decode())

        self.assertEqual(result.status_code, 200)

        self.assertEqual(data, new_model)

    def test_model_by_version_get(self):
        """Test /models/<version_id> (GET request)"""

        # Firstly, find existing version - latest
        response = self.client().get('/model')
        latest_model = Model.from_json(response.data.decode())
        latest_version = latest_model.version

        # Accesses latest model
        response = self.client().get('/models/'+str(latest_version))
        self.assertEqual(response.status_code, 200)
        loaded_model = Model.from_json(response.data.decode())
        self.assertEqual(loaded_model.version, latest_version)
        self.assertEqual(loaded_model, latest_model)

        # Accesses random model version
        random_version = random.choice(list(self.data_manipulation.versions.keys()))
        random_model = self.data_manipulation.versions[random_version]
        response = self.client().get('/models/'+str(random_version))
        self.assertEqual(response.status_code, 200)
        loaded_model = Model.from_json(response.data.decode())
        self.assertEqual(loaded_model.version, random_version)
        self.assertEqual(loaded_model, random_model)

        # Random version is removed
        del self.data_manipulation.versions[random_version]
        response = self.client().get('/models/'+str(random_version))
        self.assertEqual(response.status_code, 404)

    def test_generators_get(self):
        """Test /generators (GET request)"""
        response = self.client().get('/generators')
        self.assertEqual(response.status_code, 200)
        loaded_generators = GeneratorRegister.from_json(response.data.decode())

        self.assertEqual(loaded_generators, self.handler.generators)

        self.handler.generators = None
        response = self.client().get('/generators')
        self.assertEqual(response.status_code, 404)

    def test_generators_post(self):
        """Test /generators (POST request)"""

        # Generators register is received
        response = self.client().get('/generators')
        loaded_generators = GeneratorRegister.from_json(response.data.decode())

        # Random generator is removed
        random_generator_id = random.choice(list(loaded_generators.keys()))
        del loaded_generators[random_generator_id]

        generators_json = loaded_generators.to_json()

        # New register is sent
        result = self.client().post(
            '/generators',
            json=generators_json)

        self.assertEqual(result.status_code, 201)

        # Checks if changes were registered
        response = self.client().get('/generators')
        loaded_generators_after_removal = GeneratorRegister.from_json(response.data.decode())
        self.assertEqual(loaded_generators, loaded_generators_after_removal)

        # Empty register is created
        empty_register = GeneratorRegister()
        empty_generator_register_json = empty_register.to_json()

        result = self.client().post(
            '/generators',
            json=empty_generator_register_json)

        self.assertEqual(result.status_code, 201)

        response = self.client().get('/generators')
        loaded_generators_after_all_generators_removal = GeneratorRegister.from_json(response.data.decode())
        self.assertEqual(empty_register, loaded_generators_after_all_generators_removal)

    def test_generator_by_id_get(self):
        """Test /generators/<generator_id> (GET request)"""
        # Random id is selected, generator with that id is received
        random_id = random.choice(list(self.handler.generators.keys()))
        random_generator = self.handler.generators[random_id]

        response = self.client().get('/generators/'+str(random_id))
        self.assertEqual(response.status_code, 200)
        loaded_generator = BaseGenerator.from_json(response.data.decode())
        self.assertEqual(loaded_generator, random_generator)

        # random_id generator is removed
        del self.handler.generators[random_id]
        response = self.client().get('/generators/'+str(random_id))
        self.assertEqual(response.status_code, 404)

    # def test_generator_by_id_post(self):
    #     """Test /generators/<generator_id> (POST request)"""
    #     random_id = random.choice(list(self.handler.generators.keys()))
    #
    #     response = self.client().get('/generators/'+str(random_id))
    #     loaded_generator = BaseGenerator.from_json(response.data.decode())
    #     loaded_generator.tasks = []
    #     json_after_update = loaded_generator.to_json()
    #
    #     result = self.client().post(
    #         '/generators/'+str(random_id),
    #         json=json_after_update)
    #
    #     self.assertEqual(result.status_code, 201)
    #
    #     # Checks if changes were registered
    #     response = self.client().get('/generators'+str(random_id))
    #     loaded_generator_after_removing_tasks = BaseGenerator.from_json(response.data.decode())
    #     self.assertEqual(loaded_generator, loaded_generator_after_removing_tasks)
    #
    #     # New random generator is found
    #     random_id = random.choice(list(self.handler.generators.keys()))
    #     response = self.client().get('/generators/' + str(random_id))
    #     loaded_generator = BaseGenerator.from_json(response.data.decode())
    #     loaded_generator.file_path = "test_path"
    #
    #     json_after_second_update = loaded_generator.to_json()
    #
    #     result = self.client().post(
    #         '/generators/' + str(random_id),
    #         json=json_after_second_update)
    #
    #     self.assertEqual(result.status_code, 201)
    #
    #     # Checks if changes were registered
    #     response = self.client().get('/generators' + str(random_id))
    #     loaded_generator_after_changing_path = BaseGenerator.from_json(response.data.decode())
    #     self.assertEqual(loaded_generator, loaded_generator_after_changing_path)

    def test_element_generator_table_get(self):
        """Test /table (GET request)"""
        response = self.client().get('/table')
        self.assertEqual(response.status_code, 200)
        self.handler.element_generator_table.from_json(response.data.decode())

    def test_element_generator_table_post(self):
        """Test /table (POST request)"""
        # Gets table and removes random model element
        table_dict = self.handler.element_generator_table.to_dict()
        element_id = random.choice(list(table_dict["table_by_element"].keys()))
        del table_dict["table_by_element"][element_id]

        table_json = json.dumps(table_dict)

        result = self.client().post(
            '/table',
            json=table_json)

        self.assertEqual(result.status_code, 200)
        self.assertTrue(self.handler.element_generator_table.is_element_deactivated_by_id(element_id))

        # Changes one connection
        table_dict = self.handler.element_generator_table.to_dict()
        element_id = random.choice(list(table_dict["table_by_element"].keys()))

        n = len(table_dict['table_by_element'][element_id])
        random_index = random.randrange(0, n)
        generator, value = table_dict['table_by_element'][element_id][random_index]
        new_value = not value
        del table_dict['table_by_element'][element_id][random_index]
        table_dict['table_by_element'][element_id].append((generator, new_value))

        table_json = json.dumps(table_dict)

        result = self.client().post(
            '/table',
            json=table_json)

        self.assertEqual(result.status_code, 200)
        current_table_value = self.handler.element_generator_table.check_connection_by_ids(element_id, generator["_id"])
        self.assertEqual(current_table_value, new_value)

    def test_generate_single_element_get(self):
        """Test /generation/<element_id> (GET request)"""
        pass
