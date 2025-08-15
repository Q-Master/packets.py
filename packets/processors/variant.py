# -*- coding:utf-8 -*-
from typing import Any
from .._fieldprocessorbase import FieldProcessor


__all__ = ['Variant', 'any_t']


class Variant(FieldProcessor):
    """Processor for any(unknown) type"""
    @property
    def zero_value(self):
        return {}

    def check_py(self, py_value):
        pass

    def check_raw(self, raw_value):
        pass

    def raw_to_py(self, raw_value, strict):
        return raw_value

    def py_to_raw(self, value):
        return value

    @property
    def my_type(self):
        return Any


any_t = Variant()
