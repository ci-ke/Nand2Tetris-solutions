import sys, os

from VMTranslator.VMTranslator import VMTranslator

files = [
    'ProgramFlow/BasicLoop/BasicLoop',
    'ProgramFlow/FibonacciSeries/FibonacciSeries',
    'FunctionCalls/SimpleFunction/SimpleFunction',
]

dirs = [
    'FunctionCalls/FibonacciElement',
    'FunctionCalls/NestedCall',
    'FunctionCalls/StaticsTest',
]

if __name__ == '__main__':
    if len(sys.argv) != 2 or (sys.argv[1] not in {'build', 'clean', 'open'}):
        sys.exit(print('Usage: python make.py <build | clean | open>'))

    if sys.argv[1] == 'build':
        for f in files:
            VMTranslator(f + '.vm').run()
        for d in dirs:
            VMTranslator(d).run()

    elif sys.argv[1] == 'clean':
        for f in files:
            try:
                os.remove(f + '.asm')
            except FileNotFoundError:
                pass
        for d in dirs:
            try:
                os.remove(d + '/' + d.split('/')[-1] + '.asm')
            except FileNotFoundError:
                pass

    elif sys.argv[1] == 'open':
        srcpath = os.getcwd()
        os.chdir('../../tools/bin')
        tgtpath = os.getcwd()
        with open(tgtpath + '/' + 'CPU Emulator.dat', 'w', encoding='utf8') as fp:
            fp.write(srcpath + '\n')
        os.system('..\\CPUEmulator.bat')
