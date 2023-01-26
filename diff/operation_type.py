from enum import Enum


class OperationType(Enum):

    UNKNOWN = 0
    ADD = 1
    CHANGE = 2
    REMOVE = 3
    SUBELEMENT_ADD = 4
    SUBELEMENT_REMOVE = 5
    SUBELEMENT_CHANGE = 6
    #ADD_PROPERTY = 7
    #CHANGE_PROPERTY = 8
    #REMOVE_PROPERTY = 9
