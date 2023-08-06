''' Main executable for LnaC compiler. '''

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lnac import lexer
from lnac import generator
from lnac import parser

from lnac.nodes import Node

def main():
    args = _getArguments()

    sourcePath = args.input
    outPath = args.out
    keepAssembly = args.keep

    with open(sourcePath, 'r') as f:
        source = f.read()

    tokens = lexer.lex(source)
    tree = parser.parse(tokens)

    if tree is None:
        return 1

    assemblyPath, executablePath = generator.assembly(sourcePath, outPath, tree)
    generator.executable(assemblyPath, executablePath, keepAssembly)

    if not os.path.isfile(executablePath):
        return 1

    return 0

def _getArguments():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('input', type=str,
                            help='the input *.lna file to compile')
    argparser.add_argument('-o', '--out',
                            help='the output executable name')
    argparser.add_argument('-k', '--keep', action='store_true',
                            help='keep the intermediate assembly file')
    return argparser.parse_args()

if __name__ == '__main__':
    sys.exit(main())