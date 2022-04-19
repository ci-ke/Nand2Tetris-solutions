import sys
from .JackCompiler import JackCompiler

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(print('Usage: python -m JackCompiler <filename|dirname>'))
    JackCompiler(sys.argv[1]).run()
