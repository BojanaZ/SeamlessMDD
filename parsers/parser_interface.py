from abc import ABCMeta, abstractmethod


class IParser:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_element_by_id(self, id):
        raise NotImplementedError

    @abstractmethod
    def get_elements_by_name(self, name):
        raise NotImplementedError

    @abstractmethod
    def get_element_by_path(self, path):
        raise NotImplementedError

    @abstractmethod
    def replace_element_by_id(self, id, new_element):
        raise NotImplementedError

    @abstractmethod
    def replace_element_by_name(self, name, new_element):
        raise NotImplementedError

    @abstractmethod
    def replace_element_by_path(self, path, new_element):
        raise NotImplementedError

    @abstractmethod
    def update_element_by_id(self, id, attribute_name, new_value):
        raise NotImplementedError

    @abstractmethod
    def update_element_by_name(self, name, attribute_name, new_value):
        raise NotImplementedError

    @abstractmethod
    def update_element_by_path(self, path, attribute_name, new_value):
        raise NotImplementedError

    @abstractmethod
    def remove_element_by_id(self, id):
        raise NotImplementedError

    @abstractmethod
    def remove_element_by_name(self, name):
        raise NotImplementedError

    @abstractmethod
    def remove_element_by_path(self, path):
        raise NotImplementedError

    @abstractmethod
    def add_child_by_parent_id(self, id, child_node):
        raise NotImplementedError

    @abstractmethod
    def add_child_by_parent_name(self, name, child_node):
        raise NotImplementedError

    @abstractmethod
    def add_child_by_parent_path(self, path, child_node):
        raise NotImplementedError

    @abstractmethod
    def remove_all_child_nodes_by_parent_id(self, id):
        raise NotImplementedError

    @abstractmethod
    def remove_all_child_nodes_by_parent_name(self, name):
        raise NotImplementedError

    @abstractmethod
    def remove_all_child_nodes_by_parent_path(self, path):
        raise NotImplementedError


