# -*- coding:utf-8 -*-
from .._fieldprocessorbase import FieldProcessor


__all__ = ['Bytes', 'bytes_t']


class Bytes(FieldProcessor):
    """Processor for bytes type"""
    has_mutable_value = False
    zero_value = b''

    def __init__(self, strip=None):
        self._strip = strip

    def check_py(self, value):
        assert isinstance(value, bytes), (value, type(value))

    def check_raw(self, value):
        assert isinstance(value, bytes), (value, type(value))

    def raw_to_py(self, raw_value: bytes, strict) -> bytes:
        value = raw_value
        if self._strip is not None:
            value = value.strip(self._strip)
        return value

    def py_to_raw(self, py_value: bytes) -> bytes:
        return py_value

    @property
    def my_type(self):
        return bytes


bytes_t = Bytes()
