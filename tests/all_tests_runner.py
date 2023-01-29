from tests.serialization.serialization_test_runner import run_serialization_tests
from tests.api.api_test_runner import run_api_tests


def run_all_tests():
    run_serialization_tests()
    run_api_tests()


if __name__ == '__main__':
    run_all_tests()
