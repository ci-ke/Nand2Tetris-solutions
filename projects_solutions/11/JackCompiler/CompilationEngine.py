from typing import List, Optional

from .common import TOKEN_TYPE, SCOPE_TYPE
from .JackTokenizer import JackTokenizer
from .SymbolTable import SymbolTable
from .VMWriter import VMWriter


class CompilationEngine:
    __func = {
        TOKEN_TYPE.KEYWORD: JackTokenizer.keyword,
        TOKEN_TYPE.SYMBOL: JackTokenizer.symbol,
        TOKEN_TYPE.IDENTIFIER: JackTokenizer.identifier,
    }

    def __init__(self, tokenizer: JackTokenizer, output_list: List[str]) -> None:
        self.__tokenizer = tokenizer
        self.__symbol_table = SymbolTable()
        self.__writer = VMWriter(output_list)

        self.__class_name = ''
        self.__while_label = 0
        self.__if_label = 0

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
                and CompilationEngine.__func[token_type](self.__tokenizer) == target
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

    def __define_var(self, name: str, type_: str, kind: SCOPE_TYPE) -> None:
        if self.__symbol_table.is_defined(name):
            self.__tokenizer.wrong_msg(f'Redefined varName {name}')
        self.__symbol_table.define(name, type_, kind)

    # compile系列函数进入时current_token为语法中第一个元素，
    # 执行完毕后current_token为语法结尾的后一个元素（除compile_class）
    def compile_class(self) -> None:
        # 'class'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'class')

        # className
        self.__get_token(TOKEN_TYPE.IDENTIFIER)
        class_name = self.__tokenizer.identifier()
        if class_name != self.__tokenizer.module_name():
            self.__tokenizer.wrong_msg('Different class and file name')
        self.__class_name = class_name

        # '{'
        self.__get_token(TOKEN_TYPE.SYMBOL, '{')

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

        # end
        if self.__tokenizer.has_more_tokens():
            self.__tokenizer.wrong_msg('Encounter token out of class')

    def compile_class_var_dec(self) -> None:
        # 'static' | 'field'
        self.__expect_token(TOKEN_TYPE.KEYWORD)
        if self.__tokenizer.keyword() == 'static':
            var_kind = SCOPE_TYPE.STATIC
        elif self.__tokenizer.keyword() == 'field':
            var_kind = SCOPE_TYPE.FIELD

        # type
        self.__get_token()
        if (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() in {'int', 'char', 'boolean'}
        ):
            var_type = self.__tokenizer.keyword()
        elif self.__tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
            var_type = self.__tokenizer.identifier()
        else:
            self.__tokenizer.wrong_msg('Bad type in classVarDec')

        while True:
            # varName
            self.__get_token(TOKEN_TYPE.IDENTIFIER)
            # symbol table
            self.__define_var(self.__tokenizer.identifier(), var_type, var_kind)

            # (',' varName)* or ;
            self.__get_token(TOKEN_TYPE.SYMBOL)
            if self.__tokenizer.symbol() != ',':
                break

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')
        # end
        self.__get_token()

    def compile_subroutine(self) -> None:
        # 'constructor' | 'function' | 'method'
        self.__expect_token(TOKEN_TYPE.KEYWORD)
        func_type = self.__tokenizer.keyword()

        # symbol table
        self.__symbol_table.start_subroutine()

        # 'void' | type
        self.__get_token()
        if (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() in {'int', 'char', 'boolean', 'void'}
        ):
            pass
        elif self.__tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
            pass
        else:
            self.__tokenizer.wrong_msg('Bad type in subroutineDec')

        # subRoutineName
        self.__get_token(TOKEN_TYPE.IDENTIFIER)
        func_name = f'{self.__class_name}.{self.__tokenizer.identifier()}'

        # '('
        self.__get_token(TOKEN_TYPE.SYMBOL, '(')

        # symbol table
        if func_type == 'method':
            self.__define_var('this', self.__class_name, SCOPE_TYPE.ARG)

        # parameterList
        self.__get_token()
        self.compile_parameter_list()

        # ')'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ')')

        # subRoutineBody start
        # '{'
        self.__get_token(TOKEN_TYPE.SYMBOL, '{')

        # varDec*
        self.__get_token()
        while (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() == 'var'
        ):
            self.compile_var_dec()

        # write vm
        self.__writer.write_function(
            func_name, self.__symbol_table.var_count(SCOPE_TYPE.VAR)
        )

        if func_type == 'method':
            self.__writer.write_push('argument', 0)
            self.__writer.write_pop('pointer', 0)
        elif func_type == 'constructor':
            self.__writer.write_push(
                'constant', self.__symbol_table.var_count(SCOPE_TYPE.FIELD)
            )
            self.__writer.write_call('Memory.alloc', 1)
            self.__writer.write_pop('pointer', 0)

        # statements
        self.compile_statements()

        # '}'
        self.__expect_token(TOKEN_TYPE.SYMBOL, '}')

        # subRoutineBody end
        self.__get_token()

    def compile_parameter_list(self) -> None:
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
                    var_type = self.__tokenizer.keyword()
                elif self.__tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
                    var_type = self.__tokenizer.identifier()
                else:
                    self.__tokenizer.wrong_msg('Bad type in parameterList')

                # varName
                self.__get_token(TOKEN_TYPE.IDENTIFIER)

                # symbol table
                self.__define_var(
                    self.__tokenizer.identifier(), var_type, SCOPE_TYPE.ARG
                )

                # ',' or end
                self.__get_token()
                if (
                    self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
                    and self.__tokenizer.symbol() == ','
                ):
                    self.__get_token()
                else:
                    break

    def compile_var_dec(self) -> None:
        # 'var'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'var')

        # type
        self.__get_token()
        if (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() in {'int', 'char', 'boolean'}
        ):
            var_type = self.__tokenizer.keyword()
        elif self.__tokenizer.token_type() == TOKEN_TYPE.IDENTIFIER:
            var_type = self.__tokenizer.identifier()
        else:
            self.__tokenizer.wrong_msg('Bad type in varDec')

        while True:
            # varName
            self.__get_token(TOKEN_TYPE.IDENTIFIER)

            # symbol table
            self.__define_var(self.__tokenizer.identifier(), var_type, SCOPE_TYPE.VAR)

            # (',' varName)* or ;
            self.__get_token(TOKEN_TYPE.SYMBOL)
            if self.__tokenizer.symbol() != ',':
                break

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')

        # end
        self.__get_token()

    def compile_statements(self) -> None:
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

    def compile_do(self) -> None:
        # 'do'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'do')

        # subroutineCall
        self.__get_token()
        self.__compile_subroutine_call()

        # write vm
        self.__writer.write_pop('temp', 7)

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')

        # end
        self.__get_token()

    def __compile_subroutine_call(self) -> None:
        # subroutineName | className | varName
        self.__expect_token(TOKEN_TYPE.IDENTIFIER)

        first_name = self.__tokenizer.identifier()
        second_name = None

        # if '.' else '('
        self.__get_token(TOKEN_TYPE.SYMBOL)
        if self.__tokenizer.symbol() == '.':
            # subroutineName
            self.__get_token(TOKEN_TYPE.IDENTIFIER)
            second_name = self.__tokenizer.identifier()

            self.__get_token()

        if second_name is None:
            func_name = f'{self.__class_name}.{first_name}'
            is_method = True
        else:
            if self.__symbol_table.is_defined(first_name):
                var_type = self.__symbol_table.type_of(first_name)
                func_name = f'{var_type}.{second_name}'
                is_method = True
            else:
                func_name = f'{first_name}.{second_name}'
                is_method = False

        # '('
        self.__expect_token(TOKEN_TYPE.SYMBOL, '(')

        # write vm
        if is_method:
            if second_name is None:  # push this
                self.__writer.write_push('pointer', 0)
            else:  # push first_name
                var_scope = self.__symbol_table.kind_of(first_name)
                var_index = self.__symbol_table.index_of(first_name)
                if var_scope == SCOPE_TYPE.STATIC:
                    self.__writer.write_push('static', var_index)
                elif var_scope == SCOPE_TYPE.FIELD:
                    self.__writer.write_push('this', var_index)
                elif var_scope == SCOPE_TYPE.ARG:
                    self.__writer.write_push('argument', var_index)
                elif var_scope == SCOPE_TYPE.VAR:
                    self.__writer.write_push('local', var_index)

        # expressionList
        self.__get_token()
        num_args = self.compile_expression_list()
        if is_method:
            num_args += 1

        # write vm
        self.__writer.write_call(func_name, num_args)

        # ')'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ')')

        # end
        self.__get_token()

    def compile_let(self) -> None:
        # 'let'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'let')

        # varName
        self.__get_token(TOKEN_TYPE.IDENTIFIER)
        var_scope = self.__symbol_table.kind_of(self.__tokenizer.identifier())
        var_index = self.__symbol_table.index_of(self.__tokenizer.identifier())

        assign_to_array = False

        # if '[' else '='
        self.__get_token(TOKEN_TYPE.SYMBOL)
        if self.__tokenizer.symbol() == '[':
            assign_to_array = True

            # write vm
            if var_scope == SCOPE_TYPE.STATIC:
                self.__writer.write_push('static', var_index)
            elif var_scope == SCOPE_TYPE.FIELD:
                self.__writer.write_push('this', var_index)
            elif var_scope == SCOPE_TYPE.ARG:
                self.__writer.write_push('argument', var_index)
            elif var_scope == SCOPE_TYPE.VAR:
                self.__writer.write_push('local', var_index)
            else:
                self.__tokenizer.wrong_msg(
                    f'Using undefined varName {self.__tokenizer.identifier()}'
                )

            # expression
            self.__get_token()
            self.compile_expression()

            # write vm
            self.__writer.write_arithmetic('add')
            self.__writer.write_pop('temp', 1)

            # ']'
            self.__expect_token(TOKEN_TYPE.SYMBOL, ']')

            self.__get_token()

        # '='
        self.__expect_token(TOKEN_TYPE.SYMBOL, '=')

        # expression
        self.__get_token()
        self.compile_expression()

        # write vm
        if assign_to_array:
            self.__writer.write_push('temp', 1)
            self.__writer.write_pop('pointer', 1)
            self.__writer.write_pop('that', 0)
        else:
            if var_scope == SCOPE_TYPE.STATIC:
                self.__writer.write_pop('static', var_index)
            elif var_scope == SCOPE_TYPE.FIELD:
                self.__writer.write_pop('this', var_index)
            elif var_scope == SCOPE_TYPE.ARG:
                self.__writer.write_pop('argument', var_index)
            elif var_scope == SCOPE_TYPE.VAR:
                self.__writer.write_pop('local', var_index)
            else:
                self.__tokenizer.wrong_msg(
                    f'Using undefined varName {self.__tokenizer.identifier()}'
                )

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')

        # end
        self.__get_token()

    def compile_while(self) -> None:
        # 'while'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'while')

        # '('
        self.__get_token(TOKEN_TYPE.SYMBOL, '(')

        # write vm
        label_index = self.__while_label
        self.__while_label += 1
        self.__writer.write_label(f'WL1:{label_index}')

        # expression
        self.__get_token()
        self.compile_expression()

        # write vm
        self.__writer.write_arithmetic('not')
        self.__writer.write_if(f'WL2:{label_index}')

        # ')'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ')')

        # '{'
        self.__get_token(TOKEN_TYPE.SYMBOL, '{')

        # statments
        self.__get_token()
        self.compile_statements()

        # write vm
        self.__writer.write_goto(f'WL1:{label_index}')
        self.__writer.write_label(f'WL2:{label_index}')

        # '}'
        self.__expect_token(TOKEN_TYPE.SYMBOL, '}')

        # end
        self.__get_token()

    def compile_return(self) -> None:
        # 'return'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'return')

        # if expression
        self.__get_token()
        if not (
            self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
            and self.__tokenizer.symbol() == ';'
        ):
            # expression
            self.compile_expression()
        else:
            # write vm
            self.__writer.write_push('constant', 0)

        # write vm
        self.__writer.wirte_return()

        # ';'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ';')

        # end
        self.__get_token()

    def compile_if(self) -> None:
        # 'if'
        self.__expect_token(TOKEN_TYPE.KEYWORD, 'if')

        # '('
        self.__get_token(TOKEN_TYPE.SYMBOL, '(')

        # expression
        self.__get_token()
        self.compile_expression()

        # write vm
        label_index = self.__if_label
        self.__if_label += 1
        self.__writer.write_arithmetic('not')
        self.__writer.write_if(f'IF1:{label_index}')

        # ')'
        self.__expect_token(TOKEN_TYPE.SYMBOL, ')')

        # '{'
        self.__get_token(TOKEN_TYPE.SYMBOL, '{')

        # statements
        self.__get_token()
        self.compile_statements()

        # '}'
        self.__expect_token(TOKEN_TYPE.SYMBOL, '}')

        # 'else' or end
        self.__get_token()
        if (
            self.__tokenizer.token_type() == TOKEN_TYPE.KEYWORD
            and self.__tokenizer.keyword() == 'else'
        ):
            # write vm
            self.__writer.write_goto(f'IF2:{label_index}')
            self.__writer.write_label(f'IF1:{label_index}')

            # '{'
            self.__get_token(TOKEN_TYPE.SYMBOL, '{')

            # statements
            self.__get_token()
            self.compile_statements()

            # write vm
            self.__writer.write_label(f'IF2:{label_index}')

            # '}'
            self.__expect_token(TOKEN_TYPE.SYMBOL, '}')

            # end
            self.__get_token()
        else:
            # write vm
            self.__writer.write_label(f'IF1:{label_index}')

    def compile_expression(self) -> None:
        # term
        self.compile_term()

        # (op term)*
        while (
            self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
            and self.__tokenizer.symbol()
            in {'+', '-', '*', '/', '&', '|', '<', '>', '='}
        ):
            # op
            op = self.__tokenizer.symbol()
            # term
            self.__get_token()
            self.compile_term()

            # write vm
            if op == '+':
                self.__writer.write_arithmetic('add')
            elif op == '-':
                self.__writer.write_arithmetic('sub')
            elif op == '*':
                self.__writer.write_call('Math.multiply', 2)
            elif op == '/':
                self.__writer.write_call('Math.divide', 2)
            elif op == '&':
                self.__writer.write_arithmetic('and')
            elif op == '|':
                self.__writer.write_arithmetic('or')
            elif op == '<':
                self.__writer.write_arithmetic('lt')
            elif op == '>':
                self.__writer.write_arithmetic('gt')
            elif op == '=':
                self.__writer.write_arithmetic('eq')

    def compile_term(self) -> None:
        token_type = self.__tokenizer.token_type()

        # integerConstant
        if token_type == TOKEN_TYPE.INT_CONST:
            # write vm
            self.__writer.write_push('constant', self.__tokenizer.int_val())
            # end
            self.__get_token()

        # stringConstant
        elif token_type == TOKEN_TYPE.STRING_CONST:
            str_val = self.__tokenizer.string_val()
            # write vm
            self.__writer.write_push('constant', len(str_val))
            self.__writer.write_call('String.new', 1)
            for char in str_val:
                self.__writer.write_push('constant', ord(char))
                self.__writer.write_call('String.appendChar', 2)
            # end
            self.__get_token()

        # keywordConstant
        elif token_type == TOKEN_TYPE.KEYWORD and self.__tokenizer.keyword() in {
            'true',
            'false',
            'null',
            'this',
        }:
            # write vm
            if self.__tokenizer.keyword() in {'null', 'false'}:
                self.__writer.write_push('constant', 0)
            elif self.__tokenizer.keyword() == 'true':
                self.__writer.write_push('constant', 1)
                self.__writer.write_arithmetic('neg')
            elif self.__tokenizer.keyword() == 'this':
                self.__writer.write_push('pointer', 0)
            # end
            self.__get_token()

        # varName | varName '[' expression ']' | subroutineCall
        elif token_type == TOKEN_TYPE.IDENTIFIER:
            ahead, _ = self.__tokenizer.look_ahead()
            # varName '[' expression ']'
            if ahead == '[':
                # varName
                var_scope = self.__symbol_table.kind_of(self.__tokenizer.identifier())
                var_index = self.__symbol_table.index_of(self.__tokenizer.identifier())

                # write vm
                if var_scope == SCOPE_TYPE.STATIC:
                    self.__writer.write_push('static', var_index)
                elif var_scope == SCOPE_TYPE.FIELD:
                    self.__writer.write_push('this', var_index)
                elif var_scope == SCOPE_TYPE.ARG:
                    self.__writer.write_push('argument', var_index)
                elif var_scope == SCOPE_TYPE.VAR:
                    self.__writer.write_push('local', var_index)
                else:
                    self.__tokenizer.wrong_msg(
                        f'Using undefined varName {self.__tokenizer.identifier()}'
                    )

                # '['
                self.__get_token(TOKEN_TYPE.SYMBOL, '[')

                # expression
                self.__get_token()
                self.compile_expression()

                # write vm
                self.__writer.write_arithmetic('add')
                self.__writer.write_pop('pointer', 1)
                self.__writer.write_push('that', 0)

                # ']'
                self.__expect_token(TOKEN_TYPE.SYMBOL, ']')

                # end
                self.__get_token()

            # subroutineCall
            elif ahead in {'(', '.'}:
                self.__compile_subroutine_call()

            # varName
            else:
                var_scope = self.__symbol_table.kind_of(self.__tokenizer.identifier())
                var_index = self.__symbol_table.index_of(self.__tokenizer.identifier())
                # write vm
                if var_scope == SCOPE_TYPE.STATIC:
                    self.__writer.write_push('static', var_index)
                elif var_scope == SCOPE_TYPE.FIELD:
                    self.__writer.write_push('this', var_index)
                elif var_scope == SCOPE_TYPE.ARG:
                    self.__writer.write_push('argument', var_index)
                elif var_scope == SCOPE_TYPE.VAR:
                    self.__writer.write_push('local', var_index)
                else:
                    self.__tokenizer.wrong_msg(
                        f'Using undefined varName {self.__tokenizer.identifier()}'
                    )
                # end
                self.__get_token()

        # '(' expression ')'
        elif token_type == TOKEN_TYPE.SYMBOL and self.__tokenizer.symbol() == '(':
            # '('
            # expression
            self.__get_token()
            self.compile_expression()
            # ')'
            self.__expect_token(TOKEN_TYPE.SYMBOL, ')')
            # end
            self.__get_token()

        # unaryOp
        elif token_type == TOKEN_TYPE.SYMBOL and self.__tokenizer.symbol() in {
            '-',
            '~',
        }:
            # '-' | '~'
            uop = self.__tokenizer.symbol()
            # term
            self.__get_token()
            self.compile_term()

            # write vm
            if uop == '-':
                self.__writer.write_arithmetic('neg')
            elif uop == '~':
                self.__writer.write_arithmetic('not')

        else:
            self.__tokenizer.wrong_msg('Bad term')

    def compile_expression_list(self) -> int:
        num_args = 0

        if not (
            self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
            and self.__tokenizer.symbol() == ')'
        ):
            while True:
                # expression
                self.compile_expression()
                num_args += 1

                # ',' or end
                if (
                    self.__tokenizer.token_type() == TOKEN_TYPE.SYMBOL
                    and self.__tokenizer.symbol() == ','
                ):
                    self.__get_token()
                else:
                    break

        return num_args
