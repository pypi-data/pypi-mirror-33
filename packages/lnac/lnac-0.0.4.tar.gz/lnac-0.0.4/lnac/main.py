import argparse
import os
import subprocess
import sys

from lnac import lexer, generator
from lnac.parser import parser
from lnac.tree.ast import Ast
from lnac.tree.nodes import Node

# lnac -o build/return2 -k demos/return2.lna
# lnac demos/return2.lna
def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('input', type=str,
                            help='the input *.lna file to compile')
    argparser.add_argument('-o', '--out',
                            help='the output executable name')
    argparser.add_argument('-k', '--keep', action='store_true',
                            help='keep the intermediate assembly file')
    args = argparser.parse_args()

    sourcePath = args.input
    outPath = args.out
    keepAssembly = args.keep

    with open(sourcePath, 'r') as f:
        source = f.read()

    tokens = lexer.lex(source)
    tree = parser.parse(tokens)

    if tree.root is Node.FAIL:
        return 1

    assemblyPath, executablePath = generator.assembly(sourcePath, outPath, tree)

    subprocess.run(['gcc', '-m32', assemblyPath, '-o', executablePath])

    if not keepAssembly:
        os.remove(assemblyPath)

    return 0

if __name__ == '__main__':
    sys.exit(main())