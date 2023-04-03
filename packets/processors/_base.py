# -*- coding:utf-8 -*-
from typing import Any
from abc import ABCMeta, abstractmethod, abstractproperty


__all__ = ['FieldProcessor']


class FieldProcessor(metaclass=ABCMeta):
    """Interface for any processor
    """
    zero_value: Any = None
    has_mutable_value = True

    @abstractproperty
    def my_type(cls) -> str:
        pass

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
