from typing import List, Optional

from .common import *
from .JackTokenizer import JackTokenizer


class CompilationEngine:
    __func = {
        TOKEN_TYPE.KEYWORD: JackTokenizer.keyword,
        TOKEN_TYPE.SYMBOL: JackTokenizer.symbol,
        TOKEN_TYPE.IDENTIFIER: JackTokenizer.identifier,
        TOKEN_TYPE.INT_CONST: JackTokenizer.int_val,
        TOKEN_TYPE.STRING_CONST: JackTokenizer.string_val,
    }

    def __init__(self, tokenizer: JackTokenizer, output_list: List[str]) -> None:
        self.__xml_indent = 0
        self.__tokenizer = tokenizer
        self.__output_list = output_list

        self.__get_token()
        self.compile_class()

    def __expect_token(
        self, token_type: TOKEN_TYPE, target: Optional[str] = None
    ) -> None:
        if target is None:
            if self.__tokenizer.token_type() == token_type:
                return
            else:
                self.__tokenizer.wrong_msg(f'Expecting a {token_type.name}')
        else:
            if (
                self.__tokenizer.token_type() == token_type
                and self.__func[token_type](self.__tokenizer) == target
            ):
                return
            else:
                self.__tokenizer.wrong_msg(f'Expecting {target}')

    def __get_token(
        self, token_type: Optional[TOKEN_TYPE] = None, target: Optional[str] = None
    ) -> None:
        if token_type is None:
            if not self.__tokenizer.has_more_tokens():
                self.__tokenizer.wrong_msg(
                    'Encounter source ending when expecting a token'
                )
            self.__tokenizer.advance()
        else:
            if target is None:
                if not self.__tokenizer.has_more_tokens():
                    self.__tokenizer.wrong_msg(
                        f'Encounter source ending when expecting a {token_type.name}'
                    )
                self.__tokenizer.advance()
                self.__expect_token(token_type)
            else:
                if not self.__tokenizer.has_more_tokens():
                    self.__tokenizer.wrong_msg(
                        f'Encounter source ending when expecting {target}'
                    )
                self.__tokenizer.advance()
                self.__expect_token(token_type, target)

    def __write_output(self, label: str, content: Optional[str] = None) -> None:
        if content is None:
            self.__output_list.append(' ' * self.__xml_indent + f'<{label}>\n')
        else:
            assert label in {
                'keyword',
                'symbol',
                'identifier',
                'integerConstant',
                'stringConstant',
            }

            self.__output_list.append(
                ' ' * self.__xml_indent + f'<{label}> {content} </{label}>\n'
            )

    # compile系列函数进入时current_token为语法中第一个元素，
    # 执行完毕后current_token为语法结尾的后一个元素（除compile_class）
    def compile_class(self) -> None:
        self.__write_output('class')
        self.__xml_indent += 2

        # 'class'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'class')
        self.__write_output('keyword', 'class')

        # className
        self.__get_token(TOKEN_TYPE.IDENTIFIER)
        class_name = self.__tokenizer.identifier()
        if class_name != self.__tokenizer.module_name():
            self.__tokenizer.wrong_msg('Different class and file name')
        self.__write_output('identifier', class_name)

        # '{'
        self.__get_token(TOKEN_TYPE.SYMBOL, '{')
        self.__write_output('symbol', '{')

        # classVarDec*
        self.__get_token()
        while (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() in {'static', 'field'}
        ):
            self.compile_class_var_dec()

        # subroutineDec*
        while (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword()
            in {
                'constructor',
                'function',
                'method',
            }
        ):
            self.compile_subroutine()

        # '}'
        self.__expect_token(TOKEN_TYPE.SYMBOL, '}')
        self.__write_output('symbol', '}')

        # end
        if self.__tokenizer.has_more_tokens():
            self.__tokenizer.wrong_msg('Encounter token out of class')

        self.__xml_indent -= 2
        self.__write_output('/class')

    def compile_class_var_dec(self) -> None:
        self.__write_output('classVarDec')
        self.__xml_indent += 2

        # 'static' | 'field'
        self.__expect_token(TOKEN_TYPE.KEYWORD)
        self.__write_output('keyword', self.__tokenizer.keyword())

        # type
        self.__get_token()
        if (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() in {'int', 'char', 'boolean'}
        ):
            self.__write_output('keyword', self.__tokenizer.keyword())
        elif self.__tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
            self.__write_output('identifier', self.__tokenizer.identifier())
        else:
            self.__tokenizer.wrong_msg('Bad type in classVarDec')

        while True:
            # varName
            self.__get_token(TOKEN_TYPE.IDENTIFIER)
            self.__write_output('identifier', self.__tokenizer.identifier())

            # (',' varName)* or ;
            self.__get_token(TOKEN_TYPE.SYMBOL)
            if self.__tokenizer.symbol() == ',':
                # ','
                self.__write_output('symbol', ',')
            else:
                break

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')
        self.__write_output('symbol', ';')

        # end
        self.__get_token()

        self.__xml_indent -= 2
        self.__write_output('/classVarDec')

    def compile_subroutine(self) -> None:
        self.__write_output('subroutineDec')
        self.__xml_indent += 2

        # 'constructor' | 'function' | 'method'
        self.__expect_token(TOKEN_TYPE.KEYWORD)
        self.__write_output('keyword', self.__tokenizer.keyword())

        # 'void' | type
        self.__get_token()
        if (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() in {'int', 'char', 'boolean', 'void'}
        ):
            self.__write_output('keyword', self.__tokenizer.keyword())
        elif self.__tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
            self.__write_output('identifier', self.__tokenizer.identifier())
        else:
            self.__tokenizer.wrong_msg('Bad type in subroutineDec')

        # subRoutineName
        self.__get_token(TOKEN_TYPE.IDENTIFIER)
        self.__write_output('identifier', self.__tokenizer.identifier())

        # '('
        self.__get_token(TOKEN_TYPE.SYMBOL, '(')
        self.__write_output('symbol', '(')

        # parameterList
        self.__get_token()
        self.compile_parameter_list()

        # ')'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ')')
        self.__write_output('symbol', ')')

        # subRoutineBody start
        self.__write_output('subroutineBody')
        self.__xml_indent += 2

        # '{'
        self.__get_token(TOKEN_TYPE.SYMBOL, '{')
        self.__write_output('symbol', '{')

        # varDec*
        self.__get_token()
        while (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() == 'var'
        ):
            self.compile_var_dec()

        # statements
        self.compile_statements()

        # '}'
        self.__expect_token(TOKEN_TYPE.SYMBOL, '}')
        self.__write_output('symbol', '}')

        # subRoutineBody end
        self.__get_token()
        self.__xml_indent -= 2
        self.__write_output('/subroutineBody')

        self.__xml_indent -= 2
        self.__write_output('/subroutineDec')

    def compile_parameter_list(self) -> None:
        self.__write_output('parameterList')
        self.__xml_indent += 2

        if not (
            self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
            and self.__tokenizer.symbol() == ')'
        ):
            while True:
                # type
                if (
                    self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
                    and self.__tokenizer.keyword() in {'int', 'char', 'boolean'}
                ):
                    self.__write_output('keyword', self.__tokenizer.keyword())
                elif self.__tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
                    self.__write_output('identifier', self.__tokenizer.identifier())
                else:
                    self.__tokenizer.wrong_msg('Bad type in parameterList')

                # varName
                self.__get_token(TOKEN_TYPE.IDENTIFIER)
                self.__write_output('identifier', self.__tokenizer.identifier())

                # ',' or end
                self.__get_token()
                if (
                    self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
                    and self.__tokenizer.symbol() == ','
                ):
                    self.__write_output('symbol', ',')
                    self.__get_token()
                else:
                    break

        self.__xml_indent -= 2
        self.__write_output('/parameterList')

    def compile_var_dec(self) -> None:
        self.__write_output('varDec')
        self.__xml_indent += 2

        # 'var'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'var')
        self.__write_output('keyword', 'var')

        # type
        self.__get_token()
        if (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() in {'int', 'char', 'boolean'}
        ):
            self.__write_output('keyword', self.__tokenizer.keyword())
        elif self.__tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
            self.__write_output('identifier', self.__tokenizer.identifier())
        else:
            self.__tokenizer.wrong_msg('Bad type in varDec')

        while True:
            # varName
            self.__get_token(TOKEN_TYPE.IDENTIFIER)
            self.__write_output('identifier', self.__tokenizer.identifier())

            # (',' varName)* or ;
            self.__get_token(TOKEN_TYPE.SYMBOL)
            if self.__tokenizer.symbol() == ',':
                # ','
                self.__write_output('symbol', ',')
            else:
                break

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')
        self.__write_output('symbol', ';')

        # end
        self.__get_token()

        self.__xml_indent -= 2
        self.__write_output('/varDec')

    def compile_statements(self) -> None:
        self.__write_output('statements')
        self.__xml_indent += 2

        while (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() in {'let', 'if', 'while', 'do', 'return'}
        ):
            if self.__tokenizer.keyword() == 'let':
                self.compile_let()
            elif self.__tokenizer.keyword() == 'if':
                self.compile_if()
            elif self.__tokenizer.keyword() == 'while':
                self.compile_while()
            elif self.__tokenizer.keyword() == 'do':
                self.compile_do()
            elif self.__tokenizer.keyword() == 'return':
                self.compile_return()

        self.__xml_indent -= 2
        self.__write_output('/statements')

    def compile_do(self) -> None:
        self.__write_output('doStatement')
        self.__xml_indent += 2

        # 'do'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'do')
        self.__write_output('keyword', 'do')

        # subroutineCall
        self.__get_token()
        self.__compile_subroutine_call()

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')
        self.__write_output('symbol', ';')

        # end
        self.__get_token()

        self.__xml_indent -= 2
        self.__write_output('/doStatement')

    def __compile_subroutine_call(self) -> None:
        # subroutineName | className | varName
        self.__expect_token(TOKEN_TYPE.IDENTIFIER)
        self.__write_output('identifier', self.__tokenizer.identifier())

        # if '.' else '('
        self.__get_token(TOKEN_TYPE.SYMBOL)
        if self.__tokenizer.symbol() == '.':
            # '.'
            self.__write_output('symbol', '.')

            # subroutineName
            self.__get_token(TOKEN_TYPE.IDENTIFIER)
            self.__write_output('identifier', self.__tokenizer.identifier())

            self.__get_token()

        # '('
        self.__expect_token(TOKEN_TYPE.SYMBOL, '(')
        self.__write_output('symbol', '(')

        # expressionList
        self.__get_token()
        self.compile_expression_list()

        # ')'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ')')
        self.__write_output('symbol', ')')

        # end
        self.__get_token()

    def compile_let(self) -> None:
        self.__write_output('letStatement')
        self.__xml_indent += 2

        # 'let'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'let')
        self.__write_output('keyword', 'let')

        # varName
        self.__get_token(TOKEN_TYPE.IDENTIFIER)
        self.__write_output('identifier', self.__tokenizer.identifier())

        # if '[' else '='
        self.__get_token(TOKEN_TYPE.SYMBOL)
        if self.__tokenizer.symbol() == '[':
            # '['
            self.__write_output('symbol', '[')

            # expression
            self.__get_token()
            self.compile_expression()

            # ']'
            self.__expect_token(TOKEN_TYPE.SYMBOL, ']')
            self.__write_output('symbol', ']')

            self.__get_token()

        # '='
        self.__expect_token(TOKEN_TYPE.SYMBOL, '=')
        self.__write_output('symbol', '=')

        # expression
        self.__get_token()
        self.compile_expression()

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')
        self.__write_output('symbol', ';')

        # end
        self.__get_token()

        self.__xml_indent -= 2
        self.__write_output('/letStatement')

    def compile_while(self) -> None:
        self.__write_output('whileStatement')
        self.__xml_indent += 2

        # 'while'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'while')
        self.__write_output('keyword', 'while')

        # '('
        self.__get_token(TOKEN_TYPE.SYMBOL, '(')
        self.__write_output('symbol', '(')

        # expression
        self.__get_token()
        self.compile_expression()

        # ')'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ')')
        self.__write_output('symbol', ')')

        # '{'
        self.__get_token(TOKEN_TYPE.SYMBOL, '{')
        self.__write_output('symbol', '{')

        # statments
        self.__get_token()
        self.compile_statements()

        # '}'
        self.__expect_token(TOKEN_TYPE.SYMBOL, '}')
        self.__write_output('symbol', '}')

        # end
        self.__get_token()

        self.__xml_indent -= 2
        self.__write_output('/whileStatement')

    def compile_return(self) -> None:
        self.__write_output('returnStatement')
        self.__xml_indent += 2

        # 'return'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'return')
        self.__write_output('keyword', 'return')

        # if expression
        self.__get_token()
        if not (
            self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
            and self.__tokenizer.symbol() == ';'
        ):
            # expression
            self.compile_expression()

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')
        self.__write_output('symbol', ';')

        # end
        self.__get_token()

        self.__xml_indent -= 2
        self.__write_output('/returnStatement')

    def compile_if(self) -> None:
        self.__write_output('ifStatement')
        self.__xml_indent += 2

        # 'if'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'if')
        self.__write_output('keyword', 'if')

        # '('
        self.__get_token(TOKEN_TYPE.SYMBOL, '(')
        self.__write_output('symbol', '(')

        # expression
        self.__get_token()
        self.compile_expression()

        # ')'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ')')
        self.__write_output('symbol', ')')

        # '{'
        self.__get_token(TOKEN_TYPE.SYMBOL, '{')
        self.__write_output('symbol', '{')

        # statements
        self.__get_token()
        self.compile_statements()

        # '}'
        self.__expect_token(TOKEN_TYPE.SYMBOL, '}')
        self.__write_output('symbol', '}')

        # 'else' or end
        self.__get_token()
        if (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() == 'else'
        ):
            # 'else'
            self.__write_output('keyword', 'else')

            # '{'
            self.__get_token(TOKEN_TYPE.SYMBOL, '{')
            self.__write_output('symbol', '{')

            # statements
            self.__get_token()
            self.compile_statements()

            # '}'
            self.__expect_token(TOKEN_TYPE.SYMBOL, '}')
            self.__write_output('symbol', '}')

            # end
            self.__get_token()

        self.__xml_indent -= 2
        self.__write_output('/ifStatement')

    def compile_expression(self) -> None:
        self.__write_output('expression')
        self.__xml_indent += 2

        # term
        self.compile_term()

        # (op term)*
        while (
            self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
            and self.__tokenizer.symbol()
            in {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        ):
            # op
            current_token = self.__tokenizer.symbol()
            if current_token == '<':
                current_token = '&lt;'
            elif current_token == '>':
                current_token = '&gt;'
            elif current_token == '&':
                current_token = '&amp;'
            self.__write_output('symbol', current_token)
            # term
            self.__get_token()
            self.compile_term()

        self.__xml_indent -= 2
        self.__write_output('/expression')

    def compile_term(self) -> None:
        self.__write_output('term')
        self.__xml_indent += 2

        token_type = self.__tokenizer.token_type()

        # integerConstant
        if token_type == TOKEN_TYPE.INT_CONST:
            self.__write_output('integerConstant', str(self.__tokenizer.int_val()))
            # end
            self.__get_token()

        # stringConstant
        elif token_type == TOKEN_TYPE.STRING_CONST:
            self.__write_output('stringConstant', self.__tokenizer.string_val())
            # end
            self.__get_token()

        # keywordConstant
        elif token_type == TOKEN_TYPE.KEYWORD and self.__tokenizer.keyword() in {
            'true',
            'false',
            'null',
            'this',
        }:
            self.__write_output('keyword', self.__tokenizer.keyword())
            # end
            self.__get_token()

        # varName | varName '[' expression ']' | subroutineCall
        elif token_type == TOKEN_TYPE.IDENTIFIER:
            ahead, _ = self.__tokenizer.look_ahead()
            # varName '[' expression ']'
            if ahead == '[':
                # varName
                self.__write_output('identifier', self.__tokenizer.identifier())

                # '['
                self.__get_token(TOKEN_TYPE.SYMBOL, '[')
                self.__write_output('symbol', '[')

                # expression
                self.__get_token()
                self.compile_expression()

                # ']'
                self.__expect_token(TOKEN_TYPE.SYMBOL, ']')
                self.__write_output('symbol', ']')

                # end
                self.__get_token()

            # subroutineCall
            elif ahead in {'(', '.'}:
                self.__compile_subroutine_call()

            # varName
            else:
                self.__write_output('identifier', self.__tokenizer.identifier())
                # end
                self.__get_token()

        # '(' expression ')'
        elif token_type == TOKEN_TYPE.SYMBOL and self.__tokenizer.symbol() == '(':
            # '('
            self.__write_output('symbol', '(')
            # expression
            self.__get_token()
            self.compile_expression()
            # ')'
            self.__expect_token(TOKEN_TYPE.SYMBOL, ')')
            self.__write_output('symbol', ')')
            # end
            self.__get_token()

        # unaryOp
        elif token_type == TOKEN_TYPE.SYMBOL and self.__tokenizer.symbol() in {
            '-',
            '~',
        }:
            # '-' | '~'
            self.__write_output('symbol', self.__tokenizer.symbol())
            # term
            self.__get_token()
            self.compile_term()
        else:
            self.__tokenizer.wrong_msg('Bad term')

        self.__xml_indent -= 2
        self.__write_output('/term')

    def compile_expression_list(self) -> None:
        self.__write_output('expressionList')
        self.__xml_indent += 2

        if not (
            self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
            and self.__tokenizer.symbol() == ')'
        ):
            while True:
                # expression
                self.compile_expression()

                # ',' or end
                if (
                    self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
                    and self.__tokenizer.symbol() == ','
                ):
                    self.__write_output('symbol', ',')
                    self.__get_token()
                else:
                    break

        self.__xml_indent -= 2
        self.__write_output('/expressionList')
