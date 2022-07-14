import os
from typing import List

from .common import CompileError, COMMAND_TYPE, SymbolChecker
from .Parser import Parser
from . import Code
from .SymbolTable import SymbolTable


class Assembler:
    def __init__(self, pathname: str) -> None:
        self.__pathname = os.path.normpath(pathname)
        self.__hack_codes: List[str] = []
        self.__next_var_addr = 16
        self.__symboltable = SymbolTable()

    def __init(self) -> None:  # def separate function to catch CompileError in run()
        self.__parser = Parser(self.__pathname)

    def __first_pass(self) -> None:
        current_rom_addr = 0
        while self.__parser.has_more_commands():
            self.__parser.advance()
            if self.__parser.command_type() == COMMAND_TYPE.L_COMMAND:
                symbol = self.__parser.symbol()
                if self.__symboltable.contains(symbol):
                    self.__parser.wrong_msg('Redefined L_COMMAND symbol')
                self.__symboltable.add_entry(symbol, current_rom_addr)
            else:
                current_rom_addr += 1

    def __second_pass(self) -> None:
        self.__parser.reset()
        while self.__parser.has_more_commands():
            self.__parser.advance()
            if self.__parser.command_type() == COMMAND_TYPE.A_COMMAND:
                symbol = self.__parser.symbol()
                if SymbolChecker.legal_const(symbol):
                    code = f'{int(symbol):0>16b}'
                else:
                    if self.__symboltable.contains(symbol):
                        symbol_addr = self.__symboltable.get_address(symbol)
                        code = f'{int(symbol_addr):0>16b}'
                    else:
                        self.__symboltable.add_entry(symbol, self.__next_var_addr)
                        code = f'{int(self.__next_var_addr):0>16b}'
                        self.__next_var_addr += 1
                self.__hack_codes.append(code + '\n')
            elif self.__parser.command_type() == COMMAND_TYPE.C_COMMAND:
                code = (
                    '111'
                    + Code.comp(self.__parser.comp())
                    + Code.dest(self.__parser.dest())
                    + Code.jump(self.__parser.jump())
                )
                if len(code) != 16:
                    self.__parser.wrong_msg('Bad C_COMMAND')
                self.__hack_codes.append(code + '\n')

    def __output(self) -> None:
        hack_pathname = os.path.splitext(self.__pathname)[0] + '.hack'
        with open(hack_pathname, 'w', encoding='utf8') as f:
            f.writelines(self.__hack_codes)
        print(f'Output: {hack_pathname}')

    def run(self) -> None:
        try:
            self.__init()
            self.__first_pass()
            self.__second_pass()
            self.__output()
        except CompileError as e:
            print(e)
