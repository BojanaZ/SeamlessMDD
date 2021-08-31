import unittest
from tests.api.api_test import APITest

def run_api_tests():

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # add tests to the test suite
    suite.addTests(loader.loadTestsFromTestCase(APITest))

    # initialize a runner, pass it your suite and run it
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)

if __name__ == '__main__':
    run_api_tests()