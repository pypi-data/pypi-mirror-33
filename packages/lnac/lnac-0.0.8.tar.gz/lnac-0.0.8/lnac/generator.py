''' Implementation for generating assembly code and the resulting executable '''

from os import path, remove
import subprocess

from lnac.ast import Ast

def assembly(sourcePath : str, outPath : str, tree : Ast):
    assemblyPath, executablePath = _programPaths(sourcePath, outPath)

    with open(assemblyPath, 'w') as f:
        print(str(tree.root), file=f)

    return assemblyPath, executablePath

def executable(assemblyPath : str, executablePath : str, keepAssembly : bool):
    subprocess.run(['gcc', '-O2', assemblyPath, '-o', executablePath])

    if not keepAssembly:
        remove(assemblyPath)

def _programPaths(sourcePath : str, outPath : str):
    sourceName = path.splitext(path.basename(sourcePath))[0]

    outClean = outPath if outPath else '.'
    outDir = path.dirname(outClean)

    programPath = path.join(outDir, sourceName)

    assemblyPath = '{}.s'.format(programPath)
    executablePath = programPath if path.isdir(outClean) else outClean

    return assemblyPath, executablePath