from diff.deepdiff_extractor import diffs_from_deepdiff
from utilities.exceptions import ElementNotFoundError
from diff.diff import Diff
from diff.operation_type import OperationType


class DiffStore(object):

    def __init__(self):
        pass

    @staticmethod
    def get_diffs_for_model_elements(element_pairs):

        overall_diffs = {}
        for old_element, new_element in element_pairs:
            try:
                element_diffs = diffs_from_deepdiff(old_element, new_element)
            except ElementNotFoundError:
                element_diffs = {None: [Diff(None, None, new_element, None, type(new_element), None, new_element,
                                             operation_type=OperationType.ADD), '', new_element.id]}
            overall_diffs.update(element_diffs)
        return overall_diffs
