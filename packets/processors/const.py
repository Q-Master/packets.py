# -*- coding:utf-8 -*-
from ._base import FieldProcessor


__all__ = ['Const']


class Const(FieldProcessor):
    """Processor for immutable values"""
    has_mutable_value = False
    has_flat_value = True

    def __init__(self, value):
        self._value = value
        self.zero_value = value

    def check_py(self, py_value):
        pass

    def check_raw(self, raw_value):
        pass

    def raw_to_py(self, raw_value, strict):
        return self._value

    def py_to_raw(self, py_value):
        return self._value
