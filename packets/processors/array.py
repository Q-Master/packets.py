# -*- coding:utf-8 -*-
from typing import TypeVar, Optional, List, Iterable, Self, Union, Type
from .base import TypeDef
from .subpacket import Subpacket
from .._packetbase import PacketBase
from .._types import DiffKeys, UpdateData


__all__ = ['Array', 'ArrayT']


_VT=TypeVar('_VT')


class ArrayT(List[_VT]):
    _ro: bool
    __parent__: Optional[PacketBase]
    __modified__: bool
    __local_modified__: bool

    def __init__(self, iterable: Iterable[_VT] = (), size: Optional[int] = None) -> None:
        self._size = size
        self._ro = False
        self.__parent__ = None
        self.__modified__ = False
        self.__local_modified__ = False
        super().__init__(iterable)
    
    def __setitem__(self, index: int, value: _VT):
        if not self._ro:
            super().__setitem__(index, value)
            self.__local_modified__ = True
            self.set_modified()
            if hasattr(value, 'set_modified'):
                value.__parent__ = self # type: ignore
    
    def __delitem__(self, index: int):
        if not self._ro:
            self.__local_modified__ = True
            self.set_modified()
            super().__delitem__(index)
    
    def __len__(self) -> int:
        return super().__len__() or self._size or 0
    
    def append(self, object: _VT) -> None:
        if not self._ro:
            if self._size is None or len(self) < self._size:
                self.set_modified()
                super().append(object)
            else:
                raise IndexError(f'Sized array size overload: {self._size}')
    
    def insert(self, index: int, value: _VT):
        if not self._ro:
            if self._size is None or len(self) < self._size:
                self.set_modified()
                super().insert(index, value)
            else:
                raise IndexError(f'Sized array size overload: {self._size}')

    def set_ro(self, ro: bool):
        self._ro = ro
        for vi in self:
            if isinstance(vi, PacketBase):
                vi.set_ro(ro)

    def is_modified(self) -> bool:
        return self.__modified__

    def is_local_modified(self) -> bool:
        return self.__local_modified__
    
    def set_modified(self):
        self.__modified__ = True
        if self.__parent__:
            self.__parent__.set_modified()

    @property
    def size(self) -> Optional[int]:
        return self._size


class Array(TypeDef[ArrayT[_VT]]):
    def __init__(self, typ: Union[TypeDef[_VT], Type[_VT]], size: Optional[int] = None) -> None:
        super().__init__()
        self.has_modified = True
        if isinstance(typ, TypeDef):
            assert isinstance(typ, TypeDef)
            self._typ = typ
        else:
            self._typ = Subpacket[_VT](typ) # type: ignore
        self._size = size
        
    def check_py(self, v: Union[ArrayT[_VT], list, tuple]) -> bool:
        return isinstance(v, (list, tuple, ArrayT))
    
    def check_raw(self, r: Union[list, tuple]) -> bool:
        return isinstance(r, (list, tuple))
    
    def raw_to_py(self, r, strict = True) -> ArrayT[_VT]:
        return ArrayT[_VT]([self._typ.raw_to_py(ri, strict) for ri in r], self._size)

    def py_to_raw(self, v: ArrayT[_VT]) -> list:
        return list(map(self._typ.py_to_raw, v))

    def py_to_py(self, v: Optional[ArrayT[_VT]]) -> Optional[ArrayT[_VT]]:
        return None if v is None else ArrayT[_VT](v, self._size) if not isinstance(v, ArrayT) else v
    
    def zero_value(self) -> ArrayT[_VT]:
        if self._size:
            data = ArrayT[_VT]([self._typ.zero_value() for _ in range(self._size)], size=self._size)
        else:
            data = ArrayT[_VT]()
        return data

    def set_ro(self, ro: bool):
        super().set_ro(ro)
        self._typ.set_ro(ro)

    def self_type(self):
        typ = self._typ.self_type()
        return ArrayT[typ]

    def clone(self) -> Self:
        c = self.__class__(self._typ.clone(), self._size)
        c.set_ro(False)
        return c

    @property
    def size(self) -> Optional[int]:
        return self._size

    def diff_keys(self, v: ArrayT[_VT]) -> Optional[Union[str, DiffKeys]]:
        if v.is_modified():
            if v.is_local_modified():
                return '1'
            elif not self._typ.has_modified:
                return '1'
            else:
                res = {}
                for i, val in enumerate(v):
                    dv = self._typ.diff_keys(val)
                    if dv is None:
                        continue
                    res[str(i)] = dv
                return res if res else None
        return None

    def dump_partial(self, field_paths: DiffKeys, v: ArrayT[_VT]) -> list:
        return self.py_to_raw(v)

    def update_partial(self, instance: ArrayT[_VT], update_data: UpdateData):
        for rk, rv in update_data.items():
            k = int(rk)
            if k == len(instance):
                # means adding the next element:
                val = instance.append(self._typ.zero_value())
            else:
                val = instance[k]
            if isinstance(rv, UpdateData):
                if isinstance(val, PacketBase):
                    val.update_partial(rv)
                else:
                    self._typ.update_partial(val, rv) # type: ignore
            else:
                if rv is None:
                    # means deleting the k'th element
                    instance.pop(k)
                else:
                    instance[k] = self._typ.raw_to_py(rv)
