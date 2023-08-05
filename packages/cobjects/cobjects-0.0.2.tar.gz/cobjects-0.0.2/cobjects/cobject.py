from .cbuffer import CBuffer
from .cfield import CField


class CObject(object):
    def _fields(self):
        for nn,vv in self.__class__.__dict__.items():
            if isinstance(vv,CField):
                yield nn,vv
    def __init__(self,_buffer=None,**nargs):
        if _buffer is None:
            _buffer=CBuffer(template=CBuffer.python_types)
        self._buffer=_buffer
        self._address=self._buffer.next_object_address()
        self._offset=self._buffer.address_to_offset(self._address)
        self._offsets=[]
        self._ftypes=[]
        self._fsizes=[]
        self._fnames=[]
        curr_size=0
        curr_offset=self._offset
        curr_address=self._address
        curr_pointers=0
        pointer_list=[]
        for name,field in self._fields():
            ftype=self._buffer.resolve_type(field.ftype)
            size=field.get_size(ftype,nargs)
            if field.pointer is False:
                  if field.alignment is not None:
                      pad=field.alignment-curr_address%field.alignment
                      pad=pad%field.alignment
                      curr_size+=pad
                      curr_offset+=pad
                      curr_address+=pad
                  self._offsets.append(curr_offset)
                  self._ftypes.append(ftype)
                  self._fsizes.append(size)
                  self._fnames.append(name)
                  pad=(8-size%8)%8
                  curr_offset+=size+pad
                  curr_size+=size+pad
                  curr_address+=size+pad
            else: #is pointer
                self._offsets.append(curr_offset)
                pointers_list.append(curr_address)
                self._ftypes.append(ftype)
                self._fsizes.append(size)
                self._fnames.append(name)
                curr_offset+=8
                curr_size+=8
                curr_address+=8
        for name,field in self._fields():
            if field.pointer is True:
                  if field.alignment is not None:
                      pad=field.alignment-curr_address%field.alignment
                      pad=pad%field.alignment
                      curr_size+=pad
                      curr_offset+=pad
                      curr_address+=pad
                  offset=self._offsets[field.index]
                  data=obj._buffer._data[offset:offset+8].view('int64')
                  data[0]=curr_address
                  self._offsets[field.index]=curr_offset
        self._buffer.new_object(curr_size,self.__class__, pointer_list)
        for name,field in self._fields():
            setattr(self,name,nargs.get(name,field.default))

