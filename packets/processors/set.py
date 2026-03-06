# -*- coding:utf-8 -*-
from typing import TypeVar, Optional, Set as TSet, Self
from .base import TypeDef
from .._packetbase import PacketBase


__all__ = ['SetT', 'Set']


_VT=TypeVar('_VT')


class SetT(TSet[_VT]):
    _ro = False
    __parent__: Optional[PacketBase] = None
    __modified__: bool = False

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


class Set(TypeDef[SetT[_VT]]):
    def __init__(self, typ: TypeDef[_VT]) -> None:
        super().__init__()
        self._typ = typ
    
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
