from enum import Enum


class Type(Enum):
    """
    Enum representing the possible types that AML supports
    """
    STRING = 1
    INTEGER = 2
    DECIMAL = 3
    BOOLEAN = 4
    DATE = 5
    TIME = 9
    ARRAY = 6
    STRUCT = 7
    HASH = 8
