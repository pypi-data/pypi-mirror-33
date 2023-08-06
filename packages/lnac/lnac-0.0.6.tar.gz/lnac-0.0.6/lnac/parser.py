''' The main parser implementation '''

from lnac.tokens import TokenType
from lnac.ast import Ast
from lnac.nodes import Node, Program, Function, Return, Constant, UnaryOp

def parse(tokens):
    program = _parse_program(tokens)

    return Ast(program)

def _parse_program(tokens):
    token = tokens.pop(0)
    if token.ttype is not TokenType.IDENTIFIER:
        print ('Error on line {}. `{}` is not an identifier'.format(token.line, token.value))
        return Node.FAIL

    token = tokens.pop(0)
    if token.ttype is not TokenType.DEFINITION:
        print ('Error on line {}. `{}` is not an `:`'.format(token.line, token.value))
        return Node.FAIL

    token = tokens.pop(0)
    if token.ttype is not TokenType.TYPE_INT:
        print ('Error on line {}. `{}` is not of type `int`'.format(token.line, token.value))
        return Node.FAIL

    function = _parse_function(tokens)

    if function is Node.FAIL:
        return Node.FAIL

    return Program('Program', function)

def _parse_function(tokens):
    token = tokens.pop(0)
    if token.ttype is not TokenType.IDENTIFIER:
        print ('Error on line {}. `{}` is not an identifier'.format(token.line, token.value))
        return Node.FAIL

    name = token

    token = tokens.pop(0)
    if token.ttype is not TokenType.ASSIGNMENT:
        print ('Error on line {}. `{}` is not an `=`'.format(token.line, token.value))
        return Node.FAIL

    statement = _parse_statement(tokens)

    if statement is Node.FAIL:
        return Node.FAIL

    return Function(name.value, statement)

def _parse_statement(tokens):
    token = tokens.pop(0)
    if token.ttype is not TokenType.RETURNS:
        print ('Error on line {}. `{}` is not a `=>`'.format(token.line, token.value))
        return Node.FAIL

    expression = _parse_expression(tokens)

    if expression is Node.FAIL:
        return Node.FAIL

    return Return(expression)

def _parse_expression(tokens):
    token = tokens.pop(0)
    if token.ttype is TokenType.LITERAL_INT:
        return Constant(token.value)
    elif token.isUnaryOp():
        inner = _parse_expression(tokens)
        return UnaryOp(token.value, inner)
    else:
        print ('Error on line {}. `{}` is not part of a valid expression'.format(token.line, token.value))
        return Node.FAIL
