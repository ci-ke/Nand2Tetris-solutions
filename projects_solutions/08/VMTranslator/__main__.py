import sys

from .VMTranslator import VMTranslator

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(print('Usage: python -m VMTranslator <filename | dirname>'))
    VMTranslator(sys.argv[1]).run()
