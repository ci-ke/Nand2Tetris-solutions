import os
from .common import *
from .JackTokenizer import JackTokenizer
from .CompilationEngine import CompilationEngine


class JackAnalyzer:
    def __init__(self, pathname: str) -> None:
        self.__pathname = os.path.normpath(pathname)

    def __init(self) -> None:
        if os.path.isdir(self.__pathname):
            self.__is_dirpath = True
        elif os.path.isfile(self.__pathname):
            self.__is_dirpath = False
        else:
            raise CompileError(f'No such file: {self.__pathname}')

        if not self.__is_dirpath:
            self.__output_dirpath = os.path.join(
                os.path.dirname(self.__pathname), 'output'
            )
            self.__tokenizer = [JackTokenizer(self.__pathname)]
        else:
            self.__output_dirpath = os.path.join(self.__pathname, 'output')
            self.__tokenizer = []
            dirfiles = os.listdir(self.__pathname)
            for filename in dirfiles:
                if os.path.splitext(filename)[1] == '.jack':
                    self.__tokenizer.append(
                        JackTokenizer(os.path.join(self.__pathname, filename))
                    )
            if len(self.__tokenizer) == 0:
                raise CompileError(f'No jack file in {self.__pathname}')

        if not os.path.isdir(self.__output_dirpath):
            os.mkdir(self.__output_dirpath)

    def __xmlT_pathname(self, tokenizer: JackTokenizer) -> str:
        return os.path.join(self.__output_dirpath, tokenizer.xmlT_filename())

    def __xml_pathname(self, tokenizer: JackTokenizer) -> str:
        return os.path.join(self.__output_dirpath, tokenizer.xml_filename())

    def __process_T(self, tokenizer: JackTokenizer) -> None:
        output_list = []
        output_list.append('<tokens>\n')
        while tokenizer.has_more_tokens():
            tokenizer.advance()
            token_type = tokenizer.token_type()

            if token_type == TOKEN_TYPE.KEYWORD:
                output_list.append('<keyword> ' + tokenizer.keyword() + ' </keyword>\n')
            elif token_type == TOKEN_TYPE.SYMBOL:
                current_token = tokenizer.symbol()
                if current_token == '<':
                    current_token = '&lt;'
                elif current_token == '>':
                    current_token = '&gt;'
                elif current_token == '&':
                    current_token = '&amp;'
                output_list.append('<symbol> ' + current_token + ' </symbol>\n')
            elif token_type == TOKEN_TYPE.IDENTIFIER:
                output_list.append(
                    '<identifier> ' + tokenizer.identifier() + ' </identifier>\n'
                )
            elif token_type == TOKEN_TYPE.INT_CONST:
                output_list.append(
                    '<integerConstant> '
                    + str(tokenizer.int_val())
                    + ' </integerConstant>\n'
                )
            elif token_type == TOKEN_TYPE.STRING_CONST:
                output_list.append(
                    '<stringConstant> '
                    + tokenizer.string_val()
                    + ' </stringConstant>\n'
                )

        output_list.append('</tokens>\n')

        with open(self.__xmlT_pathname(tokenizer), 'w') as f:
            f.writelines(output_list)
        print(f'Output: {self.__xmlT_pathname(tokenizer)}')

    def __process(self, tokenizer: JackTokenizer) -> None:
        output_list = []
        CompilationEngine(tokenizer, output_list)

        with open(self.__xml_pathname(tokenizer), 'w') as f:
            f.writelines(output_list)
        print(f'Output: {self.__xml_pathname(tokenizer)}')

    def run(self) -> None:
        try:
            self.__init()
            for tokenizer in self.__tokenizer:
                self.__process_T(tokenizer)
                tokenizer.reset()
                self.__process(tokenizer)
        except CompileError as e:
            print(e)
