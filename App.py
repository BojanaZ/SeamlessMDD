from diff.diff_calculator import get_full_model_diff, filter_unique_diff
from tests.dummy_structures import dummy_data

if __name__ == '__main__':

    old_model = dummy_data()
    new_model = dummy_data()
    old_model.version = 1
    new_model.version = 2
    new_model.root.text = "RANDOM TEXT"
    del new_model.elements[12]
    diffs = filter_unique_diff(get_full_model_diff(old_model, new_model))

    for diff in diffs:
        print(diff)



