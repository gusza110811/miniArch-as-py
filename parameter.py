class BaseParameter:
    def __init__(self, value: int, length=1):
        self.value = value
        self.length= length
        "bytes, in powers of twos"
    
    def get(self,size:int):
        raise NotImplementedError(f"get() is not implemented for {self.__class__.__name__}")

class Immediate(BaseParameter):
    def __repr__(self):
        return f"Immediate({self.value})"
    
    def get(self,size=2,signed=False):
        if size == 0:
            return self.value.to_bytes((max(self.value.bit_length(),1)+7)//8, byteorder='little', signed=signed)
        else:
            return self.value.to_bytes(size, byteorder='little', signed=signed)

class Register(BaseParameter):
    def __init__(self, value, length=1):
        super().__init__(value)
        self.length = None
        self.default_size = 1
    def __repr__(self):
        return f"Register({self.value})"

class Dereference(BaseParameter):
    def __init__(self, value:int, length:int, base:int):
        super().__init__(value)
        self.length = length
        self.base = base
    def __repr__(self):
        return f"Dereference({self.base} : {self.value})"
    def get(self,size=2):
        return self.value.to_bytes(size, byteorder='little')

class IndirectDereference(BaseParameter):
    def __init__(self, segment, base, offset, length):
        self.segment = self.value = segment
        self.base = base
        self.offset = offset
        self.length = length
    def __repr__(self):
        return f"IndirectDereference({self.value}:{self.base} + {self.offset})"

