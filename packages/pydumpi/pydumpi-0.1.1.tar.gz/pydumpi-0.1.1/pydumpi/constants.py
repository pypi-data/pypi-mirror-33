from enum import IntEnum


class DataType(IntEnum):
    ERROR = 0
    NULL = 1
    CHAR = 2
    SIGNED_CHAR = 3
    UNSIGNED_CHAR = 4
    BYTE = 5
    WCHAR = 6
    SHORT = 7
    UNSIGNED_SHORT = 8
    INT = 9
    UNSIGNED = 10
    LONG = 11
    UNSIGNED_LONG = 12
    FLOAT = 13
    DOUBLE = 14
    LONG_DOUBLE = 15
    LONG_LONG_INT = 16
    UNSIGNED_LONG_LONG = 17
    LONG_LONG = 18
    PACKED = 19
    LB = 20
    UB = 21
    FLOAT_INT = 22
    DOUBLE_INT = 23
    LONG_INT = 24
    SHORT_INT = 25
    TWO_INT = 26
    LONG_DOUBLE_INT = 27
