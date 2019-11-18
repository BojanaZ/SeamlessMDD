class DictionaryUtility(object):

    @staticmethod
    def get_different_keys(first_dict, second_dict):
        different_keys = []
        for first_key in first_dict:
            second_value = second_dict.get(first_key, None)
            if not second_value or first_dict[first_key] != second_value:
                different_keys.append(first_key)
        keys_only_in_second = second_dict.keys()-first_dict.keys()
        different_keys.extend(keys_only_in_second)
        return different_keys