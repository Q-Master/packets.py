# -*- coding:utf-8 -*-
from collections.abc import Mapping
from . import FieldProcessor


__all__ = ['Object', 'object_t']


class Object(FieldProcessor):
    """Simple python object processor"""
    @property
    def zero_value(self):
        return {}

    def check_py(self, py_value):
        assert isinstance(py_value, Mapping)

    def check_raw(self, raw_value):
        assert isinstance(raw_value, Mapping)

    def raw_to_py(self, raw_value, strict):
        return raw_value

    def py_to_raw(self, value):
        return value

    @property
    def my_type(self):
        return 'dict'


object_t = Object()