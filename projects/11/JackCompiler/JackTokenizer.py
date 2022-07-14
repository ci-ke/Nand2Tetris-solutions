import os
from typing import NoReturn, Tuple

from .common import CompileError, TOKEN_TYPE, IdentifierChecker


class JackTokenizer:
    __keywords = {
        'class',
        'constructor',
        'function',
        'method',
        'field',
        'static',
        'var',
        'int',
        'char',
        'boolean',
        'void',
        'true',
        'false',
        'null',
        'this',
        'let',
        'do',
        'if',
        'else',
        'while',
        'return',
    }
    __symbols = {
        '{',
        '}',
        '(',
        ')',
        '[',
        ']',
        '.',
        ',',
        ';',
        '+',
        '-',
        '*',
        '/',
        '&',
        '|',
        '<',
        '>',
        '=',
        '~',
    }

    def __init__(self, pathname: str) -> None:
        self.__pathname = pathname
        self.__filename_root = os.path.splitext(os.path.basename(pathname))[0]

        self.__current_token = ''
        self.__next_index = 0
        self.__current_token_line = 0
        self.__next_token_line = 1

        with open(pathname, 'r', encoding='utf8') as f:
            self.__source = f.read().replace('\t', ' ')

    def has_more_tokens(self) -> bool:
        while True:
            if self.__next_index >= len(self.__source):
                return False

            if self.__source[self.__next_index] == ' ':
                self.__next_index += 1
            elif self.__source[self.__next_index] == '\n':
                self.__next_index += 1
                self.__next_token_line += 1
            elif (
                self.__source[self.__next_index : self.__next_index + 2] == '//'
            ):  # python slice won't raise IndexError
                while (
                    self.__next_index < len(self.__source)
                    and self.__source[self.__next_index] != '\n'
                ):
                    self.__next_index += 1
            elif self.__source[self.__next_index : self.__next_index + 2] == '/*':
                self.__next_index += 2
                while (
                    self.__next_index < len(self.__source)
                    and self.__source[self.__next_index : self.__next_index + 2] != '*/'
                ):
                    if self.__source[self.__next_index] == '\n':
                        self.__next_token_line += 1
                    self.__next_index += 1
                self.__next_index += 2
            else:
                break

        return True

    def advance(self) -> None:
        self.__current_token_line = self.__next_token_line
        start_index = self.__next_index

        if IdentifierChecker.legal_char(self.__source[self.__next_index]):
            while IdentifierChecker.legal_char(self.__source[self.__next_index]):
                self.__next_index += 1
                if self.__next_index >= len(self.__source):
                    break
        elif self.__source[self.__next_index] in JackTokenizer.__symbols:
            self.__next_index += 1
        elif self.__source[self.__next_index] == '"':
            self.__next_index += 1
            if self.__next_index >= len(self.__source):
                self.wrong_msg('Bad string const')

            while self.__source[self.__next_index] != '"':
                if self.__source[self.__next_index] == '\n':
                    self.wrong_msg('Not allow newline in string const')

                self.__next_index += 1
                if self.__next_index >= len(self.__source):
                    self.wrong_msg('Bad string const')

            self.__next_index += 1
        else:
            self.wrong_msg('Unknown character')

        self.__current_token = self.__source[start_index : self.__next_index]

    def look_ahead(self) -> Tuple[str, TOKEN_TYPE]:
        backup = (
            self.__current_token,
            self.__next_index,
            self.__current_token_line,
            self.__next_token_line,
        )

        if not self.has_more_tokens():
            self.wrong_msg('Encounter source ending when looking ahead')
        self.advance()

        ret_type = self.token_type()
        ret_token = self.__current_token
        if ret_type == TOKEN_TYPE.STRING_CONST:
            ret_token = ret_token[1:-1]

        (
            self.__current_token,
            self.__next_index,
            self.__current_token_line,
            self.__next_token_line,
        ) = backup

        return ret_token, ret_type

    def token_type(self) -> TOKEN_TYPE:
        if self.__current_token in JackTokenizer.__keywords:
            return TOKEN_TYPE.KEYWORD
        elif self.__current_token in JackTokenizer.__symbols:
            return TOKEN_TYPE.SYMBOL
        elif IdentifierChecker.legal_identifier(self.__current_token):
            return TOKEN_TYPE.IDENTIFIER
        elif IdentifierChecker.legal_int(self.__current_token):
            return TOKEN_TYPE.INT_CONST
        elif self.__current_token[0] == '"' and self.__current_token[-1] == '"':
            return TOKEN_TYPE.STRING_CONST
        else:
            self.wrong_msg(f'Illegal identifier "{self.__current_token}"')

    def keyword(self) -> str:
        assert self.token_type() == TOKEN_TYPE.KEYWORD

        return self.__current_token

    def symbol(self) -> str:
        assert self.token_type() == TOKEN_TYPE.SYMBOL

        return self.__current_token

    def identifier(self) -> str:
        assert self.token_type() == TOKEN_TYPE.IDENTIFIER

        return self.__current_token

    def int_val(self) -> int:
        assert self.token_type() == TOKEN_TYPE.INT_CONST

        return int(self.__current_token)

    def string_val(self) -> str:
        assert self.token_type() == TOKEN_TYPE.STRING_CONST

        return self.__current_token[1:-1]

    def vm_pathname(self) -> str:
        return os.path.splitext(self.__pathname)[0] + '.vm'

    def module_name(self) -> str:
        return self.__filename_root

    def wrong_msg(self, msg: str) -> NoReturn:
        raise CompileError(
            f'{self.__pathname}, line {self.__current_token_line}: {msg}'
        )
