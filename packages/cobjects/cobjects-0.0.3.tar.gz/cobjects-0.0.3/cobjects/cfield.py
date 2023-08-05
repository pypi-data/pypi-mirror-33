class CField(object):
    def __init__(self, index,
             ftype,default=None, const=None,
             length=None, pointer=False,
             alignment=None,
             setter=None):
        self.index = index
        self.ftype = ftype
        self.default =  default
        self.setter=setter
        self.length=length
        self.const=const
        self.pointer=pointer
        self.alignment=alignment
    def get_size(self,ftype,nargs):
        size=ftype.itemsize
        if self.length is not None:
            length=self.length
            if isinstance(length,str):
               length=eval(length,{},nargs)
            size*=length
        return size
    def _field_getter(self,obj):
        offset=obj._offsets[self.index]
        ftype=obj._ftypes[self.index]
        fsize=obj._fsizes[self.index]
        if self.length is None:
            return obj._buffer._data[offset:offset+fsize].view(ftype)[0]
        else:
            return obj._buffer._data[offset:offset+fsize].view(ftype)
    def _field_setter(self,obj,value):
        offset=obj._offsets[self.index]
        ftype=obj._ftypes[self.index]
        fsize=obj._fsizes[self.index]
        data=obj._buffer._data[offset:offset+fsize].view(ftype)
        if self.length is None:
           data[0]=value
        else:
            data[:]=value
        if self.setter is not None:
            self.setter(obj,value)
    def __get__(self,obj,cls=None):
        if obj is None:
            return self
        else:
            return self._field_getter(obj)
    def __set__(self,obj,value):
        return self._field_setter(obj,value)

