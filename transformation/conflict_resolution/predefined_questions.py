from enum import Enum


class PredefinedQuestion(Enum):
    # When we add element, it may already exist
    ALREADY_EXISTS = 0,

    # Before deletion or update, element may not exist
    DOES_NOT_EXIST = 1,

    # Element may have been altered between two generation cycles
    IS_ALTERED = 2,
