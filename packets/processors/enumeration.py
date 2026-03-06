# -*- coding:utf-8 -*-
from typing import TypeVar, Type, Self
from enum import Enum
from .base import TypeDef


__all__ = ['Enumeration', 'EnumerationByName']


T = TypeVar('T', bound=Enum)


class Enumeration(TypeDef[T]):
    """Enum processor. Stores **value** of enum in serialization"""

    def __init__(self, typ: Type[T]) -> None:
        super().__init__()
        self._typ = typ

    def check_py(self, v: T) -> bool:
        return isinstance(v, Enum)

    def check_raw(self, r) -> bool:
        return True

    def raw_to_py(self, r, strict=True) -> T:
        return self._typ(r)

    def py_to_raw(self, v: T):
        return v.value
    
    def self_type(self) -> Type[T]:
        return self._typ

    def zero_value(self) -> T:
        return self._typ()
    
    def clone(self) -> Self:
        c = self.__class__(self._typ)
        c.set_ro(False)
        return c



class EnumerationByName(Enumeration[T]):
    """Enum processor. Stores **name** of enum in serialization"""

    def check_raw(self, r: str) -> bool:
        return isinstance(r, str)

    def raw_to_py(self, r: str, strict=True) -> T:
        return self._typ[r]

    def py_to_raw(self, v: T) -> str:
        return v.name
