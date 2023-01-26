from deepdiff import DeepDiff
from diff.diff import Diff
from diff.operation_type import OperationType
import re


def extract_property_name(extracted_property, iterable=False, placeholder_word="root"):

    # index = string.index(placeholder_word)
    # last_index = index + len(placeholder_word)
    text_between_parents = re.findall('\[(.*?)\]',extracted_property)
    if iterable:
        text_between_parents = text_between_parents[:-1]
    print(text_between_parents)
    property_name = ".".join(text_between_parents)
    property_name = property_name.translate(str.maketrans({'\'': '', '\"': '', '\\': '', '_':''}))
    return property_name


def extract_property_name_with_key(extracted_property, iterable=False, placeholder_word="root"):

    # index = string.index(placeholder_word)
    # last_index = index + len(placeholder_word)
    text_between_parents = re.findall('\[(.*?)\]',extracted_property)
    if iterable:
        text_between_parents = text_between_parents[:-1]

    found_key = False
    found_key_index = 0
    for text in text_between_parents:
        if text.isnumeric():
            found_key = True
            found_key_index += 1
            break
        found_key_index += 1

    if found_key:
        property_name = ".".join(text_between_parents[found_key_index:])
    else:
        property_name = ".".join(text_between_parents)

    property_name = property_name.translate(str.maketrans({'\'': '', '\"': '', '\\': '', '_': ''}))
    return property_name


def property_name_contains_key(extracted_property):

    # index = string.index(placeholder_word)
    # last_index = index + len(placeholder_word)
    text_between_parents = re.findall('\[(.*?)\]',extracted_property)

    for text in text_between_parents:
        if text.isnumeric():
            return True
    return False


def extract_detailed_property_name(extracted_property, iterable=False, placeholder_word="root"):
    # index = string.index(placeholder_word)
    # last_index = index + len(placeholder_word)
    text_between_parents = re.findall('\[(.*?)\]', extracted_property)
    if iterable:
        text_between_parents = text_between_parents[:-1]

    found_key = False
    found_key_index = 0
    key = None
    for text in text_between_parents:
        if text.isnumeric():
            found_key = True
            found_key_index += 1
            key = int(text)
            break
        found_key_index += 1

    if found_key:
        property_name = ".".join(text_between_parents[found_key_index:])

    else:
        property_name = ".".join(text_between_parents)

    property_name = property_name.translate(str.maketrans({'\'': '', '\"': '', '\\': '', '_': ''}))

    prefix = ".".join(text_between_parents[:found_key_index-1])
    prefix = prefix.translate(str.maketrans({'\'': '', '\"': '', '\\': '', '_': ''}))
    return property_name, key, prefix


def diffs_from_deepdiff(old_element, new_element, **kwargs):
    old_element_dict = old_element.to_dict()
    new_element_dict = new_element.to_dict()
    diffs = DeepDiff(old_element_dict, new_element_dict, verbose_level=2, **kwargs)
    changed_properties = {}
    for change in diffs:
        iterable = False

        if change == 'values_changed':
            operation_type = OperationType.CHANGE

        elif change == 'dictionary_item_added':
            operation_type = OperationType.SUBELEMENT_ADD
            iterable = True

        elif change == 'dictionary_item_removed':
            operation_type = OperationType.SUBELEMENT_REMOVE
            iterable = True

        elif change == 'iterable_item_added':
            operation_type = OperationType.SUBELEMENT_ADD
            iterable = True

        elif change == 'iterable_item_removed':
            operation_type = OperationType.SUBELEMENT_REMOVE
            iterable = True

        for property_name, value in diffs[change].items():

            old_value = None
            new_value = None
            key = ''
            prefix = ''

            if operation_type == OperationType.CHANGE and property_name_contains_key(property_name):
                operation_type = OperationType.SUBELEMENT_CHANGE
                property_name, key, prefix = extract_detailed_property_name(property_name, iterable)
                property_name = property_name
                key = key
                prefix = prefix
                #new_element = getattr(new_element, prefix)[key]
                #old_element = getattr(old_element, prefix)[key]
            else:
                property_name = extract_property_name(property_name, iterable)

            if iterable:
                key = value['_id']
                if 'added' in change:
                    new_value = new_element.elements[value['_id']]
                elif 'removed' in change:
                    old_value = old_element.elements[value['_id']]

            else:
                old_value = value['old_value']
                new_value = value['new_value']

            diff = Diff(property_name, old_value, new_value, None, None, old_element, new_element, operation_type,
                        prefix, key)

            if property_name in changed_properties:
                changed_properties[property_name].append(diff)
            else:
                changed_properties[property_name] = [diff]

    return changed_properties
