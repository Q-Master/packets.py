# -*- coding:utf-8 -*-
from typing import TypeVar, Optional, Set as TSet, Self, Union, Type
from .base import TypeDef
from .subpacket import Subpacket
from .._packetbase import PacketBase
from .._types import DiffKeys, UpdateData


__all__ = ['SetT', 'Set']


_VT=TypeVar('_VT')


class SetT(TSet[_VT]):
    _ro: bool
    __parent__: Optional[PacketBase]
    __modified__: bool

    def __init__(self, *args, **kwargs) -> None:
        self._ro = False
        self.__parent__ = None
        self.__modified__ = False
        super().__init__(*args, **kwargs)
        for v in self:
            self.update_parent(v)

    def add(self, value: _VT):
        if not self._ro:
            super().add(value)
            self.set_modified()
            if hasattr(value, 'set_modified'):
                value.__parent__ = self # type: ignore

    def discard(self, value: _VT):
        if not self._ro:
            super().discard(value)
            self.set_modified()

    def remove(self, value: _VT):
        if not self._ro:
            super().remove(value)
            self.set_modified()

    def set_ro(self, ro: bool):
        self._ro = ro
        for vi in self:
            if isinstance(vi, PacketBase):
                vi.set_ro(ro)
    
    def is_modified(self) -> bool:
        return self.__modified__
    
    def set_modified(self):
        self.__modified__ = True
        if self.__parent__:
            self.__parent__.set_modified()

    def update_parent(self, value: _VT):
        if hasattr(value, 'set_modified'):
            value.__parent__ = self # type: ignore


class Set(TypeDef[SetT[_VT]]):
    def __init__(self, typ: Union[TypeDef[_VT], Type[_VT]]) -> None:
        super().__init__()
        self.has_modified = True
        if isinstance(typ, TypeDef):
            assert isinstance(typ, TypeDef)
            self._typ = typ
        else:
            self._typ = Subpacket[_VT](typ) # type: ignore
        
    def check_py(self, v: SetT[_VT]) -> bool:
        return isinstance(v, (set, SetT))
    
    def check_raw(self, r) -> bool:
        return isinstance(r, set)
    
    def raw_to_py(self, r, strict = True) -> SetT[_VT]:
        return SetT[_VT]([self._typ.raw_to_py(ri, strict) for ri in r])

    def py_to_raw(self, v: SetT[_VT]) -> set:
        return set(map(self._typ.py_to_raw, v))

    def py_to_py(self, v: Optional[SetT[_VT]]) -> Optional[SetT[_VT]]:
        return None if v is None else SetT[_VT](v) if not isinstance(v, SetT) else v

    def zero_value(self) -> SetT[_VT]:
        return SetT[_VT](set())

    def set_ro(self, ro: bool):
        super().set_ro(ro)
        self._typ.set_ro(ro)

    def self_type(self):
        typ = self._typ.self_type()
        return TSet[typ]

    def clone(self) -> Self:
        c = self.__class__(self._typ.clone())
        c.set_ro(False)
        return c

    def diff_keys(self, v: SetT[_VT]):
        return '1' if v.is_modified() else None

    def dump_partial(self, field_paths: DiffKeys, v: SetT[_VT]) -> set:
        return self.py_to_raw(v)

    def update_partial(self, instance: SetT[_VT], update_data: UpdateData):
        # almost unusable
        for rk, rv in update_data.items():
            val = self._typ.raw_to_py(rk) # type: ignore
            if val not in instance:
                instance.add(val)
            if isinstance(rv, UpdateData):
                if isinstance(val, PacketBase):
                    val.update_partial(rv)
                else:
                    self._typ.update_partial(val, rv) # type: ignore
            else:
                instance.remove(val)
                if rv is not None:
                    # means updating the element val, not just deleting
                    instance.add(self._typ.raw_to_py(rv))
