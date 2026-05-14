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
            self.hint += "\ncome back to writing the assembler you donkey"
    
    def __repr__(self):
        return f"{self.msg} : {self.pos} ; {self.hint}"

map = {}

def register(name:str,cls:"Instruction"):
    map[name] = cls

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

class Mov(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")

        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        srcL = src.length
        destL = dest.length
        length = None

        datalen = list("bwdq")

        if srcL != None and destL != None and srcL != destL and srcT != Register and destT != Register:
            return Err("conflicting data length",0,f"{datalen.index(destL)} vs {datalen.index(srcL)}")

        length = destL if not destL is None else srcL

        if length is None:
            if destT == Register:
                length = dest.default_size
            elif srcT == Register:
                length = src.default_size

        if length is None:
            return Err("ambiguous data length",0)

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot save to immediate value")

        if destT == Register:
            if srcT == Register:
                out.append(0x10)
                out.append((destval<<4)|srcval)
            elif srcT == Immediate:
                if srcval < 16:
                    out.append(0x11)
                    out.append((destval<<4)|srcval)
                elif srcval < 256:
                    out.append(0x12)
                    out.append(destval<<4)
                    out.append(srcval)
                elif srcval < 65536:
                    out.append(0x13)
                    out.append(destval<<4)
                    out.extend(srcval.to_bytes(2,"little"))
                else:
                    return Err("Immediate value too large",1,f"{src.value} does not fit in 16 bit")
            elif srcT == Dereference:
                if length == 0:
                    out.append(0x19)
                else:
                    out.append(0x1B)
                base = src.base
                offset = src.value
                target = dest.value
                descriptor = (target << 4) | (base+4)
                out.append(descriptor)
                out.extend(offset.to_bytes(2,'little'))
            elif srcT == IndirectDereference:
                base = src.base
                segment = src.segment
                offset:int = src.offset
                if length == 0:
                    out.append(0x19)
                else:
                    out.append(0x1B)
                target = dest.value
                if base == 0 and offset == 0:
                    offset = None
                if not offset is None:
                    descriptor = (target << 4) | (segment + 8 + (4 * base))
                    out.append(descriptor)
                    out.extend(offset.to_bytes(2,'little',signed=True))
                else:
                    descriptor = (target << 4) | segment
                    out.append(descriptor)

        elif destT == Dereference:
            if srcT == Register:
                if length == 0:
                    out.append(0x18)
                else:
                    out.append(0x1A)
                base = dest.base
                offset = dest.value
                source = src.value
                descriptor = ((base+4) << 4)|source
                out.append(descriptor)
                out.extend(offset.to_bytes(2,'little'))
            elif srcT == Dereference or srcT == IndirectDereference:
                return Err("unsupported operand",1,"copy directly from memory to memory")
            elif srcT == Immediate:
                return Err("unsupported operand",1,"cannot store immediate value directly to memory")
        elif destT == IndirectDereference:
            if srcT == Register:
                base = dest.value
                offset:int = dest.offset
                if length == 0:
                    out.append(0x18)
                else:
                    out.append(0x1A)
                source = src.value
                if offset:
                    descriptor = ((base+8) << 4) | source
                    out.append(descriptor)
                    out.extend(offset.to_bytes(2,'little',signed=True))
                else:
                    descriptor = (base << 4) | source
                    out.append(descriptor)
            elif srcT == Dereference or srcT == IndirectDereference:
                return Err("unsupported operand",1,"cannot copy directly from memory to memory")
            elif srcT == Immediate:
                return Err("unsupported operand",1,"cannot store immediate value directly to memory")

        if out:
            return bytes(out)
        
        return Err("not implemented",0,f"{destT} and {srcT} pair is not implemented")
register("mov",Mov)

class Lea(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")

        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        srcL = src.length
        destL = dest.length
        length = None

        datalen = list("bwdq")

        if srcL != None and destL != None and srcL != destL and srcT != Register and destT != Register:
            return Err("conflicting data length",0,f"{datalen.index(destL)} vs {datalen.index(srcL)}")

        length = destL if not destL is None else srcL

        if length is None:
            if destT == Register:
                length = dest.default_size
            elif srcT == Register:
                length = src.default_size

        if length is None:
            return Err("ambiguous data length",0)

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot save to immediate value")

        if destT == Register:
            if srcT == Dereference:
                out.append(0x1E)
                base = src.base
                offset = src.value
                target = dest.value
                descriptor = (target << 4) | (base+4)
                out.append(descriptor)
                out.extend(offset.to_bytes(2,'little'))
            elif srcT == IndirectDereference:
                base = src.base
                segment = src.segment
                offset:int = src.offset
                out.append(0x1E)
                target = dest.value
                if base == 0 and offset == 0:
                    offset = None
                if not offset is None:
                    descriptor = (target << 4) | (segment + 8 + (4 * base))
                    out.append(descriptor)
                    out.extend(offset.to_bytes(2,'little',signed=True))
                else:
                    descriptor = (target << 4) | segment
                    out.append(descriptor)
            else:
                return Err("invalid operand",1,"source must be an address")
        else:
            return Err("invalid operand",0,"dest must be a register")

        if out:
            return bytes(out)

        return Err("not implemented",0,f"{destT} and {srcT} pair is not implemented")
register("lea",Lea)

class Add(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot add to immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly to memory")
        if srcT == Dereference or srcT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly from memory")
        
        dest:Register
        if srcT == Register:
            out.append(0x20)
            out.append((destval<<4) | (srcval))
        elif srcT == Immediate:
            if srcval < 16:
                out.append(0x21)
                out.append((destval<<4) | (srcval))
            elif srcval < 256:
                out.append(0x22)
                out.append(destval<<4)
                out.append(srcval)
            elif srcval < 65536:
                out.append(0x23)
                out.append(destval<<4)
                out.extend(srcval.to_bytes(2,"little"))
            else:
                return Err("Immediate value too large",1,f"{src.value} does not fit in 16 bit")
        
        return bytes(out)
register("add",Add)

class Sub(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot add to immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly to memory")
        if srcT == Dereference or srcT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly from memory")
        
        dest:Register
        if srcT == Register:
            out.append(0x24)
            out.append((destval<<4) | (srcval))
        elif srcT == Immediate:
            if srcval < 16:
                out.append(0x25)
                out.append((destval<<4) | (srcval))
            elif srcval < 256:
                out.append(0x26)
                out.append(destval<<4)
                out.append(srcval)
            elif srcval < 65536:
                out.append(0x27)
                out.append(destval<<4)
                out.extend(srcval.to_bytes(2,"little"))
            else:
                return Err("Immediate value too large",1,f"{src.value} does not fit in 16 bit")
        
        return bytes(out)
register("sub",Sub)

class Cmp(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot add to immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly to memory")
        if srcT == Dereference or srcT == IndirectDereference:
            return Err("unsupported operand",0,"cannot add directly from memory")
        
        dest:Register
        if srcT == Register:
            out.append(0x28)
            out.append((destval<<4) | (srcval))
        elif srcT == Immediate:
            if srcval < 16:
                out.append(0x29)
                out.append((destval<<4) | (srcval))
            elif srcval < 256:
                out.append(0x2A)
                out.append(destval<<4)
                out.append(srcval)
            elif srcval < 65536:
                out.append(0x2B)
                out.append(destval<<4)
                out.extend(srcval.to_bytes(2,"little"))
            else:
                return Err("Immediate value too large",1,f"{src.value} does not fit in 16 bit")
        
        return bytes(out)
register("cmp",Cmp)

class Neg(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(1)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 1, got {len(self.args)}")
        dest = self.args[0]
        destval = dest.value
        destT = dest.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot negate immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot negate directly to memory")
        
        dest:Register
        out.append(0x2C)
        out.append(destval<<4)
        
        return bytes(out)
register("neg",Neg)

class And(Instruction):
    op=0x30

    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot bitwise to immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot bitwise directly to memory")
        if srcT == Dereference or srcT == IndirectDereference:
            return Err("unsupported operand",0,"cannot bitwise directly from memory")
        
        dest:Register
        if srcT == Register:
            out.append(self.op)
            out.append((destval<<4) | (srcval))
        elif srcT == Immediate:
            if srcval < 65536:
                out.append(self.op+1)
                out.append(destval<<4)
                out.extend(srcval.to_bytes(2,"little"))
            else:
                return Err("Immediate value too large",1,f"{src.value} does not fit in 16 bit")
        
        return bytes(out)
register("and",And)
class Or(And): op=0x32
register("or",Or)
class Xor(And): op=0x34
register("xor",Xor)

class Shr(Instruction):
    op=0x36
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__
        if destT == Immediate:
            return Err("unsupported operand",0,"cannot and to immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot and directly to memory")
        if srcT == Dereference or srcT == IndirectDereference:
            return Err("unsupported operand",0,"cannot and directly from memory")
        
        out = bytearray()

        dest:Register
        if srcT == Register:
            out.append(self.op)
            out.append((destval<<4) | (srcval))
        elif srcT == Immediate:
            if srcval < 16:
                out.append(self.op+1)
                out.append((destval<<4)|srcval)
            else:
                return Err("Immediate value too large",1,f"{src.value} does not fit in 4 bit")

        return out
register("shr",Shr)
class Shl(Shr):op=0x38
register("shl",Shl)

class Not(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(1)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 1, got {len(self.args)}")
        dest = self.args[0]
        destval = dest.value
        destT = dest.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot bitwise immediate value")
        if destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot bitwise directly to memory")
        
        dest:Register
        out.append(0x3A)
        out.append(destval<<4)
        
        return bytes(out)
register("not",Not)

class Out(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        if srcT != Register:
            return Err("unsupported operand",0,"port address must be in a register")
        if destT != Register:
            return Err("unsupported operand",0,"destination must be a register")

        return bytes([
            0x1d, (destval << 4) | srcval
        ])
register("out",Out)

class Inp(Instruction):
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        dest = self.args[0]
        src = self.args[1]
        destval = dest.value
        srcval = src.value
        destT = dest.__class__
        srcT = src.__class__

        if destT != Register:
            return Err("unsupported operand",0,"port address must be in a register")
        if srcT != Register:
            return Err("unsupported operand",0,"source must be a register")

        return bytes([
            0x1c, (destval << 4) | srcval
        ])
register("inp",Inp)
register("in",Inp)

class Jump_generic(Instruction):
    op = 0x40
    condition = 0xf

    def get(self, pc, size=2):
        countcmp = self.check_count(1)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 1, got {len(self.args)}")
        addr = self.args[0]
        addrval = addr.value
        addrT = addr.__class__

        out = bytearray([self.op])

        if addrT == Register or addrT == IndirectDereference:
            return Err("unsupported operand",0,"target must be an immediate value or a dereference for absolute jump")
        
        if addrT == Immediate:
            relAddr = addrval-pc
            if -128 <= relAddr <= 127:
                out.append(self.condition)
                out.extend(relAddr.to_bytes(1,signed=True))
            elif -32768 <= relAddr <= 32767:
                out.append(0x10 | self.condition)
                out.extend(relAddr.to_bytes(2,byteorder='little',signed=True))
            else:
                return Err("immediate value too large",0,f"{relAddr} ({addr} relative to {pc}) does not fit in signed 16 bit")
        elif addrT == Dereference:
            if addrval > 65535:
                return Err("immediate value too large",0,f"{addr} does not fit in 16 bit")

            out.append(0x20 | self.condition)
            out.extend(addrval.to_bytes(2,byteorder='little'))
        return out
register("jmp",Jump_generic)
class Jz(Jump_generic): condition = 0x0
register("jz", Jz)
register("je", Jz)
class Jnz(Jump_generic): condition = 0x1
register("jnz", Jnz)
register("jne", Jnz)
class Jc(Jump_generic): condition = 0x2
register("jc", Jc)
class Jnc(Jump_generic): condition = 0x3
register("jnc", Jnc)
class Jn(Jump_generic): condition = 0x4
register("jn", Jn)
class Jp(Jump_generic): condition = 0x5
register("jp", Jp)
register("jnn", Jp)

class Call_generic(Jump_generic): op = 0x41
register("call",Call_generic)
class Bz(Jump_generic): condition = 0x0
register("bz", Bz)
register("be", Bz)
class Bnz(Jump_generic): condition = 0x1
register("bnz", Bnz)
register("bne", Bnz)
class Bc(Jump_generic): condition = 0x2
register("bc", Bc)
class Bnc(Jump_generic): condition = 0x3
register("bnc", Bnc)
class Bn(Jump_generic): condition = 0x4
register("bn", Bn)
class Bp(Jump_generic): condition = 0x5
register("bp", Bp)
register("bnn", Bp)

class Ret(Instruction):
    def get(self, pc, size=2):
        if self.check_count(0):
            return Err("too many parameter",0,"`ret` does not take any parameter")
        return b"\x42"
register("ret",Ret)

class Jmpf(Instruction):
    op = 0x48
    def get(self, pc, size=2):
        countcmp = self.check_count(2)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 2, got {len(self.args)}")
        if not self.check_type(0,Immediate):
            return Err("unsupported operand",0,"target segment must be an immediate value")
        if not self.check_type(1,Immediate):
            return Err("unsupported operand",1,"target must be an immediate value")
        
        out = bytearray([self.op])
        
        segval = self.args[0].value
        targetval = self.args[1].value

        if segval > 65535:
            return Err("immediate value too large",0,f"{segval} does not fit in 16 bit")
        if targetval > 65535:
            return Err("immediate value too large",1,f"{targetval} does not fit in 16 bit")

        out.extend(segval.to_bytes(2,'little'))
        out.extend(targetval.to_bytes(2,'little'))
        return out
register("jmpf",Jmpf)

class Callf(Jmpf): op=0x49
register("callf",Callf)

class Retf(Instruction):
    def get(self, pc, size=2):
        if self.check_count(0):
            return Err("too many parameter",0,"`retf` does not take any parameter")
        return b"\x4A"
register("retf",Retf)

class Int(Instruction):
    op = 0x4B
    def get(self, pc, size=2):
        countcmp = self.check_count(1)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 1, got {len(self.args)}")
        if not self.check_type(0,Immediate):
            return Err("unsupported operand",0,"target segment must be an immediate value")

        out = bytearray([self.op])
        
        val = self.args[0].value

        if val > 255:
            return Err("immediate value too large",0,f"{val} does not fit in 16 bit")

        out.append(val)
        return out
register("int",Int)

class Push(Instruction):
    op=0x50
    def get(self, pc, size=2):
        countcmp = self.check_count(1)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 1, got {len(self.args)}")
        src = self.args[0]
        srcval = src.value
        srcT = src.__class__

        out = bytearray()

        if srcT == Immediate:
            return Err("unsupported operand",0,"cannot push immediate value")
        elif srcT == Register:
            out.append(self.op)
            out.append(srcval)
        elif srcT == Dereference or srcT == IndirectDereference:
            return Err("unsupported operand",0,"cannot push directly from memory")
        
        return bytes(out)
register("push",Push)
register("pushw",Push)

class Pushb(Push):op=0x51
register("pushb",Pushb)

class Pop(Instruction):
    op=0x52
    def get(self, pc, size=2):
        countcmp = self.check_count(1)
        if countcmp:
            return Err(("not enough" if countcmp == 1 else "too many") + " parameter",-1,f"expected 1, got {len(self.args)}")
        dest = self.args[0]
        destval = dest.value
        destT = dest.__class__

        out = bytearray()

        if destT == Immediate:
            return Err("unsupported operand",0,"cannot pop to immediate value")
        elif destT == Register:
            out.append(self.op)
            out.append(destval<<4)
        elif destT == Dereference or destT == IndirectDereference:
            return Err("unsupported operand",0,"cannot pop directly to memory")
        
        return bytes(out)
register("pop",Pop)
register("popw",Pop)

class Popb(Pop):op=0x53
register("popb",Popb)

class Pusha(Instruction):
    def get(self, pc, size=2):
        if self.check_count(0):
            return Err("too many parameter",0,"`pusha` does not take any parameter")
        return b"\x5E"
register("pusha",Pusha)

class Popa(Instruction):
    def get(self, pc, size=2):
        if self.check_count(0):
            return Err("too many parameter",0,"`popa` does not take any parameter")
        return b"\x5F"
register("popa",Popa)

class Flag_generic(Instruction):
    op:int
    def get(self, pc, size=2):
        if self.check_count(0):
            return Err("too many parameter",0,f"`{self.__class__.__name__.lower()}` does not take any parameter")
        return self.op.to_bytes()

class Clz(Flag_generic):op=0x60
register("clz",Clz)
class Clc(Flag_generic):op=0x61
register("clc",Clc)
class Cln(Flag_generic):op=0x62
register("cln",Cln)
class Clo(Flag_generic):op=0x63
register("clo",Clo)
class Cli(Flag_generic):op=0x64
register("cli",Cli)
class Cla(Flag_generic):op=0x67
register("cla",Cla)

class Stz(Flag_generic):op=0x68
register("stz",Stz)
class Stc(Flag_generic):op=0x69
register("stc",Stc)
class Stn(Flag_generic):op=0x6A
register("stn",Stn)
class Sto(Flag_generic):op=0x6B
register("sto",Sto)
class Sti(Flag_generic):op=0x6C
register("sti",Sti)
class Sta(Flag_generic):op=0x6F
register("sta",Sta)

class Halt(Instruction):
    def get(self, pc, size=2):
        if self.check_count(0):
            return Err("too many parameter",0,"`halt` does not take any parameter")
        return b"\xff"
register("halt",Halt)
register("hlt",Halt)
