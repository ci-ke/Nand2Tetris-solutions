import sys, os
from Assembler.Assembler import Assembler

files = [
    'add/Add',
    'max/Max',
    'max/MaxL',
    'pong/Pong',
    'pong/PongL',
    'rect/Rect',
    'rect/RectL',
]

if __name__ == '__main__':
    if len(sys.argv) != 2 or (sys.argv[1] not in {'build', 'clean', 'open'}):
        sys.exit(print('Usage: python make.py <build|clean|open>'))

    if sys.argv[1] == 'build':
        for f in files:
            Assembler(f + '.asm').run()

    elif sys.argv[1] == 'clean':
        for f in files:
            try:
                os.remove(f + '.hack')
            except FileNotFoundError:
                pass

    elif sys.argv[1] == 'open':
        srcpath = os.getcwd()
        os.chdir('../../tools/bin')
        tgtpath = os.getcwd()
        with open(tgtpath + '/' + 'Assembler.dat', 'w') as f:
            f.write(srcpath + '\n')
        os.system('..\\Assembler.bat')
