class CField(object):
    def __init__(self, index,
             ftype,default=None, const=None,
             length=None, pointer=False,
             getter=None, setter=None, deleter=None):
        self.ftype = ftype
        self.default =  default
        self._setter=itemgetter
    def _field_getter(self,obj):
        if self.getter is None:
             index=obj._address[self.index]
             ftype=obj._data.ftypes[self.ftype]
             fsize=obj._data.fsizes[self.ftype]
             if self.length is None:
                result=obj._data[index:index+size].view(ftype)[0]
             else:
                result=obj._data[index:index+size*length].view(ftype)
    def _field_setter(self,obj,value):
        pass
    def check(self,value):
        if value is None:
            return self.default
        else:
            return value
    def __get__(self,obj,cls=None):
        if obj is None:
            return self
        else:
            return self._fieldgetter(obj)
    def __call__(self,funct):
        self.getter=funct
        return self


