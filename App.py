from recreate_dummy_structures import recreate_dummy_data_manipulation, recreate_dummy_generator_handler, recreate_dummy_table
from deepdiff import DeepDiff
from diff.diff_calculator import get_full_model_diff
from tests.dummy_structures import dummy_data

if __name__ == '__main__':
    # dm = recreate_dummy_data_manipulation()
    # recreate_dummy_generator_handler()
    # recreate_dummy_table()

    old_model = dummy_data()
    new_model = dummy_data()
    old_model.version = 1
    new_model.version = 2
    new_model.root.text = "RANDOM TEXT"
    del new_model.elements[12]
    #ddiff = DeepDiff(old_model.to_dict(), new_model.to_dict())
    #print(ddiff)
    diffs = get_full_model_diff(old_model, new_model)

    filtered_diffs = []
    for diff in diffs:
        found = False
        for unique_diff in filtered_diffs:
            if diff == unique_diff:
                found = True
                break
        if not found:
            filtered_diffs.append(diff)

    for diff in filtered_diffs:
        print(diff)



