from abc import ABCMeta, abstractmethod


class IManualTracing:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_selection_trace(self, element):
        raise NotImplementedError

    @abstractmethod
    def get_insertion_trace(self, element):
        raise NotImplementedError
