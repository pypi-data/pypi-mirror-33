import re

from lnac.tokens import Token, TokenType

def lex(contents):
    output = []

    lines = contents.splitlines()
    for i, line in enumerate(lines):
        value = ''
        lnum = i + 1
        for char in line:
            if char is ' ':
                if value:
                    output.append(Token(value, lnum))
                    value = ''
            elif TokenType.isSingleOp(char):
                if not value:
                    value += char
                output.append(Token(value, lnum))
                value = ''
            else:
                value += char
        if value:
            output.append(Token(value, lnum))

    return output
