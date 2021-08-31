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

    @staticmethod
    def get_same_keys(first_dict, second_dict):
        same_keys = []
        for first_key in first_dict:
            if first_key in second_dict:
                same_keys.append(first_key)

        return same_keys

    @staticmethod
    def compare_keys(first_dict, second_dict, list_to_skip=None):
        """
        Compares two dictionaries by keys. Keys are grouped into three collections:
            1) The same keys collection
            2) Collection of only the first dictionary keys
            3) Collection of only the second dictionary keys
        :param first_dict:
        :param second_dict:
        :param list_to_skip: string list of key names that should not be included
        :return:
        """

        if list_to_skip is None:
            list_to_skip = []

        same_keys = []
        only_in_first = []

        for first_key in first_dict:
            if first_key in list_to_skip:
                continue
            if first_key in second_dict:
                same_keys.append(first_key)
            else:
                only_in_first.append(first_key)

        only_in_second = list(second_dict.keys() - first_dict.keys() - set(list_to_skip))

        return same_keys, only_in_first, only_in_second


if __name__ == '__main__':
    d1 = {"key1": None, "key2": None, "key3": None}
    d2 = {"key2": None, "key3": None}
    same, only_first, only_second = DictionaryUtility.compare_keys(d1, d2, ["key2"])
    print(same)
    print(only_first)
    print(only_second)
