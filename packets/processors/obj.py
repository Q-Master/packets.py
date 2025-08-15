# -*- coding:utf-8 -*-
from typing import Type, Any
from collections.abc import Mapping, MutableMapping
from .._fieldprocessorbase import FieldProcessor


__all__ = ['Object', 'object_t']


class Object(FieldProcessor):
    """Simple python object processor"""
    @property
    def zero_value(self):
        return {}

    def check_py(self, py_value: Mapping | MutableMapping):
        assert isinstance(py_value, (Mapping, MutableMapping))

    def check_raw(self, raw_value: Mapping | MutableMapping):
        assert isinstance(raw_value, (Mapping, MutableMapping))

    def raw_to_py(self, raw_value: Mapping | MutableMapping, strict):
        return raw_value

    def py_to_raw(self, value: Mapping | MutableMapping):
        return value

    @property
    def my_type(self) -> Type[Mapping[Any, Any]]:
        return Mapping[Any, Any]


object_t = Object()