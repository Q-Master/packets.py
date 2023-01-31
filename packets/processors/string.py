# -*- coding:utf-8 -*-
from ._base import FieldProcessor
from ._types import StringTypes


__all__ = ['String', 'string_t']


class String(FieldProcessor):
    """Processor for strings"""
    has_mutable_value = False
    zero_value = ''

    def __init__(self, max_length=None, trim=False):
        """Constructor

        Args:
            max_length (int, optional): maximum length of the string. Defaults to None.
            trim (bool, optional): if the string should be trimmed to fit `max_length`. Defaults to False.
        """        
        self._max_length = max_length
        self._trim = trim
        assert not (trim and max_length is None)

    def check_py(self, value):
        assert isinstance(value, StringTypes), (value, type(value))
        if not self._trim and (self._max_length is not None) and len(value) > self._max_length:
            raise ValueError(f'String is too long {len(value)} (max {self._max_length})')

    check_raw = check_py

    def raw_to_py(self, raw_value: str, strict: bool) -> str:
        if self._trim:
            return raw_value[:self._max_length]
        else:
            return raw_value

    def py_to_raw(self, py_value: str) -> str:
        if self._trim:
            return py_value[:self._max_length]
        else:
            return py_value


string_t = String()
