from .cbuffer import CBuffer
from .cfield import CField


class CObject(object):
    def _fields(self):
        for nn,vv in self.__class__.__dict__.items():
            if isinstance(vv,CField):
                yield nn,vv
    def __init__(self,cbuffer=None,offset=None,**nargs):
        if cbuffer is None:
            cbuffer=CBuffer(template=CBuffer.c_types)
        self._buffer=cbuffer
        if offset is None:
            self._build_from_args(nargs)
        else:
            raise(NotImplemented)
    def _build_from_args(self,nargs):
        self._offsets=[]
        self._ftypes=[]
        self._fsizes=[]
        self._fnames=[]
        curr_size=0
        curr_offset=0
        curr_pointers=0
        pointer_list=[]
        #first pass for normal fields
        for name,field in self._fields():
            ftype=self._buffer.resolve_type(field.ftype)
            size=field.get_size(ftype,nargs)
            if field.pointer is False:
                  if field.alignment is not None:
                      pad=field.alignment-curr_offset%field.alignment
                      pad=pad%field.alignment
                      curr_size+=pad
                      curr_offset+=pad
                  self._offsets.append(curr_offset)
                  self._ftypes.append(ftype)
                  self._fsizes.append(size)
                  self._fnames.append(name)
                  pad=(8-size%8)%8
                  curr_offset+=size+pad
                  curr_size+=size+pad
            else: #is pointer
                self._offsets.append(curr_offset)
                pointer_list.append(curr_offset)
                self._ftypes.append(ftype)
                self._fsizes.append(size)
                self._fnames.append(name)
                curr_offset+=8
                curr_size+=8
        #second pass for pointer fields
        pointer_data=[]
        for name,field in self._fields():
            if field.pointer is True:
                  if field.alignment is not None:
                      pad=field.alignment-curr_offset%field.alignment
                      pad=pad%field.alignment
                      curr_size+=pad
                      curr_offset+=pad
                  offset=self._offsets[field.index]
                  pointer_data.append([offset,curr_offset])
                  self._offsets[field.index]=curr_offset
                  size=self._fsizes[field.index]
                  curr_size+=size
                  curr_offset+=size
        #allocate data
        self._address = self._buffer.new_object(curr_size,
                                                self.__class__,
                                                pointer_list)
        self._offset=self._buffer.address_to_offset(self._address)
        for index in range(len(self._offsets)):
            self._offsets[index]+=self._offset
        #store pointer data
        for offset, address in pointer_data:
            doffset=offset+self._offset
            data=self._buffer._data[doffset:doffset+8].view('int64')
            data[0]=self._address+address
        #store data in fields
        for name,field in self._fields():
            setattr(self,name,nargs.get(name,field.default))
    def __repr__(self):
        out=[f"<{self.__class__.__name__} at {self._address}"]
        for nn,ff in self._fields():
            out.append(f"  {nn}:{getattr(self,nn)}")
        out.append(">")
        return "\n".join(out)


