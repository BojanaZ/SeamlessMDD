import unittest
from metamodel.field import Field
from diff.diff_calculator import get_diff
from tests.dummy_structures import dummy_data

class DiffCalculatorTest(unittest.TestCase):

    def test_get_diff_field(self):
        result = get_diff(self.old_field, self.new_field)
        assert len(result) == 1

        print([str(diff) for diff in result])

    def test_get_diff_model_simple_change(self):
        result = get_diff(self.old_model, self.new_model)
        assert len(result) == 1

    def test_get_diff_model_root_element_simple_change(self):
        self.new_model.root.text = "RANDOM TEXT"
        result = get_diff(self.old_model, self.new_model)
        assert len(result) == 3

    def test_get_diff_model_subelement_simple_change(self):
        del self.new_model.elements[12]
        result = get_diff(self.old_model, self.new_model)
        assert len(result) == 2

    def setUp(self):

        self.old_field = Field(11, "F1", False, "f1")
        self.new_field = Field(11, "F11", False, "f1")

        self.old_model = dummy_data()
        self.new_model = dummy_data()
        self.new_model.version = 99

