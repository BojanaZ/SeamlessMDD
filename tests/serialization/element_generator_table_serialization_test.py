import unittest
from transformation.generators.documents_output_generator import DocumentsOutputGenerator
from metamodel.element_generator_table import ElementGeneratorTable
from utilities.exceptions import ElementNotFoundError, GeneratorNotFoundError
from tests.dummy_structures import dummy_data
import os

class TableSerializationTest(unittest.TestCase):

    def test_table_dill_serialization(self):
        old_table = self.table
        self.table.save_to_dill("table.dill")

        new_table = self.table.load_from_dill("table.dill")

        assert new_table == old_table


    def test_table_complex_json_serialization_element_exception(self):
        table_json = self.table.to_json()
        self.table = ElementGeneratorTable()
        self.assertRaises(ElementNotFoundError, self.table.from_json, table_json)

    def test_table_complex_json_serialization_generator_exception(self):
        table_json = self.table.to_json()
        generator_to_delete = list(self.table._by_generator.keys())[0]
        for element, generators in self.table._by_element.items():
            if generator_to_delete in self.table._by_element[element]:
                del self.table._by_element[element][generator_to_delete]

        del self.table._by_generator[generator_to_delete]

        self.assertRaises(GeneratorNotFoundError, self.table.from_json, table_json)

    def setUp(self):
        data = dummy_data()
        generator = DocumentsOutputGenerator()
        generator.initialize()
        self.table = ElementGeneratorTable()
        elements = data.elements
        for element in elements.values():
            self.table.insert_pair(element, generator)

    def tearDown(self):
        try:
            os.remove("table.dill")
        except FileNotFoundError:
            pass


