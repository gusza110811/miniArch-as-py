class Context:
    def __init__(self,parent:"Context"=None):
        self.parent = parent
        self.root = parent is None
        self.pc = 0
        self.offset = 0
        self.data = {}
    
    def __repr__(self):
        return ("root" if self.root else repr(self.parent)) + f">Context({self.offset})"
    
    def inc_pc(self, n=1):
        if self.root:
            self.pc += n
        else:
            self.parent.inc_pc(n)
    
    def get_pc(self):
        if self.root:
            return self.pc
        else:
            return self.parent.get_pc()
    
    def add_label(self, name:str):
        self.set(name, self.get_pc()+self.offset)

    def get(self, key:str):
        try:
            return self.data[key]
        except KeyError:
            if not self.root:
                return self.parent.get(key)
            else:
                raise KeyError(f"{key} is not defined")
    
    def get_local(self, key:str):
        try:
            return self.data[key]
        except KeyError:
            return None
    
    def get_all(self):
        return self.data
    
    def set(self, key:str, value):
        self.data[key] = value
