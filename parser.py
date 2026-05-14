from __future__ import annotations
from typing import TYPE_CHECKING
from lark import Lark, Transformer as t
import lark
import os, sys
import typing
from context import Context
import parameter
import instruction
from dataclasses import dataclass

@dataclass
class ParseErr(Exception):
    msg:str
    line:int
    col:int
    colend:int
    hint:str=""

__dir__ = os.path.dirname(__file__)

class Transformer(t):
    def __init__(self, visit_tokens = True, allow_link=False):
        super().__init__(visit_tokens)
        self.allow_link = allow_link

    class Node:
        def __init__(self, value):pass
        
        def eval(self, context:Context=None):pass

        def __repr__(self):
            return f"<Invalid Node>"
        
        def get_first_token(self) -> lark.Token:
            return
        
        def get_last_token(self) -> lark.Token:
            return

    class Branch(Node):
        def __init__(self, value:list[Transformer.Node]):
            self.children = value
        
        def eval(self, context:Context):
            pass

        def get_first_token(self):
            tokens = [child.get_first_token() for child in self.children if child]
            tokens = list(filter(lambda c: isinstance(c,lark.Token), tokens))
            return tokens[0]
        
        def get_last_token(self):
            tokens = [child.get_last_token() for child in self.children if child]
            tokens = list(filter(lambda c: isinstance(c,lark.Token), tokens))
            return tokens[-1]
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self.children})"
    
    class Leaf(Node):
        def __init__(self, token):
            self.value = token.value
            self.token:lark.Token = token
        
        def eval(self):
            return self.value
        
        def get_first_token(self):
            return self.token
        
        def get_last_token(self):
            return self.token
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self.value})"

    class start(Branch):
        def __repr__(self):
            return " ".join([repr(value) for value in self.children])
        
        def eval(self, context):
            self.contexts:list[Context] = []
            for block in self.children:
                cont = block.eval(context)
                if isinstance(cont,Context):
                    self.contexts.append(cont)
            return self.contexts
        
        def collect(self, context:Context):
            prev_size = None
            size = 0
            PASS = 3 # pass count per iteration
            while prev_size != size:
                for idx in range(PASS):
                    context.pc = 0
                    for block in self.children:
                        block.collect(context)
                prev_size = size
                size = context.pc
        
        def emit(self):
            out = []

            for block in self.children:
                out.append(block.emit())
            
            return b"".join(out)

    def transform(self, tree) -> start:
        return super().transform(tree)
    
    class codegen(Branch):
        def __init__(self, value):
            super().__init__(value)
            if self.children:
                self.value = self.children[0]
            else:
                self.value = None

        def eval(self, context:Context):
            pass

        def collect(self, context:Context):
            pass
        
        def emit(self):
            return b""

    class scope(codegen):

        def eval(self, context:Context):
            self.context = Context(context)

            for child in self.children:
                child.eval(self.context)
            return self.context
        def collect(self, context):
            self.context.offset = context.offset
            for item in self.children:
                item.collect(self.context)
        
        def emit(self):
            out = b""
            for item in self.children:
                out += item.emit()
            return out
        
        def __repr__(self):
            return "{\n  " + ";\n  ".join([repr(value) for value in self.children]) + "\n}"

    class datagen(codegen):pass

    class code_block(codegen):

        def __init__(self, value):
            super().__init__(value)
            self.name = self.children[0]
            self.scope:Transformer.scope = self.children[1]
        def eval(self, context):
            if self.name:
                self.name = self.name.eval()
                context.set(self.name,0x7FFF)
            return self.scope.eval(context)
        
        def collect(self,context):
            if self.name:
                context.add_label(self.name)
            self.scope.collect(context)

        def emit(self):
            return self.scope.emit()

        def __repr__(self):
            return "code " + repr(self.name) + repr(self.scope)

    class instruction(codegen):
        def __init__(self, value):
            super().__init__(value)
            self.command = self.children[0]
            self.args:list[Transformer.Parameter] = self.children[1:]

        def eval(self, context):
            self.commandname = self.command.eval()
        def collect(self, context):
            self.position = context.get_pc() + context.offset
            processed_args = []

            for child in self.args:
                processed_args.append(child.eval(context))
            self.out = instruction.Instruction.from_str(self.commandname, processed_args).get(self.position)
            if isinstance(self.out, instruction.Err):
                if self.out.pos == -1:
                    err_begin = self.command.get_first_token()
                    err_end = self.command.get_last_token()
                else:
                    err_begin = self.args[self.out.pos].get_first_token()
                    err_end = self.args[self.out.pos].get_last_token()
                raise ParseErr(self.out.msg, err_begin.line-1, err_begin.column-1,err_end.end_column-1,self.out.hint)
            context.inc_pc(len(self.out))

        def emit(self):
            return self.out

        def __repr__(self):
            return f"{self.command}({", ".join([repr(value) for value in self.args])})"

    class text(datagen):
        value:Transformer.STRING
        def __repr__(self):
            return f".ascii {self.children[0]}"
        def eval(self, context):
            self.text = self.value.eval()
        def collect(self, context):
            context.inc_pc(len(self.text))
        def emit(self):
            return self.text.encode('utf-8')
    
    class text_nulterm(text):
        def __repr__(self):
            return f".asciiz {self.children[0]}"
        def eval(self, context):
            super().eval(context)
            self.text = self.text + "\0"
        def collect(self, context):
            super().collect(context)
        def emit(self):
            return self.text.encode('utf-8')
    
    class bytes(datagen):
        children:list[Transformer.expr]
        def __repr__(self):
            return f".bytes {self.children}"
        def collect(self, context):
            self.out = bytearray()
            for child in self.children:
                value = child.eval(context)
                if value > 255:
                    raise ParseErr(f"{value} does not fit in 8 bit",
                        child.get_first_token().line,
                        child.get_first_token().column,
                        child.get_last_token().end_column
                    )
                elif value < 0:
                    raise ParseErr(f"signed number not supported",
                        child.get_first_token().line,
                        child.get_first_token().column,
                        child.get_last_token().end_column
                    )
                self.out.append(value)
                context.inc_pc(1)
            return self.out
        def emit(self):
            return self.out

    class byte(datagen):
        value:Transformer.expr
        def __repr__(self):
            return f".byte {self.value}"
        def collect(self, context):
            context.inc_pc(1)
            if self.value:
                self.out = self.value.eval(context).to_bytes(1)
            else:
                self.out = bytes(1)
        def emit(self):
            return self.out
    class word(datagen):
        def __repr__(self):
            return f".word {self.value}"
        def collect(self, context):
            context.inc_pc(2)
            if self.value:
                self.out = self.value.eval(context).to_bytes(2, byteorder='little')
            else:
                self.out = bytes(2)
        def emit(self):
            return self.out
    class double(datagen):
        def __repr__(self):
            return f".double {self.value}"
        def collect(self, context):
            context.inc_pc(4)
            if self.value:
                self.out = self.value.eval(context).to_bytes(4, byteorder='little')
            else:
                self.out = bytes(4)
        def emit(self):
            return self.out
    class quad(datagen):
        def __repr__(self):
            return f".quad {self.value}"
        def collect(self, context):
            context.inc_pc(8)
            if self.value:
                self.out = self.value.eval(context).to_bytes(8, byteorder='little')
            else:
                self.out = bytes(8)
        def emit(self):
            return self.out

    class zero(datagen):
        def collect(self, context):
            if self.value:
                context.inc_pc(self.children[0].eval(context))
                self.out = b"\0" * self.children[0].eval(context)
            else:
                context.inc_pc(1)
                self.out = b'\0'
        def emit(self):
            return self.out

    class org(datagen):
        def collect(self, context):
            length = self.children[0].eval(context) - context.get_pc() + context.offset
            context.inc_pc(length)
            self.out = b"\0" * length
        def emit(self):
            return self.out
    
    class offset(datagen):
        def collect(self, context):
            offset = self.children[0].eval(context)
            context.offset = offset

    class Parameter(Branch):pass

    class immediate(Parameter):
        def __repr__(self):
            return f"immediate {self.children[0]}"
        def dry_eval(self):
            return parameter.Immediate(0)
        def eval(self, context):
            return parameter.Immediate(self.children[0].eval(context))
    class direct_addr(Parameter):
        def __init__(self, value):
            super().__init__(value)
            self.size:Transformer.IDENTIFIER = value[0]
            self.base:Transformer.SEGMENT = value[1]
            self.addr:Transformer.expr = value[2]
            if self.size:
                sizechar = self.size.eval()
                if sizechar not in ["b","w"]:
                    tok = self.size.get_first_token()
                    raise ParseErr("invalid size",tok.line-1,tok.col-1,tok.end_column-1,"valid sizes are b and w")
                self.size = ["b","w"].index(sizechar)
            else:
                self.size = None
        def __repr__(self):
            return f"deref {self.base}:{self.addr}"
        def dry_eval(self):
            return parameter.Dereference(0,self.size,1)
        def eval(self, context):
            addr = self.addr.eval(context)
            if self.base:
                base = self.base.eval()
            else:
                base = 1
            return parameter.Dereference(addr,self.size,base)
        def get_first_token(self):
            if self.children[0]:
                return self.children[0].get_first_token()
            else:
                return self.children[1].get_first_token()
    class indirect_addr(Parameter):
        def __init__(self, value):
            super().__init__(value)
            self.size:Transformer.ADDR_SIZE|None = value[0]
            self.segment:Transformer.SEGMENT = value[1]
            self.base:Transformer.BASE = value[2]
            self.sign:Transformer.SIGN = value[3]
            self.offset:Transformer.expr = value[4]
        def __repr__(self):
            return f"deref {self.segment}:{self.base} {"+" if self.sign == 0 else "-"} {self.offset}"
        def dry_eval(self):
            return parameter.IndirectDereference(0,0)
        def eval(self, context):
            if self.size:
                size = ["b","w"].index(self.size.eval())
            else:
                size = None
            base = self.base.eval()
            if self.offset:
                offset = self.offset.eval(context) * self.sign.eval()
            else:
                offset = 0
            if self.segment:
                segment = self.segment.eval()
            elif base == 0:
                segment = 1
            else:
                segment = 2
            return parameter.IndirectDereference(segment,base,offset,size)
    
    class register(Parameter):
        def eval(self, context):
            name = self.children[0].eval()
            registers = ['ax','bx','cx','dx',
                'cs','ds','ss','es',
                'sp','bp','.','.',
                'ah','bh','ch','dh'
            ]

            if name in registers:
                return parameter.Register(registers.index(name.lower()))

    class constantdef(codegen):
        def __init__(self, value):
            super().__init__(value)
            self.name:Transformer.IDENTIFIER = self.children[0]
            self.val:Transformer.expr = self.children[1]
        def __repr__(self):
            return f"{self.name} = {self.val}"
        
        def eval(self, context):
            name = self.name.eval()
            context.set(name,0)

        def collect(self, context):
            name = self.name.eval()

            context.set(name,self.val.eval(context))

    class labeldef(codegen):
        def __init__(self, value):
            super().__init__(value)
            self.name = self.children[0]

        def __repr__(self):
            return f"label {self.name}"
        
        def eval(self, context):
            self.name = self.name.eval()
            context.set(self.name,0x7FFF)
        
        def collect(self, context):
            context.add_label(self.name)
    
    class export(codegen):
        def __init__(self, value):
            super().__init__(value)

            self.source:Transformer.Leaf = self.children[0]
            self.dest:Transformer.Leaf = self.children[1]
        
        def eval(self, context):
            self.source = self.source.eval()
            if self.dest:
                self.dest = self.dest.eval()
            else:
                self.dest = self.source
            context.parent.set(self.dest,0x7fff)

        def collect(self, context):
            context.parent.set(self.dest,context.get(self.source))
    
    class exportdef(codegen):
        def __init__(self, value):
            super().__init__(value)

            self.source:Transformer.constantdef|Transformer.labeldef|Transformer.code_block = self.children[0]
        
        def eval(self, context):
            out = self.source.eval(context)
            self.name = self.source.name
            context.parent.set(self.name,0x7fff)
            return out

        def collect(self, context):
            self.source.collect(context)
            context.parent.set(self.name,context.get(self.name))
        
        def emit(self):
            return self.source.emit()

    class expr(Branch):
        def __init__(self, value):
            if len(value) == 2:
                self.lhs = value[0]
                self.rhs = value[1]
            else:
                self.rhs = value[0]
        def eval(self,context) -> int:pass

    class or_op(expr):
        def __repr__(self):
            return f"({self.lhs} | {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) | self.rhs.eval(context)
    class xor_op(expr):
        def __repr__(self):
            return f"({self.lhs} ^ {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) ^ self.rhs.eval(context)
    class and_op(expr):
        def __repr__(self):
            return f"({self.lhs} & {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) & self.rhs.eval(context)
    class not_op(expr):
        def __repr__(self):
            return f"(~ {self.rhs})"
        def eval(self, context):
            return ~self.rhs.eval(context)
    
    class shiftr(expr):
        def __repr__(self):
            return f"({self.lhs} >> {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) >> self.rhs.eval(context)
    class shiftl(expr):
        def __repr__(self):
            return f"({self.lhs} << {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) << self.rhs.eval(context)
    
    class add(expr):
        def __repr__(self):
            return f"({self.lhs} + {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) + self.rhs.eval(context)
    class sub(expr):
        def __repr__(self):
            return f"({self.lhs} - {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) - self.rhs.eval(context)
    
    class mul(expr):
        def __repr__(self):
            return f"({self.lhs} * {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) * self.rhs.eval(context)
    class div(expr):
        def __repr__(self):
            return f"({self.lhs} / {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) // self.rhs.eval(context)
    
    class unary_sub(expr):
        def __repr__(self):
            return f"(- {self.rhs})"
        def eval(self, context):
            return - self.rhs.eval(context)

    class literal(Branch):
        def __init__(self, value:Transformer.Leaf):
            super().__init__(value)
            self.val = self.children[0]
        def __repr__(self):
            return f"lit {self.val}"
        def eval(self, context):
            return self.val.eval()
    
    class symbol(Branch):
        def __repr__(self):
            return f"symbol {self.children[0]}"
        def eval(self, context):
            name = self.children[0].eval()

            try:
                return context.get(name)
            except KeyError:
                raise ParseErr(f"undefined symbol `{name}`", self.children[0].get_first_token().line-1, self.children[0].get_first_token().column-1, self.children[0].get_last_token().end_column-1)
    
    class newline(codegen):
        def __repr__(self):
            return "\\n"

    class IDENTIFIER(Leaf):
        def __repr__(self):
            return f"identifer {self.value}"
    
    class INST(Leaf):
        def __repr__(self):
            return f"inst {self.value}"

    class REGISTER(Leaf):
        def eval(self):
            return self.value.lower()
    
    class SIGN(Leaf):
        def eval(self):
            return 1 if self.value == "+" else -1
    
    class SEGMENT(Leaf):
        def eval(self):
            return ['cs','ds','ss','es'].index(self.value.lower())

    class BASE(Leaf):
        def eval(self):
            return ['bx','bp'].index(self.value.lower())

    class STRING(Leaf):
        def __init__(self,value:str):
            super().__init__(value)
            self.value = value[1:-1]
        def eval(self):
            self.value = self.value.replace(r"\n","\n")\
                .replace(r"\r","\r")\
                .replace(r"\t","\t")\
                .replace(r"\\","\\")\
                .replace(r"\b","\b")\
                .replace(r"\"","\"")
            return self.value
    class CHAR(STRING):
        def eval(self):
            super().eval()
            if len(self.value) != 1:
                raise ValueError("CHAR must be a single character")
            value = ord(self.value)
            return value

    class Number(Leaf):
        def __init__(self, token:lark.Token):
            token.value = token.value.replace("_","")
            super().__init__(token)

    class DECIMAL(Leaf):
        def eval(self):
            return int(self.value)
    class BINARY(Leaf):
        def eval(self):
            return int(self.value[2:],base=2)
    class OCTAL(Leaf):
        def eval(self):
            return int(self.value[2:],base=8)
    class HEX(Leaf):
        def eval(self):
            return int(self.value[2:],base=16)
    
    class statement(codegen):
        def __repr__(self):
            return ""
    class code_statement(statement):pass


class Parser:
    def __init__(self,linkable=False):
        self.grammar = open(os.path.join(__dir__,"grammar.lark")).read()
        self.parser = Lark(
            self.grammar,
            parser="lalr",
        )
        self.transformer = Transformer(allow_link=linkable)
    def parse(self, code:str, filename="<main>"):
        transformer = self.transformer
        parser = self.parser

        parsedTree = parser.parse(code)

        tree = transformer.transform(parsedTree)

        return tree
