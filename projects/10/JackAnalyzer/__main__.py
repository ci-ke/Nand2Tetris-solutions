import sys

from .JackAnalyzer import JackAnalyzer

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(print('Usage: python -m JackAnalyzer <filename | dirname>'))
    JackAnalyzer(sys.argv[1]).run()
