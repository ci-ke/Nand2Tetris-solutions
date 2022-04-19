import sys, os, shutil
from JackAnalyzer.JackAnalyzer import JackAnalyzer

dirs = ['ArrayTest', 'ExpressionLessSquare', 'Square']

if __name__ == '__main__':
    if len(sys.argv) != 2 or (sys.argv[1] not in {'build', 'clean', 'check'}):
        sys.exit(print('Usage: python make.py <build|clean|check>'))

    if sys.argv[1] == 'build':
        for d in dirs:
            JackAnalyzer(d).run()

    elif sys.argv[1] == 'clean':
        for d in dirs:
            try:
                shutil.rmtree(d + '/output')
            except FileNotFoundError:
                pass

    elif sys.argv[1] == 'check':
        for d in dirs:
            try:
                output_files = os.listdir(d + '/output')
                for f in output_files:
                    os.system(f'..\\..\\tools\\TextComparer.bat {d}/{f} {d}/output/{f}')
            except FileNotFoundError:
                pass
