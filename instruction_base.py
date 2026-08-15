from parameter import *

class Err:
    def __init__(self,
            msg:str,
            pos:int,
            hint:str="",):
        self.msg = msg
        self.pos = pos
        self.hint = hint

        if msg == "not implemented":
            self.hint += "\n somebody forgot to implement this specific usage of the instruction, please contact target maintainer"
    
    def __repr__(self):
        return f"{self.msg} : {self.pos} ; {self.hint}"

class Instruction:
    def __init__(self,args:list[BaseParameter]):
        self.args = args
    def __repr__(self):
        return f"{self.__class__.__name__}(args={self.args})"
    def get(self, pc:int, size=2) -> bytes|Err:
        raise NotImplementedError(f"get() not implemented for {self.__class__.__name__}")

    @classmethod
    def from_str(cls, name:str, args:list[BaseParameter]) -> "Instruction":
        if name not in map:
            raise SyntaxError(f"unknown instruction '{name}'")
        return map[name](args)
    
    def check_type(self, index:int, expect:BaseParameter|list[BaseParameter]):
        if not isinstance(expect,list):
            if isinstance(self.args[index],expect):
                return True
            else:
                return False
        else:
            for exp in expect:
                if isinstance(self.args[index],exp):
                    return True
            return False
    def check_count(self, expect:int):
        if expect == len(self.args):
            return 0
        if expect > len(self.args):
            return 1
        if expect < len(self.args):
            return -1

map = {}

def register(name:str,cls:"Instruction"):
    map[name] = cls