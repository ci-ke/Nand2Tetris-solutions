import sys, os, shutil

files = ['Array', 'Keyboard', 'Math', 'Memory', 'Output', 'Screen', 'String', 'Sys']

if __name__ == '__main__':
    if len(sys.argv) != 2 or (sys.argv[1] not in {'build', 'clean', 'open'}):
        sys.exit(print('Usage: python make.py <build|clean|open>'))

    if sys.argv[1] == 'build':
        os.system(f'..\\..\\tools\\JackCompiler.bat .')

        if not os.path.isdir('JackOS'):
            os.mkdir('JackOS')

        for f in files:
            if os.path.exists('JackOS/' + f + '.vm'):
                os.remove('JackOS/' + f + '.vm')
            shutil.move(f + '.vm', 'JackOS')

            if os.path.isdir(f + 'Test'):
                shutil.copy('JackOS/' + f + '.vm', f + 'Test')
                os.system(f'..\\..\\tools\\JackCompiler.bat {f}Test')

                if f == 'Memory':
                    shutil.copy('JackOS/Memory.vm', 'MemoryTest/MemoryDiag')
                    os.system(f'..\\..\\tools\\JackCompiler.bat MemoryTest/MemoryDiag')

    elif sys.argv[1] == 'clean':
        if os.path.isdir('JackOS'):
            shutil.rmtree('JackOS')

        for f in files:
            try:
                dfs = os.listdir(f + 'Test')
                for df in dfs:
                    if os.path.splitext(df)[1] == '.vm':
                        os.remove(f + 'Test/' + df)
            except FileNotFoundError:
                pass

        try:
            fs = os.listdir('MemoryTest/MemoryDiag')
            for f in fs:
                if os.path.splitext(f)[1] == '.vm':
                    os.remove('MemoryTest/MemoryDiag/' + f)
        except FileNotFoundError:
            pass

    elif sys.argv[1] == 'open':
        srcpath = os.getcwd()
        os.chdir('../../tools/bin')
        tgtpath = os.getcwd()
        with open(tgtpath + '/' + 'Virtual Machine Emulator.dat', 'w') as f:
            f.write(srcpath + '\n')
        os.system('..\\VMEmulator.bat')
