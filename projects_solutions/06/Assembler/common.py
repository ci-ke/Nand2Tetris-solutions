from enum import Enum


class CompileError(Exception):
    pass


class COMMAND_TYPE(Enum):
    A_COMMAND = 1
    C_COMMAND = 2
    L_COMMAND = 3


class SymbolChecker:
    __available_symbols = (
        {str(i) for i in range(10)}
        | {chr(i) for i in range(ord('a'), ord('z') + 1)}
        | {chr(i) for i in range(ord('A'), ord('Z') + 1)}
        | {'_', '.', '$', ':'}
    )

    __number_symbols = {str(i) for i in range(10)}

    @staticmethod
    def legal_symbol(symbol: str) -> bool:
        if len(symbol) == 0:
            return False
        if symbol[0] in SymbolChecker.__number_symbols:
            return False
        for c in symbol:
            if c not in SymbolChecker.__available_symbols:
                return False
        return True

    @staticmethod
    def legal_const(symbol: str) -> bool:
        if len(symbol) == 0:
            return False
        for c in symbol:
            if c not in SymbolChecker.__number_symbols:
                return False
        return True
