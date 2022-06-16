import sys

from .Assembler import Assembler

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(print('Usage: python -m Assembler <filename>'))
    Assembler(sys.argv[1]).run()
