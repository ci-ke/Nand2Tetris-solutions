import os
from typing import List, Set

from .common import CompileError, COMMAND_TYPE
from .Parser import Parser
from .CodeWriter import CodeWriter


class VMTranslator:
    def __init__(self, pathname: str) -> None:
        self.__pathname = os.path.normpath(pathname)
        self.__declared_function: Set[str] = set()
        self.__parsers: List[Parser] = []

    def __init(self) -> None:
        if os.path.isdir(self.__pathname):
            self.__is_dirpath = True
        elif os.path.isfile(self.__pathname):
            self.__is_dirpath = False
        else:
            raise CompileError(f'No such file: {self.__pathname}')

        if not self.__is_dirpath:
            self.__parsers.append(Parser(self.__pathname))
            asm_pathname = os.path.splitext(self.__pathname)[0] + '.asm'
        else:
            dirfiles = os.listdir(self.__pathname)
            for filename in dirfiles:
                if os.path.splitext(filename)[1] == '.vm':
                    self.__parsers.append(
                        Parser(os.path.join(self.__pathname, filename))
                    )
            asm_pathname = os.path.join(
                self.__pathname, os.path.basename(self.__pathname) + '.asm'
            )

            if len(self.__parsers) == 0:
                raise CompileError(f'No vm file in {self.__pathname}')

        self.__codewriter = CodeWriter(asm_pathname)

    def __process(self, parser: Parser) -> None:
        self.__codewriter.set_file_name(parser.module_name())
        in_function = ''
        while parser.has_more_commands():
            parser.advance()
            if parser.command_type() == COMMAND_TYPE.C_ARITHMETIC:
                self.__codewriter.write_arithmetic(parser.arg1())
            elif parser.command_type() in {COMMAND_TYPE.C_PUSH, COMMAND_TYPE.C_POP}:
                if not self.__codewriter.write_push_pop(
                    parser.command_type(), parser.arg1(), parser.arg2()
                ):
                    parser.wrong_msg('Bad push/pop command')
            elif parser.command_type() == COMMAND_TYPE.C_LABEL:
                if not self.__codewriter.write_label(parser.arg1(), in_function):
                    parser.wrong_msg('Bad label command')
            elif parser.command_type() == COMMAND_TYPE.C_GOTO:
                if not self.__codewriter.write_goto(parser.arg1(), in_function):
                    parser.wrong_msg('Bad goto command')
            elif parser.command_type() == COMMAND_TYPE.C_IF:
                if not self.__codewriter.write_if(parser.arg1(), in_function):
                    parser.wrong_msg('Bad if-goto command')
            elif parser.command_type() == COMMAND_TYPE.C_FUNCTION:
                function_name = parser.arg1()
                if function_name in self.__declared_function:
                    parser.wrong_msg('Redefined function')
                if not self.__codewriter.write_function(function_name, parser.arg2()):
                    parser.wrong_msg('Bad function command')
                self.__declared_function.add(function_name)
                in_function = function_name
            elif parser.command_type() == COMMAND_TYPE.C_CALL:
                if not self.__codewriter.write_call(parser.arg1(), parser.arg2()):
                    parser.wrong_msg('Bad call command')
            elif parser.command_type() == COMMAND_TYPE.C_RETURN:
                self.__codewriter.write_return()

    def run(self) -> None:
        try:
            self.__init()
            if self.__is_dirpath:
                self.__codewriter.write_init()
            for parser in self.__parsers:
                self.__process(parser)
            self.__codewriter.close()
        except CompileError as e:
            print(e)
