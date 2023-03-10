# -*- coding:utf-8 -*-
from typing import Any
from abc import ABCMeta, abstractmethod


__all__ = ['FieldProcessor']


class FieldProcessor(metaclass=ABCMeta):
    """Interface for any processor
    """
    zero_value: Any = None
    has_mutable_value = True

    @abstractmethod
    def check_py(self, py_value):
        pass

    @abstractmethod
    def check_raw(self, raw_value):
        pass

    @abstractmethod
    def raw_to_py(self, raw_value, strict):
        pass

    @abstractmethod
    def py_to_raw(self, value):
        pass

    def dump_partial(self, value):
        return self.py_to_raw(value)
