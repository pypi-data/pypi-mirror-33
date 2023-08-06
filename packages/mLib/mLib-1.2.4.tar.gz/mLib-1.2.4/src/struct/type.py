import ctypes

class Structure(ctypes.Structure):

    _blacklist_ = []

    @classmethod
    def sizeof(self):
        return ctypes.sizeof(self)
    
    @classmethod
    def parse(self,data):
        return self.from_buffer_copy(data)

    @classmethod
    def new(self):
        return self.parse("\x00"*self.sizeof())
    
    def pack(self):
        return buffer(self)[:]
    
    def as_dict(self):
        ret = {}
        for field, _ in self._fields_:
            if field in self._blacklist_:
                continue
            
            value = getattr(self, field)
            if isinstance(value, Structure):
                ret[field] = value.as_dict()
            elif hasattr(value, "value"):
                ret[field] = value.value
            elif hasattr(value, "__getitem__"):
                ret[field] = value[:]
            else:
                ret[field] = value
        return ret
