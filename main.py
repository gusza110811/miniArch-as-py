#!/usr/bin/python3
import parser, constructor, color
import os, sys
import argparse
import lark.exceptions

if os.path.islink(__file__):
    link = os.path.dirname(os.readlink(__file__))
    if link.startswith("/"):
        __dir__ = link
    else:
        __dir__ = os.path.join(os.path.dirname(__file__),link)
else:
    __dir__ = os.path.dirname(__file__)

class Assembler:
    def __init__(self,linkable=False):
        self.linkable = linkable
        self.parser = parser.Parser(linkable)
        self.constructor = constructor.Constructor()

    def main(self, code:str, filename="<main>"):
        codelns = code.split("\n")
        tree = None
        try:
            tree = self.parser.parse(code,filename)
        except lark.exceptions.UnexpectedCharacters as e:
            line = e.line -1 if e.line > 0 else -1
            col = e.column -1 if e.column > 0 else -1
            msg = "unexpected character at line"
            match e.char:
                case "{":
                    msg = "unmatched braces"
                case "\"":
                    msg = "unmatched quote"
                case "'":
                    msg = "unmatched quote"
                case "\n":
                    msg = "unexpected line break"
            print(color.fg.MAGENTA + f"{msg} {line+1} char {col+1}")
            print(color.RESET + "  "+codelns[line])
            print(color.fg.RED + "  "+" "*(col)+"^")
            return None
        except lark.exceptions.UnexpectedEOF as e:
            line = e.line -1 if e.line > 0 else -1
            col = e.column -1 if e.column > 0 else -1
            msg = "unexpected end of file"
            print(color.fg.MAGENTA + f"{msg}")
            print(color.RESET + "  "+codelns[line])
            print(color.fg.RED + "  "+" "*(col)+"^")
            print(color.fg.GRAY + f"There may be unmatched braces in the source")

        if tree is None:
            return

        #print("\n".join([repr(item) for item in tree.children]))
        try:
            out = self.constructor.main(tree,filename)
        except parser.ParseErr as e:
            print(f"File {filename} line {e.line+1} char {e.col}")
            print(color.fg.MAGENTA + e.msg.capitalize())
            print(color.RESET + "  " + codelns[e.line])
            print(color.fg.RED + "  " + " "*e.col+"^"*(e.colend-e.col if e.col < e.colend else 1))
            print(color.fg.GRAY + e.hint.capitalize())
            return None

        print("\n")
        return out

def test():
    test = open("main.asm").read()

    assembler = Assembler()
    out = assembler.main(test)
    with open("main.bin","wb") as file:
        file.write(out)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    argparser.add_argument("source",help="source assembly")
    argparser.add_argument("--output","-o",nargs="?",help="output file",default=None)
    argparser.add_argument("--linkable","-l",help="generate linkable object file instead of executable binary",action="store_true")
    argparser.add_argument("--symbols","-s",help="show all symbols in source assembly",action="store_true")

    args = argparser.parse_args()

    source:str = args.source
    dest = args.output

    if dest is None:
        dest = ".".join(source.split(".")[:-1]) + ".bin"

    if not os.path.isfile(source):
        sys.exit(f"")

    code = open(source).read()

    assembler = Assembler(args.linkable)
    out = assembler.main(code,source)
    if args.symbols:
        print("gr.id: name            = value    hex  unicode\n")
        for idx, context in enumerate(assembler.constructor.contexts):
            for idxj, (symbol, value) in enumerate(context.data.items()):
                print(f"{idx:02}.{idxj:02}: {symbol:<15} = {value:5}  {value:5X}  {ascii(chr(value))}")
    if not out is None:
        with open(dest,"wb") as file:
            file.write(out)
    else:
        sys.exit(1)
