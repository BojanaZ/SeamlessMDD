from enum import Enum


class OperationType(Enum):

    UNKNOWN = 0
    ADD = 1
    CHANGE = 2
    REMOVE = 3
    ADD_PROPERTY = 4
    CHANGE_PROPERTY = 5
    REMOVE_PROPERTY = 6
