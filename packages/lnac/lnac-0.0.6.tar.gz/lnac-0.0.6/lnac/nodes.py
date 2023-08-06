''' Node implementaitons used for parsing '''

import os

class Node:
    def __init__(self, name : str, value):
        self.name = name
        self.value = value

    def __str__(self):
        return '{}{}{}'.format(self.name, '\n', str(self.value))

class Expression(Node):
    def __init__(self, name : str, value):
        Node.__init__(self, 'EXPRESSION', value)

class Constant(Expression):
    def __init__(self, number : int):
        self.number = number
        Expression.__init__(self, 'CONSTANT', self.number)

    def __str__(self):
        return 'movl\t${}, %eax'.format(str(self.number))

class UnaryOp(Expression):
    def __init__(self, tok, expression : Expression):
        self.tok = tok
        self.expression = expression
        Expression.__init__(self, 'UNARY', self.tok)

    def __str__(self):
        operations = {
            '-' : '{}{}neg\t\t%eax'.format(str(self.expression), '\n'),
            '!' : '{0}{1}cmpl\t$0, %eax{1}movl\t$0, %eax{1}sete\t%al'.format(str(self.expression), '\n')
        }
        return operations.get(self.tok, 'INVALID UNARY OPERATION')

class Return(Node):
    def __init__(self, constant : Constant):
        self.constant = constant
        Node.__init__(self, 'RETURN', self.constant)

    def __str__(self):
        return '{}{}ret'.format(str(self.constant), '\n')

class Function(Node):
    def __init__(self, name : str, returns : Return):
        self.returns = returns
        Node.__init__(self, name, self.returns)

    def __str__(self):
        return '_{}:{}{}'.format(self.name, '\n', str(self.returns))

class Program(Node):
    def __init__(self, name : str, function : Function):
        self.function = function
        Node.__init__(self, name, self.function)

    def __str__(self):
        return '.globl _{}{}{}'.format(self.function.name, '\n', str(self.function))

Node.FAIL = Node('Fail', None)