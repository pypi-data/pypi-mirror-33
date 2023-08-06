import re

Types = []

class TokenType:
    def __init__(self, name : str, pattern : str):
        self.name = name
        self.pattern = pattern
        Types.append(self)

    def _matches(self, value : str):
        return re.match(self.pattern, value)

    @staticmethod
    def getType(value : str):
        for ttype in Types:
            if ttype._matches(value):
                return ttype
        return 'NAK'

    @staticmethod
    def isSingleOp(value):
        singleOperators = [
            TokenType.NEGATION,
            TokenType.LOGICAL_NEGATION,
            TokenType.ADDITION,
            TokenType.MULTIPLICATION,
            TokenType.DIVISION,
            TokenType.OPEN_PARENTHESIS,
            TokenType.CLOSED_PARENTHESIS
        ]
        return any(o._matches(value) for o in singleOperators)

class Token:
    def __init__(self, value : str, line : int):
        self.ttype = TokenType.getType(value)
        self.value = value
        self.line = line

    def __str__(self):
        return '({}, {}, {})'.format(self.ttype.name, self.value, self.line)

    def isUnaryOp(self):
        unaryOperators = [
            TokenType.NEGATION,
            TokenType.LOGICAL_NEGATION
        ]
        return self.ttype in unaryOperators

TokenType.DEFINITION = TokenType('DEFINITION', ':')
TokenType.RETURNS = TokenType('RETURNS', '=>')
TokenType.ASSIGNMENT = TokenType('ASSIGNMENT', '=')
TokenType.NEGATION = TokenType('NEGATION', '-')
TokenType.LOGICAL_NEGATION = TokenType('LOGICAL_NEGATION', '!')
TokenType.ADDITION = TokenType('ADDITION', '\\+')
TokenType.MULTIPLICATION = TokenType('MULTIPLICATION', '\\*')
TokenType.DIVISION = TokenType('DIVISION', '/')
TokenType.OPEN_PARENTHESIS = TokenType('OPEN_PARENTHESIS', '\\(')
TokenType.CLOSED_PARENTHESIS = TokenType('CLOSED_PARENTHESIS', '\\)')
TokenType.TYPE_INT = TokenType('TYPE_INT', 'int')
TokenType.LITERAL_INT = TokenType('LITERAL_INT', '[0-9]+')
TokenType.IDENTIFIER = TokenType('IDENTIFIER', '[a-zA-Z]\\w*')