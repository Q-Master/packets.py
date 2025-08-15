# -*- coding:utf-8 -*-
from typing import TypeVar, Generic
from .._fieldprocessorbase import FieldProcessor


__all__ = ['Const']


T = TypeVar('T')


class Const(Generic[T], FieldProcessor):
    """Processor for immutable values"""
    has_mutable_value = False
    has_flat_value = True

    def __init__(self, value: T):
        self._value = value
        self.zero_value = value

    def check_py(self, py_value):
        pass

    def check_raw(self, raw_value):
        pass

    def raw_to_py(self, raw_value, strict) -> T:
        return self._value

    def py_to_raw(self, py_value) -> T:
        return self._value

    @property
    def my_type(self):
        return type(self._value)
