from __future__ import annotations
from typing import TYPE_CHECKING
from context import Context
from parser import Transformer

class Constructor:
    def __init__(self):
        self.globals = Context()
        self.contexts = [self.globals]

    def main(self,ast:Transformer.start,filename="<main>") -> bytes:

        self.contexts.extend(ast.eval(self.globals))

        ast.collect(self.globals)
        #print([context.data for context in contexts])
        #print(self.globals.data)

        return ast.emit()
