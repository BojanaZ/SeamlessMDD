import unittest
from transformation.generator_handler import GeneratorHandler
from transformation.generators.documents_output_generator import DocumentsOutputGenerator
from transformation.data_manipulation import DataManipulation
from tests.dummy_structures import dummy_data
import os


class GeneratorHandlerSerializationTest(unittest.TestCase):

    def test_generator_handler_dill_serialization(self):
        self.handler.save_to_dill("handler.dill")

        new_handler = self.handler.load_from_dill("handler.dill")

        assert new_handler == self.handler

    def test_generator_handler_json_serialization(self):
        self.handler.save_to_json("handler.json")

        new_handler = self.handler.load_from_json("handler.json")

        assert new_handler == self.handler

    def setUp(self):
        model = dummy_data()

        data_manipulation = DataManipulation()
        data_manipulation.update_model(model)

        self.handler = GeneratorHandler()
        generator = DocumentsOutputGenerator()
        generator.initialize()
        self.handler.register(generator)

        elements = data_manipulation.get_latest_model().elements
        for element_id, element in elements.items():
            self.handler.element_generator_table.insert_pair(element, generator)

    def tearDown(self):
        try:
            os.remove("handler.json")
            os.remove("handler.dill")
        except FileNotFoundError:
            pass
