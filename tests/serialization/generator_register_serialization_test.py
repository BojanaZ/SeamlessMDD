import unittest
from transformation.generator_handler import GeneratorHandler
from transformation.generators.documents_output_generator import DocumentsOutputGenerator
import os


class GeneratorRegisterSerializationTest(unittest.TestCase):

    def test_generators_register_dill_serialization(self):
        self.generator_register.save_to_dill("generators.dill")

        new_generator_register = self.generator_register.load_from_dill("generators.dill")

        assert new_generator_register == self.generator_register

    def test_generators_register_json_serialization(self):
        self.generator_register.save_to_json("generators.json")

        new_generator_register = self.generator_register.load_from_json("generators.json")

        assert new_generator_register == self.generator_register

    def setUp(self):
        self.handler = GeneratorHandler()
        generator = DocumentsOutputGenerator()
        generator.initialize()
        self.handler.register(generator)
        self.generator_register = self.handler.generators

    def tearDown(self):
        try:
            os.remove("generators.json")
            os.remove("generators.dill")
        except FileNotFoundError:
            pass
