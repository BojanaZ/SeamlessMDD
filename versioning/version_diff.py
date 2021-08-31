import gettext
from utilities.dictionary_utility import DictionaryUtility


class VersionDiff(object):

    def __init__(self, previous_element, current_element):
        self._previous_element = previous_element
        self._current_element = current_element
        self._diff = self.calculate_diff()

    @property
    def previous_element(self):
        return self._previous_element

    @previous_element.setter
    def previous_element(self, previous_element):
        self._previous_element = previous_element

    @property
    def current_element(self):
        return self._current_element

    @current_element.setter
    def current_element(self, current_element):
        self._current_element = current_element

    @property
    def diff(self):
        return self._diff

    @diff.setter
    def diff(self, diff):
        self._diff = diff

    def calculate_diff(self):
        if type(self._previous_element)!=type(self._current_element):
            raise TypeError

        return DictionaryUtility.get_different_keys(self.previous_element, self.current_element)







