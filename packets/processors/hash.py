# -*- coding:utf-8 -*-
from typing import TypeVar, Dict, Generic, Self, Optional, Set, Union, Type
from enum import Enum
from .base import TypeDef
from .subpacket import Subpacket
from .._packetbase import PacketBase
from .._types import DiffKeys


__all__ = ['HashT', 'Hash']


_K = TypeVar('_K', bound=Union[int, float, str, Enum])
_V = TypeVar('_V')


class HashT(Dict[_K, _V]):
    _ro = False
    __parent__: Optional[PacketBase] = None
    __modified__: bool = False
    __diff__: Set[_K] = set()

    def __setitem__(self, key: _K, value: _V):
        if not self._ro:
            super().__setitem__(key, value)
            self.set_modified()
            self.__diff__.add(key)

    def __delitem__(self, key):
        if not self._ro:
            super().__delitem__(key)
            self.set_modified()
            self.__diff__.add(key)

    def set_ro(self, ro: bool):
        self._ro = ro
        for ki, vi in self.items():
            if isinstance(ki, PacketBase):
                ki.set_ro(ro)
            if isinstance(vi, PacketBase):
                vi.set_ro(ro)

    def is_modified(self) -> bool:
        return self.__modified__
    
    def set_modified(self):
        self.__modified__ = True
        if self.__parent__:
            self.__parent__.set_modified()


class Hash(TypeDef[HashT[_K, _V]]):
    def __init__(self, ktyp: TypeDef[_K], vtyp: Union[TypeDef[_V], Type[_V]]) -> None:
        super().__init__()
        self.has_modified = True
        self._ktyp = ktyp
        if isinstance(vtyp, TypeDef):
            assert isinstance(vtyp, TypeDef)
            self._vtyp = vtyp
        else:
            self._vtyp = Subpacket[_V](vtyp) # type: ignore

    def check_py(self, v: HashT[_K, _V]) -> bool:
        return isinstance(v, (dict, HashT))
    
    def check_raw(self, r: dict) -> bool:
        return isinstance(r, dict)
    
    def raw_to_py(self, r: dict, strict = True) -> HashT[_K, _V]:
        d = HashT[_K, _V]({self._ktyp.raw_to_py(ki, strict): self._vtyp.raw_to_py(ri, strict) for ki, ri in r.items()})
        d.__diff__ = set()
        d.__modified__ = False
        return d

    def py_to_raw(self, v: HashT[_K, _V]) -> dict:
        return dict({self._ktyp.py_to_raw(ki): self._vtyp.py_to_raw(vi) for ki, vi in v.items()})

    def py_to_py(self, v: Optional[HashT[_K, _V]]) -> Optional[HashT[_K, _V]]:
        return None if v is None else HashT[_K, _V](v) if not isinstance(v, HashT) else v
        
    def zero_value(self) -> HashT[_K, _V]:
        return HashT[_K, _V]()

    def set_ro(self, ro: bool):
        super().set_ro(ro)
        self._ktyp.set_ro(ro)
        self._vtyp.set_ro(ro)

    def self_type(self):
        return HashT[_K, _V]

    def clone(self) -> Self:
        c = self.__class__(self._ktyp.clone(), self._vtyp.clone())
        c.set_ro(False)
        return c

    def diff_keys(self, data: HashT[_K, _V]) -> DiffKeys:
        res = {}
        for k in data.__diff__:
            res[k] = self._vtyp.diff_keys(data[k])
        return res
