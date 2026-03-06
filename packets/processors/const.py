# -*- coding:utf-8 -*-
from typing import Self, Type
from .base import TypeDef, T


__all__ = ['Const']


class Const(TypeDef[T]):
    def __new__(cls, typ: Type[TypeDef[T]]) -> TypeDef[T]:
        inst = super.__new__(typ)
        inst.set_ro(True)
        return inst
    
    def check_py(self, v) -> bool:
        assert False, ('Constants not checkable')
        return True
    
    def check_raw(self, r) -> bool:
        assert False, ('Constants not checkable')
        return True
    
    def raw_to_py(self, r, strict=True):
        assert False, ('Constants not checkable')
        return None

    def py_to_raw(self, v):
        assert False, ('Constants not checkable')
        return None

    def zero_value(self):
        assert False, ('Constants not checkable')
        return None

    def is_const(self) -> bool: 
        return True

    def clone(self):
        assert False, ('Constants not checkable')
        return None
