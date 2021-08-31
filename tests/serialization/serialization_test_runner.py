import unittest
from tests.serialization.data_manipulation_serialization_test import DataManipulationSerializationTest
from tests.serialization.element_generator_table_serialization_test import TableSerializationTest
from tests.serialization.generator_handler_serialization_test import GeneratorHandlerSerializationTest
from tests.serialization.generator_register_serialization_test import GeneratorRegisterSerializationTest


def run_serialization_tests():

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # add tests to the test suite
    suite.addTests(loader.loadTestsFromTestCase(DataManipulationSerializationTest))
    suite.addTests(loader.loadTestsFromTestCase(TableSerializationTest))
    suite.addTests(loader.loadTestsFromTestCase(GeneratorHandlerSerializationTest))
    suite.addTests(loader.loadTestsFromTestCase(GeneratorRegisterSerializationTest))

    # initialize a runner, pass it your suite and run it
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)


if __name__ == '__main__':
    run_serialization_tests()
