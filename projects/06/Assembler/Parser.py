import os
from .common import *


class Parser:
    def __init__(self, pathname: str) -> None:
        self.__pathname = pathname
        self.__file_lines = []
        self.__line_no = []

        self.__current_command = ''
        self.__next_index = 0

        if not os.path.isfile(pathname):
            raise CompileError(f'No such file: {pathname}')

        with open(pathname, 'r') as f:
            for number, line in enumerate(f):
                if (index := line.find('//')) != -1:
                    line = line[:index]
                line = line.strip()
                line = line.replace(' ', '').replace('\t', '')
                if len(line) != 0:
                    self.__file_lines.append(line)
                    self.__line_no.append(number + 1)

    def reset(self) -> None:
        self.__current_command = ''
        self.__next_index = 0

    def has_more_commands(self) -> bool:
        return self.__next_index < len(self.__file_lines)

    def advance(self) -> None:
        if self.has_more_commands():
            self.__current_command = self.__file_lines[self.__next_index]
            self.__next_index += 1

    def command_type(self) -> COMMAND_TYPE:
        if self.__current_command[0] == '@':
            return COMMAND_TYPE.A_COMMAND
        elif self.__current_command[0] == '(' and self.__current_command[-1] == ')':
            return COMMAND_TYPE.L_COMMAND
        else:
            return COMMAND_TYPE.C_COMMAND

    def symbol(self) -> str:
        assert self.command_type() in {COMMAND_TYPE.L_COMMAND, COMMAND_TYPE.A_COMMAND}

        if self.command_type() == COMMAND_TYPE.L_COMMAND:
            symbol = self.__current_command[1:-1]
            if not SymbolChecker.legal_symbol(symbol):
                self.wrong_msg('Bad L_COMMAND symbol')
            return symbol
        elif self.command_type() == COMMAND_TYPE.A_COMMAND:
            symbol = self.__current_command[1:]
            if not SymbolChecker.legal_symbol(symbol) and not SymbolChecker.legal_const(
                symbol
            ):
                self.wrong_msg('Bad A_COMMAND symbol')
            return symbol

    def dest(self) -> str:
        assert self.command_type() == COMMAND_TYPE.C_COMMAND

        if (index := self.__current_command.find('=')) != -1:
            return self.__current_command[:index]
        else:
            return ''

    def comp(self) -> str:
        assert self.command_type() == COMMAND_TYPE.C_COMMAND

        index1 = self.__current_command.find('=')
        index2 = self.__current_command.find(';')
        index1 = index1 + 1 if index1 != -1 else None
        index2 = index2 if index2 != -1 else None
        return self.__current_command[index1:index2]

    def jump(self) -> str:
        assert self.command_type() == COMMAND_TYPE.C_COMMAND

        if (index := self.__current_command.find(';')) != -1:
            return self.__current_command[index + 1 :]
        else:
            return ''

    def wrong_msg(self, msg: str):
        raise CompileError(
            f'{self.__pathname}, line {self.__line_no[self.__next_index-1]}: {msg}'
        )
