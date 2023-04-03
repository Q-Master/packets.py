# -*- coding:utf-8 -*-
from numbers import Integral
from enum import EnumMeta
from . import FieldProcessor


__all__ = ['BitMask']


def _iterbits(n):
    while n:
        b = n & (~n + 1)
        yield b
        n ^= b

class BitMask(FieldProcessor):
    """Processor for bit masks"""
    @property
    def zero_value(self):
        return 0

    def __init__(self, enum):
        """Constructor

        Args:
            enum (Enum): bits supported. Can be up to 64 elements (64 bit).
        """  
        assert isinstance(enum, EnumMeta), (enum, type(enum))
        assert len(enum) == len(set(enum))
        for element in enum:
            assert isinstance(element.value, Integral)
            assert 0 <= element.value <= 64
        self._powers_to_elements = {
            2**element.value: element
            for element in enum
        }
        self._elements_to_powers = {
            element: 2**element.value
            for element in enum
        }
        self._enum = enum

    def check_py(self, py_value):
        assert isinstance(py_value, set)
        if __debug__:
            for element in py_value:
                assert isinstance(element, self._enum)

    def check_raw(self, raw_value):
        assert isinstance(raw_value, Integral)

    def raw_to_py(self, raw_value: Integral, strict) -> set:
        return set(filter(None, (self._powers_to_elements.get(v) for v in _iterbits(raw_value))))

    def py_to_raw(self, set_of_elements: set) -> int:
        return sum(self._elements_to_powers[element] for element in set_of_elements)

    @property
    def my_type(self):
        return 'set'
