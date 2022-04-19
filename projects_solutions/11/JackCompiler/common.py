from enum import Enum


class CompileError(Exception):
    pass


class TOKEN_TYPE(Enum):
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5


class SCOPE_TYPE(Enum):
    STATIC = 1
    FIELD = 2
    ARG = 3
    VAR = 4
    NONE = 5


class IdentifierChecker:
    __available_chars = (
        {str(i) for i in range(10)}
        | {chr(i) for i in range(ord('a'), ord('z') + 1)}
        | {chr(i) for i in range(ord('A'), ord('Z') + 1)}
        | {'_'}
    )

    __number_chars = {str(i) for i in range(10)}

    @staticmethod
    def legal_identifier(token: str) -> bool:
        if len(token) == 0:
            return False
        if token[0] in IdentifierChecker.__number_chars:
            return False
        for c in token:
            if c not in IdentifierChecker.__available_chars:
                return False
        return True

    @staticmethod
    def legal_int(token: str) -> bool:
        if len(token) == 0:
            return False
        for c in token:
            if c not in IdentifierChecker.__number_chars:
                return False
        return True

    @staticmethod
    def legal_char(c: str) -> bool:
        return c in IdentifierChecker.__available_chars
