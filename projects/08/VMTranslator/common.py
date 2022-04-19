from enum import Enum


class CompileError(Exception):
    pass


class COMMAND_TYPE(Enum):
    C_ARITHMETIC = 1
    C_PUSH = 2
    C_POP = 3
    C_LABEL = 4
    C_GOTO = 5
    C_IF = 6
    C_FUNCTION = 7
    C_RETURN = 8
    C_CALL = 9


class SymbolChecker:
    __available_symbols = (
        {str(i) for i in range(10)}
        | {chr(i) for i in range(ord('a'), ord('z') + 1)}
        | {chr(i) for i in range(ord('A'), ord('Z') + 1)}
        | {'_', '.', ':'}
    )  # asm can use '$', not vm

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
