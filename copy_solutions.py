# copy solutions in projects/ to projects_solutions/

import os, shutil

project_dir = 'projects'

src = {
    '01': {'.hdl'},
    '02': {'.hdl'},
    '03/a': {'.hdl'},
    '03/b': {'.hdl'},
    '04/fill': {'.asm'},
    '04/mult': {'.asm'},
    '05': {'.hdl'},
    '06': {'Assembler/', '.py', '.md'},
    '07': {'VMTranslator_alpha/', '.py', '.md'},
    '08': {'VMTranslator/', '.py', '.md'},
    '10': {'JackAnalyzer/', '.py', '.md'},
    '11': {'JackCompiler/', '.py', '.md'},
    '12': {'.jack', '.py', '.md'},
}

solution_dir = 'projects_solutions'

if not os.path.isdir(solution_dir):
    os.mkdir(solution_dir)

for ch_dir in src:
    src_dir = project_dir + '/' + ch_dir

    tgt_dir = solution_dir + '/' + ch_dir[:2]
    if not os.path.isdir(tgt_dir):
        os.mkdir(tgt_dir)

    for tgt in src[ch_dir]:
        if tgt[0] == '.':
            all_files = os.listdir(src_dir)
            for f in all_files:
                if os.path.splitext(f)[1] == tgt:
                    shutil.copy(src_dir + '/' + f, tgt_dir)
                    print('copy: {} -> {}'.format(src_dir + '/' + f, tgt_dir + '/' + f))
        elif tgt[-1] == '/':
            if os.path.isdir(tgt_dir + '/' + tgt):
                shutil.rmtree(tgt_dir + '/' + tgt)
            shutil.copytree(src_dir + '/' + tgt, tgt_dir + '/' + tgt)
            print('copy: {} -> {}'.format(src_dir + '/' + tgt, tgt_dir + '/' + tgt))
        else:
            shutil.copy(src_dir + '/' + tgt, tgt_dir)
            print('copy: {} -> {}'.format(src_dir + '/' + tgt, tgt_dir + '/' + tgt))
