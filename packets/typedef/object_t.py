# -*- coding:utf-8 -*-
from typing import Type, Optional, Dict
from ..processors.base import TypeDef
from .._packetbase import PacketBase
from .._types import DiffKeys, UpdateData



class ObjectT(Dict):
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


class Object(TypeDef[Dict]):
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

    def diff_keys(self, v: ObjectT) -> DiffKeys:
        res = {}
        for k in v.__diff__:
            val = v.get(k)
            if isinstance(val, ObjectT):
                res[k] = self.diff_keys(val)
            else:
                res[k] = super().diff_keys({})
        return res

    def dump_partial(self, field_paths: DiffKeys, v: ObjectT) -> dict:
        result = {}
        if len(v):
            for key, subpaths in field_paths.items():
                if key in v.keys():
                    val = v[key]
                    if isinstance(subpaths, str):
                        raw_value = self.py_to_raw(val)
                        if raw_value is not None:
                            result[key] = raw_value
                    else:
                        if isinstance(val, PacketBase):
                            result[key] = val.dump_partial(subpaths)
                        elif isinstance(val, (dict, ObjectT)):
                            result[key] = self.dump_partial(subpaths, val) # type: ignore
                        else:
                            result[key] = self.py_to_raw(val)
        return result

    def update_partial(self, instance: ObjectT, update_data: UpdateData):
        for rk, rv in update_data.items():
            k = rk
            if isinstance(rv, UpdateData):
                val = instance.setdefault(k, self.zero_value())
                if isinstance(val, PacketBase):
                    val.update_partial(rv)
                else:
                    self.update_partial(val, rv)
            else:
                if rv is None:
                    del instance[k]
                else:
                    instance[k] = rv


object_t = Object()
