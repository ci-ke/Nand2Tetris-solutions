from .common import *

class SymbolTable:
    def __init__(self) -> None:
        self.__class_scope = {}
        self.__method_scope = {}
        self.__index = {
            SCOPE_TYPE.STATIC: 0,
            SCOPE_TYPE.FIELD: 0,
            SCOPE_TYPE.ARG: 0,
            SCOPE_TYPE.VAR: 0,
        }

    def start_subroutine(self) -> None:
        self.__method_scope.clear()
        self.__index[SCOPE_TYPE.ARG] = 0
        self.__index[SCOPE_TYPE.VAR] = 0

    def define(self, name: str, type_: str, kind: SCOPE_TYPE) -> None:
        if kind in {SCOPE_TYPE.STATIC, SCOPE_TYPE.FIELD}:
            self.__class_scope[name] = (type_, kind, self.__index[kind])
        elif kind in {SCOPE_TYPE.ARG, SCOPE_TYPE.VAR}:
            self.__method_scope[name] = (type_, kind, self.__index[kind])
        else:
            assert False
        self.__index[kind] += 1

    def var_count(self, kind: SCOPE_TYPE) -> int:
        if kind in {SCOPE_TYPE.STATIC, SCOPE_TYPE.FIELD}:
            count = 0
            for line in self.__class_scope.values():
                if line[1] == kind:
                    count += 1
            return count
        elif kind in {SCOPE_TYPE.ARG, SCOPE_TYPE.VAR}:
            count = 0
            for line in self.__method_scope.values():
                if line[1] == kind:
                    count += 1
            return count
        else:
            assert False

    def kind_of(self, name: str) -> SCOPE_TYPE:
        line = self.__class_scope.get(name, None)
        if line is None:
            line = self.__method_scope.get(name, None)
        if line is None:
            return SCOPE_TYPE.NONE
        return line[1]

    def type_of(self, name: str) -> str:
        line = self.__class_scope.get(name, None)
        if line is None:
            line = self.__method_scope.get(name, None)
        if line is None:
            return ''
        return line[0]

    def index_of(self, name: str) -> int:
        line = self.__class_scope.get(name, None)
        if line is None:
            line = self.__method_scope.get(name, None)
        if line is None:
            return -1
        return line[2]

    def is_defined(self, name: str) -> bool:
        return name in self.__class_scope or name in self.__method_scope
