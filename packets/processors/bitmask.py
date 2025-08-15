# -*- coding:utf-8 -*-
from typing import TypeVar, Set, Generic, Type
from numbers import Integral
from enum import Enum
from .._fieldprocessorbase import FieldProcessor


__all__ = ['BitMask']


T = TypeVar('T', bound=Enum)


def _iterbits(n):
    while n:
        b = n & (~n + 1)
        yield b
        n ^= b


class BitMask(Generic[T], FieldProcessor):
    """Processor for bit masks"""
    @property
    def zero_value(self):
        return 0

    def __init__(self, enum: Type[T]):
        """Constructor

        Args:
            enum (Enum): bits supported. Can be up to 64 elements (64 bit).
        """  
        assert issubclass(enum, Enum), (enum, type(enum))
        assert len(enum) == len(set(enum))
        for element in enum:
            assert isinstance(element.value, Integral)
            assert int(element.value) >= 0 and int(element.value) <= 64
        self._powers_to_elements = {
            2**int(element.value): element
            for element in enum
        }
        self._elements_to_powers = {
            element: 2**int(element.value)
            for element in enum
        }
        self._enum = enum

    def check_py(self, py_value: Set[T]):
        assert isinstance(py_value, set)

    def check_raw(self, raw_value: int):
        assert isinstance(raw_value, int)

    def raw_to_py(self, raw_value: int, strict) -> Set[T]:
        return set(filter(None, (self._powers_to_elements.get(v) for v in _iterbits(int(raw_value)))))

    def py_to_raw(self, set_of_elements: set) -> int:
        return sum(self._elements_to_powers[element] for element in set_of_elements)

    @property
    def my_type(self):
        return Set[T]
