from utilities.dictionary_utility import DictionaryUtility
from diff.diff import Diff
from diff.operation_type import OperationType
from metamodel.element import ModelElement
from metamodel.model import Model


def get_flat_element_diff(old_dict, new_dict, object_ref):

    diffs = []

    same, only_first, only_second = DictionaryUtility.compare_keys(old_dict, new_dict, ['_container'])

    for key in same:
        if old_dict[key] != new_dict[key]:
            diffs.append(Diff(key, old_dict[key], new_dict[key], object_ref, OperationType.CHANGE))

    for key in only_first:
        diffs.append(Diff(key, old_dict[key], None, object_ref, OperationType.REMOVE))

    for key in only_second:
        diffs.append(Diff(key, None, new_dict[key], object_ref, OperationType.ADD))

    return diffs


def get_deep_element_diff(old_dict, new_dict, object_ref):

    diffs = []

    same, only_first, only_second = DictionaryUtility.compare_keys(old_dict, new_dict, ['_container'])

    for key in same:
        diffs.extend(compare_items(old_dict[key], new_dict[key], object_ref, key))
        if old_dict[key] != new_dict[key]:
            diffs.append(Diff(key, old_dict[key], new_dict[key], object_ref, OperationType.CHANGE))

    for key in only_first:
        diffs.append(Diff(key, old_dict[key], None, object_ref, OperationType.REMOVE))

    for key in only_second:
        diffs.append(Diff(key, None, new_dict[key], object_ref, OperationType.ADD))

    return diffs


def handle_iterable(old_iterable, new_iterable, object_ref, property_name):
    diffs = []
    if type(old_iterable) is dict and type(new_iterable) is dict:
        diffs.extend(get_deep_element_diff(old_iterable, new_iterable, object_ref))
        return diffs

    for old_item in old_iterable:
        if old_item not in new_iterable:
            for new_item in new_iterable:
                try:
                    if old_item.id == new_item.id:
                        diffs.extend(get_full_model_diff(old_item, new_item))
                except TypeError:
                    diffs.append(Diff(property_name, old_item, None, object_ref, OperationType.REMOVE))

    for new_item in new_iterable:
        if new_item not in old_iterable:
            for old_item in old_iterable:
                try:
                    if old_item.id == new_item.id:
                        diffs.extend(get_full_model_diff(old_item, new_item))
                except TypeError:
                    diffs.append(Diff(property_name, None, new_item, object_ref, OperationType.ADD))

    return []


def compare_items(old_item, new_item, object_ref, property_name):
    diffs = []

    if old_item is new_item:
        return diffs

    if type(old_item) is Model and type(new_item) is Model:
        return diffs

    if old_item is None and new_item is not None:
        diffs.append(Diff(property_name, None, new_item, object_ref, OperationType.ADD_PROPERTY))

    elif old_item is not None and new_item is None:
        diffs.append(Diff(property_name, old_item, None, object_ref, OperationType.REMOVE_PROPERTY))

    elif issubclass(type(old_item), ModelElement):
        diffs.extend(get_full_model_diff(old_item, new_item))

    elif hasattr(old_item, '__iter__'):
        diffs.extend(handle_iterable(old_item, new_item, object_ref, property_name))

    elif old_item != new_item:
        diffs.append(Diff(property_name, old_item, new_item, object_ref, OperationType.CHANGE_PROPERTY))

    return diffs


def get_full_model_diff(old_model, new_model):
    old_dict = old_model.get_first_level_dict()
    new_dict = new_model.get_first_level_dict()

    diffs = []

    same, only_first, only_second = DictionaryUtility.compare_keys(old_dict, new_dict, ['_container'])

    for key in same:
        diffs.extend(compare_items(old_dict[key], new_dict[key], new_model, key))

    for key in only_first:
        diffs.append(Diff(key, old_dict[key], None, new_model, OperationType.REMOVE_PROPERTY))

    for key in only_second:
        diffs.append(Diff(key, None, new_dict[key], new_model, OperationType.ADD_PROPERTY))

    return diffs


def filter_unique_diff(diffs):
    filtered_diffs = []
    
    for diff in diffs:
        found = False
        for unique_diff in filtered_diffs:
            if diff == unique_diff:
                found = True
                break
        if not found:
            filtered_diffs.append(diff)

    return filtered_diffs
