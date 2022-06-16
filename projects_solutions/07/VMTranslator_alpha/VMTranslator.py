import os

from .common import *
from .Parser import Parser
from .CodeWriter import CodeWriter


class VMTranslator:
    def __init__(self, pathname: str) -> None:
        self.__pathname = os.path.normpath(pathname)
        asm_pathname = os.path.splitext(self.__pathname)[0] + '.asm'
        self.__codewriter = CodeWriter(asm_pathname)

    def __init(self) -> None:
        self.__parser = Parser(self.__pathname)

    def __process(self, parser: Parser) -> None:
        self.__codewriter.set_file_name(parser.module_name())
        while parser.has_more_commands():
            parser.advance()
            if parser.command_type() == COMMAND_TYPE.C_ARITHMETIC:
                self.__codewriter.write_arithmetic(parser.arg1())
            elif parser.command_type() in {COMMAND_TYPE.C_PUSH, COMMAND_TYPE.C_POP}:
                if not self.__codewriter.write_push_pop(
                    parser.command_type(), parser.arg1(), parser.arg2()
                ):
                    parser.wrong_msg('Bad push/pop command')
            else:
                parser.wrong_msg('Unsupported command, under developing')

    def run(self) -> None:
        try:
            self.__init()
            self.__process(self.__parser)
            self.__codewriter.close()
        except CompileError as e:
            print(e)
