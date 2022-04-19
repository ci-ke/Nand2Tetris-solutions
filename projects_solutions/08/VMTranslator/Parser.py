import os
from .common import *


class Parser:
    __command_name_type = {
        'add': COMMAND_TYPE.C_ARITHMETIC,
        'sub': COMMAND_TYPE.C_ARITHMETIC,
        'neg': COMMAND_TYPE.C_ARITHMETIC,
        'eq': COMMAND_TYPE.C_ARITHMETIC,
        'gt': COMMAND_TYPE.C_ARITHMETIC,
        'lt': COMMAND_TYPE.C_ARITHMETIC,
        'and': COMMAND_TYPE.C_ARITHMETIC,
        'or': COMMAND_TYPE.C_ARITHMETIC,
        'not': COMMAND_TYPE.C_ARITHMETIC,
        'push': COMMAND_TYPE.C_PUSH,  # push segment index (2)
        'pop': COMMAND_TYPE.C_POP,  # pop segment index (2)
        'label': COMMAND_TYPE.C_LABEL,  # label symbol
        'goto': COMMAND_TYPE.C_GOTO,  # goto symbol
        'if-goto': COMMAND_TYPE.C_IF,  # if-goto symbol
        'function': COMMAND_TYPE.C_FUNCTION,  # function funName nLocals (2)
        'call': COMMAND_TYPE.C_CALL,  # call funName nArgs (2)
        'return': COMMAND_TYPE.C_RETURN,
    }

    def __init__(self, pathname: str) -> None:
        self.__pathname = pathname
        self.__filename_root = os.path.splitext(os.path.basename(pathname))[0]
        self.__file_lines = []
        self.__line_no = []

        self.__current_command = []
        self.__next_index = 0

        if not os.path.isfile(pathname):
            raise CompileError(f'No such file: {pathname}')

        with open(pathname, 'r') as f:
            for number, line in enumerate(f):
                if (index := line.find('//')) != -1:
                    line = line[:index]
                line = line.strip()
                line_list = line.split()
                if len(line_list) != 0:
                    self.__file_lines.append(line_list)
                    self.__line_no.append(number + 1)

    def has_more_commands(self) -> bool:
        return self.__next_index < len(self.__file_lines)

    def advance(self) -> None:
        if self.has_more_commands():
            self.__current_command = self.__file_lines[self.__next_index]
            self.__next_index += 1
            if len(self.__current_command) > 3:
                self.wrong_msg('Bad command, too many args')

    def command_type(self) -> COMMAND_TYPE:
        if self.__current_command[0] not in self.__command_name_type:
            self.wrong_msg('Bad command name')
        else:
            return self.__command_name_type[self.__current_command[0]]

    def arg1(self) -> str:
        assert self.command_type() != COMMAND_TYPE.C_RETURN

        if self.command_type() == COMMAND_TYPE.C_ARITHMETIC:
            return self.__current_command[0]
        else:
            return self.__current_command[1]

    def arg2(self) -> int:
        assert self.command_type() in {
            COMMAND_TYPE.C_PUSH,
            COMMAND_TYPE.C_POP,
            COMMAND_TYPE.C_FUNCTION,
            COMMAND_TYPE.C_CALL,
        }

        try:
            return int(self.__current_command[2])
        except ValueError:
            self.wrong_msg('Bad command arg2')

    def wrong_msg(self, msg: str):
        raise CompileError(
            f'{self.__pathname}, line {self.__line_no[self.__next_index-1]}: {msg}'
        )

    def module_name(self) -> str:
        return self.__filename_root
