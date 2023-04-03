# -*- coding:utf-8 -*-
from enum import EnumMeta
from ._base import FieldProcessor
from ._types import StringTypes


__all__ = ['Enumeration', 'EnumerationByName']


class Enumeration(FieldProcessor):
    """Enum processor. Stores **value** of enum in serialization"""
    def __init__(self, enum):
        assert isinstance(enum, EnumMeta)
        self._enum = enum

    def check_py(self, py_value):
        assert isinstance(py_value, self._enum)

    def check_raw(self, raw_value):
        pass

    def raw_to_py(self, raw_value, strict):
        return self._enum(raw_value)

    def py_to_raw(self, enum_element):
        return enum_element.value

    @property
    def my_type(self):
        return 'Enum'


class EnumerationByName(FieldProcessor):
    """Enum processor. Stores **name** of enum in serialization"""
    def __init__(self, enum):
        assert isinstance(enum, EnumMeta)
        self._enum = enum

    def check_py(self, py_value):
        assert isinstance(py_value, self._enum)

    def check_raw(self, raw_value):
        assert isinstance(raw_value, StringTypes)

    def raw_to_py(self, raw_value, strict):
        return self._enum[raw_value]

    def py_to_raw(self, enum_element):
        return enum_element.name

    @property
    def my_type(self):
        return 'Enum'
