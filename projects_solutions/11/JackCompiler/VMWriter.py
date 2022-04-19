class VMWriter:
    def __init__(self, output_list: list) -> None:
        self.__output_list = output_list

    def write_push(self, segment: str, index: int) -> None:
        assert segment in {
            'argument',
            'local',
            'static',
            'constant',
            'this',
            'that',
            'pointer',
            'temp',
        }
        assert 0 <= index <= 32767

        self.__output_list.append(f'push {segment} {index}\n')

    def write_pop(self, segment: str, index: int) -> None:
        assert segment in {
            'argument',
            'local',
            'static',
            'constant',
            'this',
            'that',
            'pointer',
            'temp',
        }
        assert 0 <= index <= 32767

        self.__output_list.append(f'pop {segment} {index}\n')

    def write_arithmetic(self, command: str) -> None:
        assert command in {'add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'}

        self.__output_list.append(command + '\n')

    def write_label(self, string: str) -> None:
        self.__output_list.append(f'label {string}\n')

    def write_goto(self, string: str) -> None:
        self.__output_list.append(f'goto {string}\n')

    def write_if(self, string: str) -> None:
        self.__output_list.append(f'if-goto {string}\n')

    def write_call(self, name: str, num_args: int) -> None:
        self.__output_list.append(f'call {name} {num_args}\n')

    def write_function(self, name: str, num_locals: int) -> None:
        self.__output_list.append(f'function {name} {num_locals}\n')

    def wirte_return(self) -> None:
        self.__output_list.append('return\n')
