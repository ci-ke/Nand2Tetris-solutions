import os
from typing import List

from .common import CompileError
from .JackTokenizer import JackTokenizer
from .CompilationEngine import CompilationEngine


class JackCompiler:
    def __init__(self, pathname: str) -> None:
        self.__pathname = os.path.normpath(pathname)
        self.__tokenizer: List[JackTokenizer] = []

    def __init(self) -> None:
        if os.path.isdir(self.__pathname):
            is_dirpath = True
        elif os.path.isfile(self.__pathname):
            is_dirpath = False
        else:
            raise CompileError(f'No such file: {self.__pathname}')

        if not is_dirpath:
            self.__tokenizer.append(JackTokenizer(self.__pathname))
        else:
            dirfiles = os.listdir(self.__pathname)
            for filename in dirfiles:
                if os.path.splitext(filename)[1] == '.jack':
                    self.__tokenizer.append(
                        JackTokenizer(os.path.join(self.__pathname, filename))
                    )
            if len(self.__tokenizer) == 0:
                raise CompileError(f'No jack file in {self.__pathname}')

    def __process(self, tokenizer: JackTokenizer) -> None:
        output_list: List[str] = []
        CompilationEngine(tokenizer, output_list)

        with open(tokenizer.vm_pathname(), 'w', encoding='utf8') as f:
            f.writelines(output_list)
        print(f'Output: {tokenizer.vm_pathname()}')

    def run(self) -> None:
        try:
            self.__init()
            for tokenizer in self.__tokenizer:
                self.__process(tokenizer)
        except CompileError as e:
            print(e)
