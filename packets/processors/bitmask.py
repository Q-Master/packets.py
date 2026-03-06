# -*- coding:utf-8 -*-
from typing import TypeVar, Type, Set, Self
from enum import Enum
from .base import TypeDef


__all__ = ['Bitmask']


T = TypeVar('T', bound=Enum)


def _iterbits(n):
    while n:
        b = n & (~n + 1)
        yield b
        n ^= b


class Bitmask(TypeDef[T]):
    def __init__(self, enum: Type[T]) -> None:
        """Constructor

        Args:
            enum (Enum): bits supported. Can be up to 64 elements (64 bit).
        """
        super().__init__()
        self._powers_to_enum = {}
        self._enum_to_powers = {}
        for element in enum:
            assert isinstance(element.value, int)
            assert element.value >= 0 and element.value <= 64
            self._powers_to_enum[2**element.value] = element
            self._enum_to_powers[element] = 2**element.value
        self._typ = enum
    
    def check_py(self, v: Set[T]) -> bool:
        return isinstance(v, set)
    
    def check_raw(self, r: int) -> bool:
        return isinstance(r, int)
    
    def raw_to_py(self, raw_value: int, strict) -> Set[T]:
        return set(filter(None, (self._powers_to_enum.get(v) for v in _iterbits(int(raw_value)))))
    
    def py_to_raw(self, v: Set[T]) -> int:
        return sum(self._enum_to_powers[element] for element in v)
        
    def zero_value(self) -> Set[T]:
        return set()
    
    def self_type(self) -> type[Set[T]]:
        return Set[T]

    def clone(self) -> Self:
        c = self.__class__(self._typ)
        c.set_ro(False)
        return c
