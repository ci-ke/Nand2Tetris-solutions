from typing import List

from .common import *


class CodeWriter:
    # SP，R13为变量名，表示RAM地址0，13中的内容
    # &SP, &R13为地址，表示0, 13
    # [100]为间接引用，指RAM地址100中的内容
    # [SP]，[R13]表示变量SP，R13作为RAM索引的内存位置的内容，即[[0]]，[[13]]
    # [&SP]==SP，[&R13]==R13
    __asmcode_add = (
        '@SP\n',  # A=&SP
        'AM=M-1\n',  # A,SP=SP-1
        'D=M\n',  # D=[SP]; D=y
        '@R13\n',  # A=&R13
        'M=D\n',  # R13=D; R13=y
        '@SP\n',  # A=&SP
        'AM=M-1\n',  # A,SP=SP-1
        'D=M\n',  # D=[SP]; D=x
        '@R13\n',  # A=&R13
        'D=D+M\n',  # D=D+R13; D=x+y (9)
        '@SP\n',  # A=&SP
        'A=M\n',  # A=SP
        'M=D\n',  # [SP]=D
        '@SP\n',  # A=&SP
        'M=M+1\n',  # SP+=1
    )
    __asmcode_add_replace = 9

    __asmcode_neg = (
        '@SP\n',  # A=&SP
        'AM=M-1\n',  # A,SP=SP-1
        'M=-M\n',  # [SP]=-[SP]; [SP]=-y (2)
        '@SP\n',  # A=&SP
        'M=M+1\n',  # SP+=1
    )
    __asmcode_neg_replace = 2

    __asmcode_eq = (
        '@SP\n',  # A=&SP
        'AM=M-1\n',  # A,SP=SP-1
        'D=M\n',  # D=[SP]; D=y
        '@R13\n',  # A=&R13
        'M=D\n',  # R13=D; R13=y
        '@SP\n',  # A=&SP
        'AM=M-1\n',  # A,SP=SP-1
        'D=M\n',  # D=[SP]; D=x
        '@R13\n',  # A=&R13
        'D=D-M\n',  # D=D+R13; D=x-y
        '@$$CMPt_{}\n',  # (10)
        'D;JEQ\n',  # if D==0, goto compare_true (11)
        '@SP\n',  # A=&SP
        'A=M\n',  # A=SP
        'M=0\n',  # [SP]=0; [SP]=false
        '@$$CMPe_{}\n',  # (15)
        '0;JMP\n',  # goto compare_end
        '($$CMPt_{})\n',  # (compare_true) (17)
        '@SP\n',  # A=&SP
        'A=M\n',  # A=SP
        'M=-1\n',  # [SP]=-1; [SP]=true
        '($$CMPe_{})\n',  # (compare_end) (21)
        '@SP\n',  # A=&SP
        'M=M+1\n',  # SP+=1
    )
    __asmcode_eq_replace = 11
    __asmcode_eq_format = (10, 15, 17, 21)

    __asmcode_push_local = (
        '@LCL\n',  # A=&LCL
        'D=M\n',  # D=LCL
        '@{index}\n',  # A=index
        'A=D+A\n',  # A=LCL+index
        'D=M\n',  # D=[LCL+index]
        '@SP\n',  # A=&SP
        'A=M\n',  # A=SP
        'M=D\n',  # [SP]=D
        '@SP\n',  # A=&SP
        'M=M+1\n',  # SP+=1
    )
    __asmcode_push_local_replace = 0
    __asmcode_push_local_format = 2

    __asmcode_pop_local = (
        '@LCL\n',  # A=&LCL
        'D=M\n',  # D=LCL
        '@{index}\n',  # A=index
        'D=D+A\n',  # D=LCL+index
        '@R13\n',  # A=&R13
        'M=D\n',  # R13=LCL+index
        '@SP\n',  # A=&SP
        'AM=M-1\n',  # A,SP=SP-1
        'D=M\n',  # D=[SP]
        '@R13\n',  # A=&R13
        'A=M\n',  # A=LCL+index
        'M=D\n',  # [LCL+index]=[SP]
    )
    __asmcode_pop_local_replace = 0
    __asmcode_pop_local_format = 2

    __asmcode_push_temp = (
        '@{Rname}\n',  # A=&Ri
        'D=M\n',  # D=Ri
        '@SP\n',  # A=&SP
        'A=M\n',  # A=SP
        'M=D\n',  # [SP]=D
        '@SP\n',  # A=&SP
        'M=M+1\n',  # SP+=1
    )
    __asmcode_push_temp_format = 0

    __asmcode_pop_temp = (
        '@SP\n',  # A=&SP
        'AM=M-1\n',  # A,SP=SP-1
        'D=M\n',  # D=[SP]
        '@{Rname}\n',  # A=&Ri
        'M=D\n',  # Ri=D
    )
    __asmcode_pop_temp_format = 3

    def __init__(self, pathname: str) -> None:
        self.__pathname = pathname
        self.__asm_codes: List[str] = []
        self.__label_index = 0

    def set_file_name(self, parsing_filename: str) -> None:
        self.__parsing_filename = parsing_filename

    def write_arithmetic(self, command: str) -> None:
        if command == 'add':
            code = list(self.__asmcode_add)
        elif command == 'sub':
            code = list(self.__asmcode_add)
            code[self.__asmcode_add_replace] = 'D=D-M\n'
        elif command == 'neg':
            code = list(self.__asmcode_neg)
        elif command == 'eq':
            code = list(self.__asmcode_eq)
            for i in self.__asmcode_eq_format:
                code[i] = code[i].format(self.__label_index)
            self.__label_index += 1
        elif command == 'gt':
            code = list(self.__asmcode_eq)
            code[self.__asmcode_eq_replace] = 'D;JGT\n'
            for i in self.__asmcode_eq_format:
                code[i] = code[i].format(self.__label_index)
            self.__label_index += 1
        elif command == 'lt':
            code = list(self.__asmcode_eq)
            code[self.__asmcode_eq_replace] = 'D;JLT\n'
            for i in self.__asmcode_eq_format:
                code[i] = code[i].format(self.__label_index)
            self.__label_index += 1
        elif command == 'and':
            code = list(self.__asmcode_add)
            code[self.__asmcode_add_replace] = 'D=D&M\n'
        elif command == 'or':
            code = list(self.__asmcode_add)
            code[self.__asmcode_add_replace] = 'D=D|M\n'
        elif command == 'not':
            code = list(self.__asmcode_neg)
            code[self.__asmcode_neg_replace] = 'M=!M\n'
        else:
            assert False

        self.__asm_codes.extend(code)

    def write_push_pop(
        self, command_type: COMMAND_TYPE, segment: str, index: int
    ) -> bool:  # return bool to support error check
        assert command_type in {COMMAND_TYPE.C_PUSH, COMMAND_TYPE.C_POP}

        if not 0 <= index <= 32767:
            return False

        if command_type == COMMAND_TYPE.C_PUSH:
            if segment == 'constant':
                code = [
                    f'@{index}\n',  # A=index
                    'D=A\n',  # D=A
                    '@SP\n',  # A=&SP
                    'A=M\n',  # A=SP
                    'M=D\n',  # [SP]=D
                    '@SP\n',  # A=&SP
                    'M=M+1\n',  # SP+=1
                ]
            elif segment == 'local':
                code = list(self.__asmcode_push_local)
                code[self.__asmcode_push_local_format] = code[
                    self.__asmcode_push_local_format
                ].format(index=index)
            elif segment == 'argument':
                code = list(self.__asmcode_push_local)
                code[self.__asmcode_push_local_replace] = '@ARG\n'
                code[self.__asmcode_push_local_format] = code[
                    self.__asmcode_push_local_format
                ].format(index=index)
            elif segment == 'this':
                code = list(self.__asmcode_push_local)
                code[self.__asmcode_push_local_replace] = '@THIS\n'
                code[self.__asmcode_push_local_format] = code[
                    self.__asmcode_push_local_format
                ].format(index=index)
            elif segment == 'that':
                code = list(self.__asmcode_push_local)
                code[self.__asmcode_push_local_replace] = '@THAT\n'
                code[self.__asmcode_push_local_format] = code[
                    self.__asmcode_push_local_format
                ].format(index=index)
            elif segment == 'temp':
                if 0 <= index <= 7:
                    code = list(self.__asmcode_push_temp)
                    code[self.__asmcode_push_temp_format] = code[
                        self.__asmcode_push_temp_format
                    ].format(Rname=f'R{5 + index}')
                else:
                    return False
            elif segment == 'pointer':
                if index == 0:
                    code = list(self.__asmcode_push_temp)
                    code[self.__asmcode_push_temp_format] = code[
                        self.__asmcode_push_temp_format
                    ].format(Rname='THIS')
                elif index == 1:
                    code = list(self.__asmcode_push_temp)
                    code[self.__asmcode_push_temp_format] = code[
                        self.__asmcode_push_temp_format
                    ].format(Rname='THAT')
                else:
                    return False
            elif segment == 'static':
                code = list(self.__asmcode_push_temp)
                code[self.__asmcode_push_temp_format] = code[
                    self.__asmcode_push_temp_format
                ].format(Rname=f'{self.__parsing_filename}.{index}')
            else:
                return False
        elif command_type == COMMAND_TYPE.C_POP:
            if segment == 'constant':
                return False
            elif segment == 'local':
                code = list(self.__asmcode_pop_local)
                code[self.__asmcode_pop_local_format] = code[
                    self.__asmcode_pop_local_format
                ].format(index=index)
            elif segment == 'argument':
                code = list(self.__asmcode_pop_local)
                code[self.__asmcode_pop_local_replace] = '@ARG\n'
                code[self.__asmcode_pop_local_format] = code[
                    self.__asmcode_pop_local_format
                ].format(index=index)
            elif segment == 'this':
                code = list(self.__asmcode_pop_local)
                code[self.__asmcode_pop_local_replace] = '@THIS\n'
                code[self.__asmcode_pop_local_format] = code[
                    self.__asmcode_pop_local_format
                ].format(index=index)
            elif segment == 'that':
                code = list(self.__asmcode_pop_local)
                code[self.__asmcode_pop_local_replace] = '@THAT\n'
                code[self.__asmcode_pop_local_format] = code[
                    self.__asmcode_pop_local_format
                ].format(index=index)
            elif segment == 'temp':
                if 0 <= index <= 7:
                    code = list(self.__asmcode_pop_temp)
                    code[self.__asmcode_pop_temp_format] = code[
                        self.__asmcode_pop_temp_format
                    ].format(Rname=f'R{5 + index}')
                else:
                    return False
            elif segment == 'pointer':
                if index == 0:
                    code = list(self.__asmcode_pop_temp)
                    code[self.__asmcode_pop_temp_format] = code[
                        self.__asmcode_pop_temp_format
                    ].format(Rname='THIS')
                elif index == 1:
                    code = list(self.__asmcode_pop_temp)
                    code[self.__asmcode_pop_temp_format] = code[
                        self.__asmcode_pop_temp_format
                    ].format(Rname='THAT')
                else:
                    return False
            elif segment == 'static':
                code = list(self.__asmcode_pop_temp)
                code[self.__asmcode_pop_temp_format] = code[
                    self.__asmcode_pop_temp_format
                ].format(Rname=f'{self.__parsing_filename}.{index}')
            else:
                return False

        self.__asm_codes.extend(code)
        return True

    def write_init(self) -> None:
        code = ['@256\n', 'D=A\n', '@SP\n', 'M=D\n']
        self.__asm_codes.extend(code)
        self.write_call('Sys.init', 0)
        code = ['($$HALT)\n', '@$$HALT\n', '0;JMP\n']
        self.__asm_codes.extend(code)

    def write_label(self, label: str, in_function: str) -> bool:
        if SymbolChecker.legal_symbol(label):
            code = [f'({in_function}${label})\n']
            self.__asm_codes.extend(code)
            return True
        else:
            return False

    def write_goto(self, label: str, in_function: str) -> bool:
        if SymbolChecker.legal_symbol(label):
            code = [f'@{in_function}${label}\n', '0;JMP\n']
            self.__asm_codes.extend(code)
            return True
        else:
            return False

    def write_if(self, label: str, in_function: str) -> bool:
        if SymbolChecker.legal_symbol(label):
            code = [
                '@SP\n',  # A=&SP
                'AM=M-1\n',  # A,SP=SP-1
                'D=M\n',  # D=[SP]
                f'@$$IFn_{self.__label_index}\n',
                'D;JEQ\n',
                f'@{in_function}${label}\n',
                '0;JMP\n',
                f'($$IFn_{self.__label_index})\n',
            ]
            self.__label_index += 1
            self.__asm_codes.extend(code)
            return True
        else:
            return False

    def write_call(self, function_name: str, num_args: int) -> bool:
        if SymbolChecker.legal_symbol(function_name):
            code = [
                f'@$$RETADDR_{self.__label_index}\n',  # A=retaddr
                'D=A\n',  # D=retaddr
                '@SP\n',  # A=&SP
                'A=M\n',  # A=SP
                'M=D\n',  # [SP]=D=retaddr
                '@SP\n',  # A=&SP
                'M=M+1\n',  # SP+=1; push retaddr
                '@LCL\n',  # A=&LCL
                'D=M\n',  # D=LCL
                '@SP\n',  # A=&SP
                'A=M\n',  # A=SP
                'M=D\n',  # [SP]=D=LCL
                '@SP\n',  # A=&SP
                'M=M+1\n',  # SP+=1; push LCL
                '@ARG\n',  # A=&ARG
                'D=M\n',  # D=ARG
                '@SP\n',  # A=&SP
                'A=M\n',  # A=SP
                'M=D\n',  # [SP]=D=ARG
                '@SP\n',  # A=&SP
                'M=M+1\n',  # SP+=1; push ARG
                '@THIS\n',  # A=&THIS
                'D=M\n',  # D=THIS
                '@SP\n',  # A=&SP
                'A=M\n',  # A=SP
                'M=D\n',  # [SP]=D=THIS
                '@SP\n',  # A=&SP
                'M=M+1\n',  # SP+=1; push THIS
                '@THAT\n',  # A=&THAT
                'D=M\n',  # D=THAT
                '@SP\n',  # A=&SP
                'A=M\n',  # A=SP
                'M=D\n',  # [SP]=D=THAT
                '@SP\n',  # A=&SP
                'M=M+1\n',  # SP+=1; push THAT
                '@SP\n',  # A=&SP
                'D=M\n',  # D=SP
                f'@{num_args+5}\n',  # A=n+5
                'D=D-A\n',  # D=SP-n-5
                '@ARG\n',  # A=&ARG
                'M=D\n',  # ARG=SP-n-5
                '@SP\n',  # A=&SP
                'D=M\n',  # D=SP
                '@LCL\n',  # A=&LCL
                'M=D\n',  # LCL=SP
                f'@{function_name}\n',
                '0;JMP\n',  # goto f
                f'($$RETADDR_{self.__label_index})\n',  # (retaddr)
            ]
            self.__label_index += 1
            self.__asm_codes.extend(code)
            return True
        else:
            return False

    def write_return(self) -> None:
        code = [
            '@LCL\n',  # A=&LCL
            'D=M\n',  # D=LCL
            '@R13\n',  # A=&R13
            'M=D\n',  # R13=D=LCL; FRAME=LCL
            '@5\n',  # A=5
            'A=D-A\n',  # A=D-5=LCL-5
            'D=M\n',  # D=[LCL-5]
            '@R14\n',  # A=&R14
            'M=D\n',  # R14=D=[LCL-5]=RET; RET=[FRAME-5]
            '@SP\n',  # A=&SP
            'AM=M-1\n',  # A,SP=SP-1
            'D=M\n',  # D=[SP]
            '@ARG\n',  # A=&ARG
            'A=M\n',  # A=ARG
            'M=D\n',  # [ARG]=D=[SP]; [ARG]=pop()
            'D=A+1\n',  # D=ARG+1
            '@SP\n',  # A=&SP
            'M=D\n',  # SP=D; SP=ARG+1
            '@R13\n',  # A=&R13=&FRAME
            'AM=M-1\n',  # A,FRAME=FRAME-1
            'D=M\n',  # D=[FRAME]
            '@THAT\n',  # A=&THAT
            'M=D\n',  # THAT=D; THAT=[oriFRAME-1]
            '@R13\n',  # A=&R13=&FRAME
            'AM=M-1\n',  # A,FRAME=FRAME-1
            'D=M\n',  # D=[FRAME]
            '@THIS\n',  # A=&THIS
            'M=D\n',  # THIS=D; THIS=[oriFRAME-2]
            '@R13\n',  # A=&R13=&FRAME
            'AM=M-1\n',  # A,FRAME=FRAME-1
            'D=M\n',  # D=[FRAME]
            '@ARG\n',  # A=&ARG
            'M=D\n',  # ARG=D; ARG=[oriFRAME-3]
            '@R13\n',  # A=&R13=&FRAME
            'AM=M-1\n',  # A,FRAME=FRAME-1
            'D=M\n',  # D=[FRAME]
            '@LCL\n',  # A=&LCL
            'M=D\n',  # LCL=D; LCL=[oriFRAME-4]
            '@R14\n',  # A=&R14
            'A=M\n',  # A=R14=RET
            '0;JMP\n',  # goto RET
        ]
        self.__asm_codes.extend(code)

    def write_function(self, function_name: str, num_locals: int) -> bool:
        if SymbolChecker.legal_symbol(function_name):
            code = [
                f'({function_name})\n',
                f'@{num_locals}\n',  # A=num_locals
                'D=A\n',  # D=num_locals
                f'($$PULCs_{self.__label_index})\n',
                f'@$$PULCe_{self.__label_index}\n',
                'D;JEQ\n',
                '@SP\n',  # A=&SP
                'A=M\n',  # A=SP
                'M=0\n',  # [SP]=0
                '@SP\n',  # A=&SP
                'M=M+1\n',  # SP+=1
                'D=D-1\n',  # D-=1
                f'@$$PULCs_{self.__label_index}\n',
                '0;JMP\n',
                f'($$PULCe_{self.__label_index})\n',
            ]
            self.__label_index += 1
            self.__asm_codes.extend(code)
            return True
        else:
            return False

    def close(self) -> None:
        with open(self.__pathname, 'w') as f:
            f.writelines(self.__asm_codes)
        print(f'Output: {self.__pathname}')
