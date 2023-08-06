''' Standalone abstract syntax tree wrapper for a root node '''

from lnac.nodes import Node

class Ast():
    def __init__(self, root):
        self.root = root

    def __str__(self):
        return str(self.root)