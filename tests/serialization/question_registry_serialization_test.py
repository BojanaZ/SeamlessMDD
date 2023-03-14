import unittest
from tests.dummy_structures import question_registry
from transformation.conflict_resolution.question_registry import QuestionRegistry


class QuestionRegistrySerializationTest(unittest.TestCase):

    def test_qr_json_serialization_to_file(self):
        self.question_registry.save_to_json()
        new_qr = QuestionRegistry.load_from_json()

        assert self.question_registry == new_qr

    def setUp(self):
        self.question_registry = question_registry()

