import sys, os

from JackCompiler.JackCompiler import JackCompiler

dirs = ['Average', 'ComplexArrays', 'ConvertToBin', 'Pong', 'Seven', 'Square']

if __name__ == '__main__':
    if len(sys.argv) != 2 or (sys.argv[1] not in {'build', 'clean', 'open'}):
        sys.exit(print('Usage: python make.py <build | clean | open>'))

    if sys.argv[1] == 'build':
        for d in dirs:
            JackCompiler(d).run()

    elif sys.argv[1] == 'clean':
        for d in dirs:
            try:
                fs = os.listdir(d)
                for f in fs:
                    if os.path.splitext(f)[1] == '.vm':
                        os.remove(d + '/' + f)
            except FileNotFoundError:
                pass

    elif sys.argv[1] == 'open':
        srcpath = os.getcwd()
        os.chdir('../../tools/bin')
        tgtpath = os.getcwd()
        with open(tgtpath + '/' + 'Virtual Machine Emulator.dat', 'w') as fp:
            fp.write(srcpath + '\n')
        os.system('..\\VMEmulator.bat')
