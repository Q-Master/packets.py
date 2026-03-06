# -*- coding:utf-8 -*-
from typing import TypeAlias
from ..processors.base import TypeDef


class Bool(TypeDef[bool]):
    def check_py(self, v: bool) -> bool:
        return isinstance(v, (bool))
    
    def check_raw(self, r) -> bool:
        return isinstance(r, (bool, int, float, str))
    
    def raw_to_py(self, r, strict=True) -> bool:
        if isinstance(r, bool):
            return r
        elif isinstance(r, str):
            return r[0].upper() == 'T'
        else:
            return int(r) > 0

    def py_to_raw(self, v: bool) -> bool:
        return v

    def zero_value(self) -> bool:
        return False

    def self_type(self) -> type[bool]:
        return bool


bool_t = Bool()
BoolT: TypeAlias = bool
