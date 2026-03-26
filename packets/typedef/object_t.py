# -*- coding:utf-8 -*-
from typing import Type, Optional
from ..processors.base import TypeDef
from .._packetbase import PacketBase
from .._types import DiffKeys


class ObjectT(dict):
    _ro = False
    __parent__: Optional[PacketBase] = None
    __modified__: bool = False
    __diff__ = set()

    def __setitem__(self, key, value):
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


class Object(TypeDef[dict]):
    """Simple python object processor"""
    def __init__(self) -> None:
        super().__init__()
        self.has_modified = True
    
    def check_py(self, v: dict) -> bool:
        return isinstance(v, dict)    

    def check_raw(self, r: dict) -> bool:
        return isinstance(r, dict)

    def raw_to_py(self, r, strict=True) -> ObjectT:
        d = ObjectT(r)
        d.__diff__ = set()
        d.__modified__ = False
        return d
    
    def py_to_raw(self, v: ObjectT) -> dict:
        return v
    
    def py_to_py(self, v: dict) -> Optional[ObjectT]:
        return None if v is None else ObjectT(v) if not isinstance(v, ObjectT) else v

    def zero_value(self) -> dict:
        return {}

    def self_type(self) -> Type[ObjectT]:
        return ObjectT

    def diff_keys(self, data: ObjectT) -> DiffKeys:
        res = {}
        for k in data.__diff__:
            v = data.get(k)
            if isinstance(v, ObjectT):
                res[k] = self.diff_keys(v)
            else:
                res[k] = super().diff_keys({})
        return res


object_t = Object()
